import json
import time
from typing import Callable, Dict, List

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
            return any(
                group["name"].decode("utf-8") == consumer_group for group in groups
            )
        except:
            return False

    def register_channel(
        self,
        channel_name: str,
        read_messages: bool = False,
        retention_ms: int | None = None, # NEW: time-based retention window
    ):
        """Registers a channel , optionally starting message consumption automatically."""
        controller = f"{__name__}.Consumer.register_channel"

        consumer_group = f"{channel_name}_consumer_group"
        if not self._consumer_group_exists(channel_name, consumer_group):
            try:
                self._redis_client.xgroup_create(
                    channel_name, consumer_group, "$", mkstream=True
                )
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

    def register_handler(
        self,
        channel_name: str,
        handler_func: Callable,
    ):
        self._handlers[channel_name].append(handler_func)
        return self

    @retry_wrapper()
    def consume_messages(self, channel: str, consumer_group: str, block_time: float):
        """Reads and processes messages for a specific consumer group in a
        channel."""
        controller = f"{__name__}.Consumer.consume_messages"
        try:
            messages = self._redis_client.xreadgroup(
                consumer_group,
                self.consumer_name,
                {channel: ">"},
                block=int(block_time * 1000),
                count=1,
            )

            for message in messages:
                stream_name, message_data = message
                message_id, message_content = message_data[0]

                name = message_content.get(b"name")
                body = message_content.get(b"body")

                if name and body:
                    name = name.decode("utf-8") if isinstance(name, bytes) else name
                    body = (
                        json.loads(body.decode("utf-8"))
                        if isinstance(body, bytes)
                        else body
                    )

                    for handler in self._handlers.get(channel, []):
                        try:
                            handler(name=name, payload=body)
                        except Exception as e:
                            footprint.leave(
                                log_type="error",
                                message="We faced an error while we want to read a message",
                                controller=controller,
                                subject="Consuming Message Error",
                                payload={
                                    "error": exception_to_dict(e),
                                    "handler": handler.__name__,
                                    "name": name,
                                    "body": body,
                                },
                            )

                    self._redis_client.xack(channel, consumer_group, message_id)

        except Exception as e:
            footprint.leave(
                log_type="error",
                message=f"Error consuming messages from channel {channel}",
                controller=controller,
                subject="Consuming Messages Error",
                payload={
                    "error": exception_to_dict(e),
                },
            )

    def persist_consume_messages(
        self, channel: str, consumer_group: str, rest_time: float, block_time: float
    ):
        while True:
            self.consume_messages(
                channel=channel, consumer_group=consumer_group, block_time=block_time
            )
            if rest_time > 0:
                time.sleep(rest_time)

    def consume_all_channels(self, block_time: float):
        for channel_name, consumer_group, read_messages, _ in self._channels:
            if read_messages:
                self.consume_messages(
                    channel=channel_name,
                    consumer_group=consumer_group,
                    block_time=block_time,
                )

    def persist_consume_all_channels(self, rest_time: float, block_time: float):
        while True:
            self.consume_all_channels(block_time=block_time)
            if rest_time > 0:
                time.sleep(rest_time)

    @retry_wrapper()
    def clean_up_consumed_messages(self):
        """Deletes messages from streams that have been fully processed by all
        consumers in a group."""
        controller = f"{__name__}.Consumer.clean_up_consumed_messages"
        for channel_name, _, _, retention_ms in self._channels:
            try:
                if retention_ms and retention_ms > 0:
                    now_ms = self._server_now_ms()
                    cutoff = now_ms - retention_ms
                    removed = self._redis_client.xtrim(
                        channel_name, minid=f"{cutoff}-0", approximate=True
                    )
                    if removed:
                        footprint.leave(
                            log_type="info",
                            message=f"Trimmed {removed} entries older than {retention_ms}ms in {channel_name}.",
                            controller=controller,
                            subject="Time-based stream trimming",
                            payload={"cutoff_ms": cutoff, "retention_ms": retention_ms},
                        )
                    continue

            except Exception as e:
                footprint.leave(
                    log_type="error",
                    message=f"Error cleaning up messages in channel {channel_name}",
                    controller=controller,
                    subject="Cleaning up messages Error",
                    payload={
                        "error": exception_to_dict(e),
                    },
                )
