import json
import asyncio
from typing import Dict, AsyncIterator, Optional
from fastapi import WebSocket
from redis.asyncio import Redis
from redis.exceptions import RedisError
from app.configuration.redis_client import get_async_redis_instance
from app.utils.logger import log


class WSConnectionManager:
    """
    Advanced WebSocket connection manager using Redis for multi-worker coordination.

    Features:
    - Connection tracking across workers
    - Pub/Sub for cross-worker messaging
    - Automatic cleanup
    - Connection state synchronization
    """

    def __init__(
        self,
        redis_instance: Redis,
        redis_prefix: str = "ws",
        expire_time: int = 300,  # 5 minutes
    ):
        self.redis = redis_instance
        self.redis_prefix = redis_prefix
        self.expire_time = expire_time
        self.connections_key = f"{self.redis_prefix}:connections"
        self.client_pubsubs = {}

    def _get_channel_name(self, client_id: str) -> str:
        """Get the Redis channel name for a client"""
        return f"{self.redis_prefix}:channel:{client_id}"

    def _get_connection_key(self, client_id: str) -> str:
        """Get the Redis key for a specific connection"""
        return f"{self.redis_prefix}:connection:{client_id}"

    async def _get_client_pubsub(self, client_id: str) -> Redis.pubsub:
        """Get or create a dedicated pubsub for a client"""
        if client_id not in self.client_pubsubs:
            self.client_pubsubs[client_id] = self.redis.pubsub()
            await self.client_pubsubs[client_id].subscribe(
                self._get_channel_name(client_id)
            )
            log.info(f"Created dedicated pubsub for client {client_id}")

        return self.client_pubsubs[client_id]

    async def connect(self, client_id: str, websocket: WebSocket) -> bool:
        """
        Register a new WebSocket connection.

        Args:
            client_id: Unique client identifier
            websocket: WebSocket connection object

        Returns:
            bool: True if connection was registered successfully
        """
        try:
            connection_data = {
                "client_id": client_id,
                "client_host": f"{websocket.client.host}:{websocket.client.port}",
                "headers": dict(websocket.headers),
                "worker_id": id(self),
            }

            # Use transaction to ensure atomic operations
            async with self.redis.pipeline() as pipe:
                await (
                    pipe.hset(
                        self.connections_key, client_id, json.dumps(connection_data)
                    )
                    .expire(self.connections_key, self.expire_time)
                    .set(
                        self._get_connection_key(client_id),
                        "active",
                        ex=self.expire_time,
                    )
                    .execute()
                )
            await self._get_client_pubsub(client_id)

            log.info(f"Connected client {client_id}")
            return True

        except RedisError as e:
            log.error(f"Redis error connecting client {client_id}: {str(e)}")
            return False

    async def disconnect(self, client_id: str) -> bool:
        """
        Remove a WebSocket connection.

        Args:
            client_id: Unique client identifier

        Returns:
            bool: True if disconnection was successful
        """
        try:
            async with self.redis.pipeline() as pipe:
                await (
                    pipe.hdel(self.connections_key, client_id)
                    .delete(self._get_connection_key(client_id))
                    .execute()
                )

            # Clean up the pubsub connection
            if client_id in self.client_pubsubs:
                pubsub = self.client_pubsubs.pop(client_id)
                await pubsub.unsubscribe(self._get_channel_name(client_id))
                await pubsub.close()

            log.info(f"Disconnected client {client_id}")
            return True

        except RedisError as e:
            log.error(f"Redis error disconnecting client {client_id}: {str(e)}")
            return False
        except Exception as e:
            log.error(f"Unexpected error disconnecting client {client_id}: {str(e)}")
            return False

    async def send_message(self, client_id: str, message: dict) -> bool:
        """
        Send a message to a specific client across workers.

        Args:
            client_id: Target client identifier
            message: Message to send

        Returns:
            bool: True if message was published successfully
        """
        try:
            await self.redis.publish(
                self._get_channel_name(client_id), json.dumps(message)
            )
            return True
        except RedisError as e:
            log.error(f"Redis error sending to client {client_id}: {str(e)}")
            return False

    async def listen_messages(self, client_id: str) -> AsyncIterator[dict]:
        """
        Listen for incoming messages for a specific client.

        Args:
            client_id: Client identifier to listen for

        Yields:
            dict: Received messages
        """
        try:
            pubsub = await self._get_client_pubsub(client_id)

            while True:
                try:
                    message = await pubsub.get_message(
                        ignore_subscribe_messages=True, timeout=1.0
                    )

                    if message and message["type"] == "message":
                        data = message["data"]
                        if isinstance(data, bytes):
                            data = data.decode("utf-8")
                        yield json.loads(data)

                except asyncio.CancelledError:
                    break
                except RedisError as e:
                    log.error(f"Redis error listening for client {client_id}: {str(e)}")
                    await asyncio.sleep(1)
                except Exception as e:
                    log.error(
                        f"Unexpected error listening for client {client_id}: {str(e)}"
                    )
                    await asyncio.sleep(1)

        except Exception as e:
            log.error(f"Fatal error in listen_messages for {client_id}: {str(e)}")
        finally:
            if client_id in self.client_pubsubs:
                try:
                    await self.client_pubsubs[client_id].unsubscribe()
                except Exception:
                    pass

    async def broadcast(self, message: dict, exclude: list[str] = None) -> int:
        """
        Broadcast a message to all connected clients.

        Args:
            message: Message to broadcast
            exclude: List of client IDs to exclude

        Returns:
            int: Number of clients that received the message
        """
        try:
            connections = await self.redis.hgetall(self.connections_key)
            if not connections:
                return 0

            exclude_set = set(exclude or [])
            count = 0
            message_str = json.dumps(message)

            # Use pipeline for better performance with many clients
            async with self.redis.pipeline() as pipe:
                for client_id in connections:
                    client_id = (
                        client_id.decode()
                        if isinstance(client_id, bytes)
                        else client_id
                    )
                    if client_id not in exclude_set:
                        pipe.publish(self._get_channel_name(client_id), message_str)

                # Execute all publish commands in one go
                results = await pipe.execute()
                count = sum(1 for r in results if r)

            return count
        except RedisError as e:
            log.error(f"Redis error broadcasting message: {str(e)}")
            return 0

    async def connection_exists(self, client_id: str) -> bool:
        """Check if a connection exists for the given client ID"""
        try:
            return bool(await self.redis.exists(self._get_connection_key(client_id)))
        except RedisError as e:
            log.error(f"Redis error checking connection {client_id}: {str(e)}")
            return False

    async def get_active_connections(self) -> Dict[str, dict]:
        """Get all active connections with their metadata"""
        try:
            connections = await self.redis.hgetall(self.connections_key)
            return {
                (k.decode() if isinstance(k, bytes) else k): json.loads(
                    v.decode() if isinstance(v, bytes) else v
                )
                for k, v in connections.items()
            }
        except RedisError as e:
            log.error(f"Redis error getting connections: {str(e)}")
            return {}

    async def refresh_connection(self, client_id: str) -> bool:
        """Refresh a connection's TTL to keep it active"""
        try:
            return bool(
                await self.redis.expire(
                    self._get_connection_key(client_id), self.expire_time
                )
            )
        except RedisError as e:
            log.error(f"Redis error refreshing connection {client_id}: {str(e)}")
            return False

    async def cleanup(self):
        """Clean up all resources when shutting down"""
        for client_id, pubsub in list(self.client_pubsubs.items()):
            try:
                await pubsub.unsubscribe()
                await pubsub.close()
            except Exception as e:
                log.error(f"Error closing pubsub for {client_id}: {str(e)}")
        self.client_pubsubs.clear()


# Global instance with enhanced error handling
_connection_manager = None

async def get_connection_manager() -> WSConnectionManager:
    global _connection_manager
    if _connection_manager is None:
        try:
            redis_client = get_async_redis_instance()
            _connection_manager = WSConnectionManager(redis_client)
            log.success("WebSocket Connection Manager initialized successfully")
        except Exception as e:
            log.error(f"Failed to initialize WebSocket Connection Manager: {str(e)}")
            raise
    return _connection_manager


async def cleanup_connection_manager():
    global _connection_manager
    if _connection_manager:
        await _connection_manager.cleanup()
        _connection_manager = None
        log.info("✅ WebSocket Connection Manager disposed")
