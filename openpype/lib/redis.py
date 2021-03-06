from typing import Any

import aioredis
import aioredis.client

from openpype.config import pypeconfig


class Redis:
    connected: bool = False
    redis_pool: aioredis.Redis

    @classmethod
    async def connect(cls) -> None:
        """Create a Redis connection pool"""
        cls.redis_pool = aioredis.from_url(pypeconfig.redis_url)
        cls.connected = True

    @classmethod
    async def get(cls, namespace: str, key: str) -> Any:
        """Get a value from Redis"""
        if not cls.connected:
            await cls.connect()
        value = await cls.redis_pool.get(f"{namespace}-{key}")
        return value

    @classmethod
    async def set(cls, namespace: str, key: str, value: str, ttl: int = 0) -> None:
        """Create/update a record in Redis

        Optional ttl argument may be provided to set expiration time.
        """
        if not cls.connected:
            await cls.connect()
        command = ["set", f"{namespace}-{key}", value]
        if ttl:
            command.extend(["ex", str(ttl)])

        await cls.redis_pool.execute_command(*command)

    @classmethod
    async def delete(cls, namespace: str, key: str) -> None:
        """Delete a record from Redis"""
        if not cls.connected:
            await cls.connect()
        await cls.redis_pool.delete(f"{namespace}-{key}")

    @classmethod
    async def incr(cls, namespace: str, key: str) -> None:
        """Increment a value in Redis"""
        if not cls.connected:
            await cls.connect()
        await cls.redis_pool.incr(f"{namespace}-{key}")

    @classmethod
    async def pubsub(cls) -> aioredis.client.PubSub:
        """Create a Redis pubsub connection"""
        if not cls.connected:
            await cls.connect()
        return cls.redis_pool.pubsub()

    @classmethod
    async def publish(cls, message: str, channel: str | None = None) -> None:
        """Publish a message to a Redis channel"""
        if not cls.connected:
            await cls.connect()
        if channel is None:
            channel = pypeconfig.redis_channel
        await cls.redis_pool.publish(channel, message)
