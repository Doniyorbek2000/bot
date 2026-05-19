"""Moderation service for banned words filtering."""
from datetime import datetime, timedelta
from typing import List, Optional
from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database.models import BannedWord, GroupSettings, Warning, AdminLog
from app.utils.logger import logger


class ModerationService:
    """Service for content moderation."""

    async def get_banned_words(
        self,
        group_id: int,
        db: AsyncSession
    ) -> List[str]:
        """
        Get all active banned words for a group.

        Args:
            group_id: Telegram group ID
            db: Database session

        Returns:
            List of banned words (lowercase)
        """
        result = await db.execute(
            select(BannedWord.word).where(
                BannedWord.group_id == group_id,
                BannedWord.is_active == True
            )
        )
        return [row[0].lower() for row in result.fetchall()]

    def check_message(self, text: str, banned_words: List[str]) -> Optional[str]:
        """
        Check if message contains banned words.

        Args:
            text: Message text
            banned_words: List of banned words

        Returns:
            Matched banned word or None
        """
        if not text:
            return None
        text_lower = text.lower()
        for word in banned_words:
            if word in text_lower:
                return word
        return None

    async def apply_penalty(
        self,
        bot: Bot,
        chat_id: int,
        user_id: int,
        message_id: int,
        matched_word: str,
        penalty: str,
        db: AsyncSession
    ):
        """
        Apply moderation penalty.

        Args:
            bot: Aiogram bot instance
            chat_id: Telegram chat ID
            user_id: Telegram user ID
            message_id: Message ID to delete
            matched_word: The banned word that was found
            penalty: Penalty type (delete/warn/mute/ban)
            db: Database session
        """
        try:
            # Always delete the message
            try:
                await bot.delete_message(chat_id, message_id)
            except TelegramBadRequest:
                pass

            if penalty == "delete":
                await self._log_action(db, user_id, chat_id, "delete", matched_word)

            elif penalty == "warn":
                warning_count = await self._add_warning(db, user_id, chat_id, matched_word)
                await bot.send_message(
                    chat_id,
                    f"⚠️ <b>Ogohlantirish!</b>\n"
                    f"Foydalanuvchi taqiqlangan so'z ishlatdi.\n"
                    f"Ogohlantirishlar soni: <b>{warning_count}/3</b>",
                    parse_mode="HTML"
                )
                # Auto-mute after 3 warnings
                if warning_count >= 3:
                    await self._mute_user(bot, chat_id, user_id, db)

            elif penalty == "mute":
                await self._mute_user(bot, chat_id, user_id, db)

            elif penalty == "ban":
                try:
                    await bot.ban_chat_member(chat_id, user_id)
                    await bot.send_message(
                        chat_id,
                        f"🚫 Foydalanuvchi guruhdan chiqarildi (taqiqlangan so'z).",
                        parse_mode="HTML"
                    )
                except Exception as e:
                    logger.error(f"Failed to ban user {user_id}: {e}")
                await self._log_action(db, user_id, chat_id, "ban", matched_word)

        except Exception as e:
            logger.error(f"Error applying penalty: {e}")

    async def _mute_user(
        self,
        bot: Bot,
        chat_id: int,
        user_id: int,
        db: AsyncSession
    ):
        """Mute user for 24 hours."""
        try:
            from aiogram.types import ChatPermissions
            until = datetime.now() + timedelta(hours=24)
            await bot.restrict_chat_member(
                chat_id,
                user_id,
                permissions=ChatPermissions(can_send_messages=False),
                until_date=until
            )
            await bot.send_message(
                chat_id,
                f"🔇 Foydalanuvchi 24 soatga cheklandi (taqiqlangan so'z).",
                parse_mode="HTML"
            )
            await self._log_action(db, user_id, chat_id, "mute", "24h")
        except Exception as e:
            logger.error(f"Failed to mute user {user_id}: {e}")

    async def _add_warning(
        self,
        db: AsyncSession,
        user_id: int,
        group_id: int,
        reason: str
    ) -> int:
        """Add warning and return total count."""
        warning = Warning(
            user_id=user_id,
            group_id=group_id,
            reason=reason[:200]
        )
        db.add(warning)
        await db.commit()

        # Count total warnings
        result = await db.execute(
            select(func.count(Warning.id)).where(
                Warning.user_id == user_id,
                Warning.group_id == group_id
            )
        )
        return result.scalar_one()

    async def _log_action(
        self,
        db: AsyncSession,
        user_id: int,
        group_id: int,
        action: str,
        details: str
    ):
        """Log moderation action."""
        try:
            log = AdminLog(
                admin_id=None,
                group_id=group_id,
                action=f"moderation_{action}",
                details=f"user:{user_id} word:{details}",
                level="info"
            )
            db.add(log)
            await db.commit()
        except Exception:
            pass

    async def add_banned_word(
        self,
        group_id: int,
        word: str,
        added_by: int,
        db: AsyncSession
    ) -> bool:
        """
        Add a banned word for a group.

        Args:
            group_id: Telegram group ID
            word: Word to ban
            added_by: Admin user ID
            db: Database session

        Returns:
            True if added, False if already exists
        """
        try:
            existing = await db.execute(
                select(BannedWord).where(
                    BannedWord.group_id == group_id,
                    BannedWord.word == word.lower()
                )
            )
            if existing.scalar_one_or_none():
                return False

            bw = BannedWord(
                group_id=group_id,
                word=word.lower(),
                added_by=added_by
            )
            db.add(bw)
            await db.commit()
            return True

        except Exception as e:
            logger.error(f"Error adding banned word: {e}")
            return False

    async def remove_banned_word(
        self,
        group_id: int,
        word: str,
        db: AsyncSession
    ) -> bool:
        """Remove a banned word."""
        try:
            result = await db.execute(
                select(BannedWord).where(
                    BannedWord.group_id == group_id,
                    BannedWord.word == word.lower()
                )
            )
            bw = result.scalar_one_or_none()
            if bw:
                await db.delete(bw)
                await db.commit()
                return True
            return False
        except Exception as e:
            logger.error(f"Error removing banned word: {e}")
            return False
