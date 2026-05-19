"""Mandatory subscription service."""
import json
from typing import List, Optional
from aiogram import Bot
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database.models import RequiredChannel, GroupSettings
from app.utils.logger import logger


class SubscriptionService:
    """Service for checking mandatory channel subscriptions."""

    async def get_required_channels(
        self,
        group_id: int,
        db: AsyncSession
    ) -> List[RequiredChannel]:
        """
        Get all required channels for a group (including global ones).

        Args:
            group_id: Telegram group ID
            db: Database session

        Returns:
            List of required channels
        """
        result = await db.execute(
            select(RequiredChannel).where(
                RequiredChannel.group_id == group_id,
                RequiredChannel.is_active == True
            )
        )
        return result.scalars().all()

    async def check_user_subscriptions(
        self,
        user_id: int,
        group_id: int,
        bot: Bot,
        db: AsyncSession,
        redis_client=None
    ) -> tuple[bool, List[RequiredChannel]]:
        """
        Check if user is subscribed to all required channels.

        Args:
            user_id: Telegram user ID
            group_id: Telegram group ID
            bot: Aiogram bot instance
            db: Database session
            redis_client: Redis client for caching

        Returns:
            Tuple of (all_subscribed, unsubscribed_channels)
        """
        cache_key = f"sub:{user_id}:{group_id}"

        # Check Redis cache
        if redis_client:
            try:
                cached = await redis_client.get(cache_key)
                if cached:
                    data = json.loads(cached)
                    if data.get("subscribed"):
                        return True, []
            except Exception:
                pass

        channels = await self.get_required_channels(group_id, db)
        if not channels:
            return True, []

        unsubscribed = []
        for channel in channels:
            try:
                member = await bot.get_chat_member(channel.channel_id, user_id)
                if member.status in ("left", "kicked", "banned"):
                    unsubscribed.append(channel)
            except (TelegramForbiddenError, TelegramBadRequest):
                # Bot not in channel or channel not found - skip
                continue
            except Exception as e:
                logger.error(f"Error checking subscription for channel {channel.channel_id}: {e}")
                continue

        all_subscribed = len(unsubscribed) == 0

        # Cache result for 5 minutes
        if redis_client and all_subscribed:
            try:
                await redis_client.setex(
                    cache_key, 300,
                    json.dumps({"subscribed": True})
                )
            except Exception:
                pass

        return all_subscribed, unsubscribed

    async def build_subscription_message(
        self,
        unsubscribed: List[RequiredChannel]
    ) -> tuple[str, list]:
        """
        Build subscription required message with inline buttons.

        Args:
            unsubscribed: List of unsubscribed channels

        Returns:
            Tuple of (message_text, inline_buttons)
        """
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

        msg = "⚠️ <b>Yozish uchun quyidagi kanallarga obuna bo'ling:</b>\n\n"

        buttons = []
        for ch in unsubscribed:
            name = ch.channel_title or ch.channel_username or str(ch.channel_id)
            link = ch.invite_link or (
                f"https://t.me/{ch.channel_username.lstrip('@')}"
                if ch.channel_username else None
            )
            if link:
                buttons.append([InlineKeyboardButton(
                    text=f"📢 {name}",
                    url=link
                )])

        buttons.append([InlineKeyboardButton(
            text="✅ Tekshirish",
            callback_data="check_subscription"
        )])

        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
        return msg, keyboard

    async def invalidate_cache(
        self,
        user_id: int,
        group_id: int,
        redis_client
    ):
        """Invalidate subscription cache for a user."""
        if redis_client:
            try:
                await redis_client.delete(f"sub:{user_id}:{group_id}")
            except Exception:
                pass
