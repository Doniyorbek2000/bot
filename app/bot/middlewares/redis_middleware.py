"""Redis middleware for aiogram."""
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject


class RedisMiddleware(BaseMiddleware):
    """Middleware that provides Redis client to handlers."""

    def __init__(self, redis_client):
        """
        Initialize Redis middleware.

        Args:
            redis_client: Redis async client instance
        """
        self.redis = redis_client

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        """
        Inject Redis client into handler data.

        Args:
            handler: Next handler
            event: Telegram event
            data: Handler data dict

        Returns:
            Handler result
        """
        data["redis"] = self.redis
        return await handler(event, data)
