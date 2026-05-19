"""Admin filters for aiogram."""
from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery

from app.utils.config import settings


class IsSuperAdmin(BaseFilter):
    """Filter that checks if user is super admin."""

    async def __call__(self, event: Message | CallbackQuery) -> bool:
        """
        Check if user is super admin.

        Args:
            event: Message or callback query

        Returns:
            True if user is super admin
        """
        user_id = event.from_user.id
        return user_id in settings.super_admin_ids_list


class IsGroupAdmin(BaseFilter):
    """Filter that checks if user is group admin."""

    async def __call__(self, message: Message) -> bool:
        """
        Check if user is group admin.

        Args:
            message: Message event

        Returns:
            True if user is group admin
        """
        if message.chat.type == "private":
            return False

        try:
            member = await message.bot.get_chat_member(
                message.chat.id,
                message.from_user.id
            )
            return member.status in ("administrator", "creator")
        except Exception:
            return False
