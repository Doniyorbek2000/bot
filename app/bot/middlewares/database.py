"""Database middleware for aiogram."""
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from app.database.session import AsyncSessionLocal


class DatabaseMiddleware(BaseMiddleware):
    """Middleware that provides database session to handlers."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        """
        Inject database session into handler data.

        Args:
            handler: Next handler
            event: Telegram event
            data: Handler data dict

        Returns:
            Handler result
        """
        async with AsyncSessionLocal() as session:
            data["db"] = session
            try:
                result = await handler(event, data)
                await session.commit()
                return result
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
