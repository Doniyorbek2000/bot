"""Rate limiting middleware."""
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message

from app.utils.logger import logger


class RateLimitMiddleware(BaseMiddleware):
    """Middleware for rate limiting user messages."""

    def __init__(self, redis_client, limit: int = 30, window: int = 60):
        """
        Initialize rate limiter.

        Args:
            redis_client: Redis client
            limit: Max messages per window
            window: Time window in seconds
        """
        self.redis = redis_client
        self.limit = limit
        self.window = window

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        """
        Check rate limit before processing message.

        Args:
            handler: Next handler
            event: Message event
            data: Handler data

        Returns:
            Handler result or None if rate limited
        """
        if not self.redis or not isinstance(event, Message):
            return await handler(event, data)

        user_id = event.from_user.id
        chat_id = event.chat.id if event.chat else user_id
        key = f"ratelimit:{user_id}:{chat_id}"

        try:
            count = await self.redis.get(key)
            if count and int(count) >= self.limit:
                logger.warning(f"Rate limit exceeded for user {user_id} in chat {chat_id}")
                # Silently ignore excess messages
                return None

            # Increment counter
            pipe = self.redis.pipeline()
            pipe.incr(key)
            pipe.expire(key, self.window)
            await pipe.execute()

        except Exception as e:
            logger.error(f"Rate limit check error: {e}")

        return await handler(event, data)
