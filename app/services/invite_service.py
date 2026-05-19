"""Invite tracking service."""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database.models import InviteTracking, GroupSettings
from app.utils.logger import logger


class InviteService:
    """Service for tracking user invites."""

    async def record_invite(
        self,
        inviter_id: int,
        invited_id: int,
        group_id: int,
        db: AsyncSession
    ) -> bool:
        """
        Record a new member invite.

        Args:
            inviter_id: User who invited
            invited_id: User who was invited
            group_id: Telegram group ID
            db: Database session

        Returns:
            True if recorded successfully
        """
        try:
            # Check if already exists
            result = await db.execute(
                select(InviteTracking).where(
                    InviteTracking.inviter_id == inviter_id,
                    InviteTracking.invited_id == invited_id,
                    InviteTracking.group_id == group_id
                )
            )
            if result.scalar_one_or_none():
                return False  # Already recorded

            invite = InviteTracking(
                inviter_id=inviter_id,
                invited_id=invited_id,
                group_id=group_id,
                is_valid=True
            )
            db.add(invite)
            await db.commit()
            return True

        except Exception as e:
            logger.error(f"Error recording invite: {e}")
            return False

    async def get_invite_count(
        self,
        user_id: int,
        group_id: int,
        db: AsyncSession
    ) -> int:
        """
        Get valid invite count for a user in a group.

        Args:
            user_id: Telegram user ID
            group_id: Telegram group ID
            db: Database session

        Returns:
            Number of valid invites
        """
        try:
            result = await db.execute(
                select(func.count(InviteTracking.id)).where(
                    InviteTracking.inviter_id == user_id,
                    InviteTracking.group_id == group_id,
                    InviteTracking.is_valid == True
                )
            )
            count = result.scalar_one()
            return count

        except Exception as e:
            logger.error(f"Error getting invite count: {e}")
            return 0

    async def check_invite_threshold(
        self,
        user_id: int,
        group_id: int,
        db: AsyncSession
    ) -> tuple[bool, int, int]:
        """
        Check if user has met the invite threshold.

        Args:
            user_id: Telegram user ID
            group_id: Telegram group ID
            db: Database session

        Returns:
            Tuple of (threshold_met, current_count, required_count)
        """
        try:
            # Get threshold
            result = await db.execute(
                select(GroupSettings.invite_threshold).where(
                    GroupSettings.group_id == group_id
                )
            )
            threshold = result.scalar_one_or_none() or 3

            # Get current count
            count = await self.get_invite_count(user_id, group_id, db)

            return count >= threshold, count, threshold

        except Exception as e:
            logger.error(f"Error checking invite threshold: {e}")
            return True, 0, 0  # Allow by default on error

    async def invalidate_invite(
        self,
        invited_id: int,
        group_id: int,
        db: AsyncSession
    ):
        """
        Invalidate an invite when user leaves the group.

        Args:
            invited_id: User who left
            group_id: Telegram group ID
            db: Database session
        """
        try:
            result = await db.execute(
                select(InviteTracking).where(
                    InviteTracking.invited_id == invited_id,
                    InviteTracking.group_id == group_id
                )
            )
            invite = result.scalar_one_or_none()
            if invite:
                invite.is_valid = False
                await db.commit()

        except Exception as e:
            logger.error(f"Error invalidating invite: {e}")

    def build_invite_progress_message(
        self,
        current: int,
        required: int
    ) -> str:
        """
        Build invite progress message.

        Args:
            current: Current invite count
            required: Required invite count

        Returns:
            Formatted message
        """
        remaining = max(0, required - current)
        progress = min(100, int((current / required) * 100))

        msg = f"""⚠️ <b>Yozish uchun guruhga odam qo'shing</b>

📊 Sizning natijangiz: <b>{current}/{required}</b>
📈 Progress: <b>{progress}%</b>

"""
        if remaining > 0:
            msg += f"Yana <b>{remaining}</b> ta odam qo'shishingiz kerak."
        else:
            msg += "✅ Siz yozish huquqiga ega bo'ldingiz!"

        return msg
