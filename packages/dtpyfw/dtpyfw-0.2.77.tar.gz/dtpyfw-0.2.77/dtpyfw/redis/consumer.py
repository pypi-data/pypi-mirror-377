import json
import time
from typing import Callable, Dict, List, Optional

from ..core.exception import exception_to_dict
from ..core.retry import retry_wrapper
from ..log import footprint
from .connection import RedisInstance

__all__ = ("Consumer",)


class Consumer:
    def __init__(self, redis_instance: RedisInstance, consumer_name: str):
        self.consumer_name: str = consumer_name
        self._handlers: Dict[str, List] = {}
        self._channels = []
        self._redis_instance = redis_instance
        self._redis_client = self._redis_instance.get_redis_client()

    def _server_now_ms(self) -> int:
        """Server time in ms to avoid client clock skew."""
        sec, usec = self._redis_client.time()
        return sec * 1000 + (usec // 1000)

    def _consumer_group_exists(self, channel_name: str, consumer_group: str) -> bool:
        try:
            groups = self._redis_client.xinfo_groups(channel_name)
            return any(group["name"].decode("utf-8") == consumer_group for group in groups)
        except Exception:
            return False

    @staticmethod
    def _processed_set_key(channel: str, group: str) -> str:
        # Tracks processed message IDs to guarantee at-most-once processing by ID
        return f"stream:{channel}:group:{group}:processed"

    @staticmethod
    def _dlq_stream(channel: str) -> str:
        # Dead-letter stream per channel
        return f"{channel}:dlq"

    def register_channel(
        self,
        channel_name: str,
        read_messages: bool = False,
        retention_ms: Optional[int] = None,  # time-based retention window
    ):
        """Registers a channel, optionally starting message consumption automatically."""
        controller = f"{__name__}.Consumer.register_channel"

        consumer_group = f"{channel_name}_consumer_group"
        if not self._consumer_group_exists(channel_name, consumer_group):
            try:
                # Start at "$" so we only consume new messages created after the group.
                # If you need historical catch-up, run XGROUP SETID <stream> <group> 0-0 once, outside.
                self._redis_client.xgroup_create(channel_name, consumer_group, "$", mkstream=True)
            except Exception as e:
                footprint.leave(
                    log_type="error",
                    subject="Error creating consumer group",
                    message=f"Error creating consumer group {consumer_group} for channel {channel_name}.",
                    controller=controller,
                    payload=exception_to_dict(e),
                )

        self._channels.append((channel_name, consumer_group, read_messages, retention_ms))
        self._handlers[channel_name] = []
        return self

    def register_handler(self, channel_name: str, handler_func: Callable):
        self._handlers[channel_name].append(handler_func)
        return self

    @retry_wrapper()
    def consume_messages(self, channel: str, consumer_group: str, block_time: float, count: int = 16):
        """
        Reads and processes messages for a specific consumer group in a channel.

        Guarantees: each message ID is processed at most once (per group) by using a Redis SET
        as a dedup ledger. Messages are always XACKed (or dead-lettered + XACKed) so they
        don't linger in the group PEL and get redelivered later.
        """
        controller = f"{__name__}.Consumer.consume_messages"
        processed_key = self._processed_set_key(channel, consumer_group)

        try:
            # Note: '>' means only messages never-delivered to this group.
            # If Redis later re-delivers due to crashes/claims, the dedup set protects us.
            messages = self._redis_client.xreadgroup(
                consumer_group,
                self.consumer_name,
                {channel: ">"},
                block=int(block_time * 1000),
                count=count,
            )

            if not messages:
                return

            stream_name, message_batch = messages[0]
            for message_id, message_content in message_batch:
                # Dedup first: if we've processed this ID before, just ack and skip.
                try:
                    was_added = self._redis_client.sadd(processed_key, message_id)
                    if was_added == 0:
                        # Already processed earlier; ack and move on.
                        self._redis_client.xack(channel, consumer_group, message_id)
                        continue
                except Exception as e:
                    # If dedup check itself fails, be defensive: do not process to avoid dup effects.
                    footprint.leave(
                        log_type="warning",
                        message="Dedup SET operation failed; skipping message to avoid duplicate processing",
                        controller=controller,
                        subject="Dedup error",
                        payload={"error": exception_to_dict(e), "message_id": message_id},
                    )
                    # Do not ack: better to let it retry later than risk double-processing.

                    continue

                # Safe decode + schema guard
                try:
                    raw_name = message_content.get(b"name")
                    raw_body = message_content.get(b"body")
                    if raw_name is None or raw_body is None:
                        footprint.leave(
                            log_type="error",
                            message="Missing required fields 'name' or 'body'.",
                            controller=controller,
                            subject="DLQ write error",
                            payload={"raw_name": raw_name, "raw_body": raw_body},
                        )
                        continue

                    name = raw_name.decode("utf-8") if isinstance(raw_name, bytes) else raw_name
                    body = json.loads(raw_body.decode("utf-8")) if isinstance(raw_body, bytes) else raw_body

                except Exception as e:
                    # Dead-letter the bad payload and ACK so it will not be re-read.
                    try:
                        self._redis_client.xadd(
                            self._dlq_stream(channel),
                            {
                                "reason": "decode/schema",
                                "error": json.dumps(exception_to_dict(e)),
                                "message_id": message_id,
                                "raw": json.dumps(
                                    {k.decode() if isinstance(k, bytes) else k: (v.decode() if isinstance(v, bytes) else v)
                                     for k, v in (message_content or {}).items()},
                                    default=str,
                                ),
                            },
                        )
                    except Exception as dlq_err:
                        footprint.leave(
                            log_type="error",
                            message="Failed to write to DLQ",
                            controller=controller,
                            subject="DLQ write error",
                            payload={"error": exception_to_dict(dlq_err), "message_id": message_id},
                        )
                    finally:
                        # Ack to prevent any re-delivery
                        self._redis_client.xack(channel, consumer_group, message_id)
                    continue

                # Execute handlers
                for handler in self._handlers.get(channel, []):
                    try:
                        handler(name=name, payload=body)
                    except Exception as e:
                        # Handler failure: dead-letter and ack to avoid re-processing.
                        try:
                            self._redis_client.xadd(
                                self._dlq_stream(channel),
                                {
                                    "reason": "handler",
                                    "handler": handler.__name__,
                                    "error": json.dumps(exception_to_dict(e)),
                                    "message_id": message_id,
                                    "name": name,
                                    "payload": json.dumps(body, default=str),
                                },
                            )
                        except Exception as dlq_err:
                            footprint.leave(
                                log_type="error",
                                message="Failed to write handler error to DLQ",
                                controller=controller,
                                subject="DLQ write error",
                                payload={"error": exception_to_dict(dlq_err), "message_id": message_id},
                            )
                        finally:
                            self._redis_client.xack(channel, consumer_group, message_id)
                        break  # stop other handlers for this message
                else:
                    # All handlers succeeded; ACK once.
                    self._redis_client.xack(channel, consumer_group, message_id)

        except Exception as e:
            footprint.leave(
                log_type="error",
                message=f"Error consuming messages from channel {channel}",
                controller=controller,
                subject="Consuming Messages Error",
                payload={"error": exception_to_dict(e)},
            )

    def persist_consume_messages(self, channel: str, consumer_group: str, rest_time: float, block_time: float, count: int = 16):
        while True:
            self.consume_messages(channel=channel, consumer_group=consumer_group, block_time=block_time, count=count)
            if rest_time > 0:
                time.sleep(rest_time)

    def consume_all_channels(self, block_time: float, count: int = 16):
        for channel_name, consumer_group, read_messages, _ in self._channels:
            if read_messages:
                self.consume_messages(channel=channel_name, consumer_group=consumer_group, block_time=block_time, count=count)

    def persist_consume_all_channels(self, rest_time: float, block_time: float, count: int = 16):
        controller = f"{__name__}.Consumer.persist_consume_all_channels"
        for channel_name, consumer_group, read_messages, _ in self._channels:
            footprint.leave(
                log_type="info",
                message="Channel consumption configuration",
                controller=controller,
                subject="Persist consuming channels",
                payload={
                    "channel": channel_name,
                    "consumer_group": consumer_group,
                    "will_read_messages": bool(read_messages),
                },
            )

        while True:
            self.consume_all_channels(block_time=block_time, count=count)
            if rest_time > 0:
                time.sleep(rest_time)

    @retry_wrapper()
    def clean_up_consumed_messages(self):
        """
        Deletes messages from streams based on a time retention window.
        Note: XTRIM MINID will remove entries regardless of PEL status. Use a generous retention window.
        """
        controller = f"{__name__}.Consumer.clean_up_consumed_messages"
        for channel_name, consumer_group, _, retention_ms in self._channels:
            try:
                if retention_ms and retention_ms > 0:
                    now_ms = self._server_now_ms()
                    cutoff = now_ms - retention_ms
                    removed = self._redis_client.xtrim(channel_name, minid=f"{cutoff}-0", approximate=True)
                    if removed:
                        footprint.leave(
                            log_type="info",
                            message=f"Trimmed {removed} entries older than {retention_ms}ms in {channel_name}.",
                            controller=controller,
                            subject="Time-based stream trimming",
                            payload={"cutoff_ms": cutoff, "retention_ms": retention_ms},
                        )
            except Exception as e:
                footprint.leave(
                    log_type="error",
                    message=f"Error cleaning up messages in channel {channel_name}",
                    controller=controller,
                    subject="Cleaning up messages Error",
                    payload={"error": exception_to_dict(e)},
                )
