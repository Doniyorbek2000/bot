"""Group event handlers: new members, messages, etc."""
from aiogram import Router, F
from aiogram.types import Message, ChatMemberUpdated
from aiogram.filters import ChatMemberUpdatedFilter, JOIN_TRANSITION, LEAVE_TRANSITION
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database.models import Group, GroupSettings
from app.services.subscription_service import SubscriptionService
from app.services.invite_service import InviteService
from app.services.moderation_service import ModerationService
from app.utils.logger import logger

router = Router()

subscription_service = SubscriptionService()
invite_service = InviteService()
moderation_service = ModerationService()


@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=JOIN_TRANSITION))
async def bot_added_to_group(event: ChatMemberUpdated, db: AsyncSession):
    """Handle bot being added to a group."""
    chat = event.chat
    if chat.type not in ("group", "supergroup", "channel"):
        return

    # Register group
    result = await db.execute(
        select(Group).where(Group.telegram_id == chat.id)
    )
    group = result.scalar_one_or_none()

    if not group:
        group = Group(
            telegram_id=chat.id,
            title=chat.title or "Unknown",
            username=chat.username,
            chat_type=chat.type,
            is_active=True,
            added_by=event.from_user.id if event.from_user else None
        )
        db.add(group)
        await db.commit()

        # Create default settings
        group_settings = GroupSettings(group_id=chat.id)
        db.add(group_settings)
        await db.commit()

        logger.info(f"Bot added to group: {chat.id} ({chat.title})")

        # Send welcome message
        try:
            await event.bot.send_message(
                chat.id,
                f"👋 <b>Hududiy Agent Bot</b> guruhga qo'shildi!\n\n"
                f"Guruh adminlari /admin buyrug'i orqali botni sozlashlari mumkin.",
                parse_mode="HTML"
            )
        except Exception:
            pass
    else:
        group.is_active = True
        await db.commit()


@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=LEAVE_TRANSITION))
async def bot_removed_from_group(event: ChatMemberUpdated, db: AsyncSession):
    """Handle bot being removed from a group."""
    result = await db.execute(
        select(Group).where(Group.telegram_id == event.chat.id)
    )
    group = result.scalar_one_or_none()
    if group:
        group.is_active = False
        await db.commit()
        logger.info(f"Bot removed from group: {event.chat.id}")


@router.chat_member(ChatMemberUpdatedFilter(member_status_changed=JOIN_TRANSITION))
async def new_member_joined(event: ChatMemberUpdated, db: AsyncSession):
    """Handle new member joining a group."""
    # Skip bots
    if event.new_chat_member.user.is_bot:
        return

    # Get group settings
    result = await db.execute(
        select(GroupSettings).where(GroupSettings.group_id == event.chat.id)
    )
    settings = result.scalar_one_or_none()

    if not settings or not settings.invite_enabled:
        return

    # Record invite if invited by someone
    if event.from_user and event.from_user.id != event.new_chat_member.user.id:
        inviter_id = event.from_user.id
        invited_id = event.new_chat_member.user.id

        # Don't count bots
        if not event.from_user.is_bot:
            await invite_service.record_invite(
                inviter_id, invited_id, event.chat.id, db
            )


@router.chat_member(ChatMemberUpdatedFilter(member_status_changed=LEAVE_TRANSITION))
async def member_left(event: ChatMemberUpdated, db: AsyncSession):
    """Handle member leaving a group."""
    if event.old_chat_member.user.is_bot:
        return

    # Invalidate their invite
    await invite_service.invalidate_invite(
        event.old_chat_member.user.id,
        event.chat.id,
        db
    )


@router.message(F.chat.type.in_({"group", "supergroup"}))
async def handle_group_message(message: Message, db: AsyncSession, redis=None):
    """Handle all group messages for moderation and access control."""
    if not message.from_user or message.from_user.is_bot:
        return

    # Get group settings
    result = await db.execute(
        select(GroupSettings).where(GroupSettings.group_id == message.chat.id)
    )
    settings = result.scalar_one_or_none()

    if not settings:
        return

    # Check if group is blocked
    group_result = await db.execute(
        select(Group).where(Group.telegram_id == message.chat.id)
    )
    group = group_result.scalar_one_or_none()
    if group and group.is_blocked:
        try:
            await message.delete()
        except Exception:
            pass
        return

    # Check admin - admins bypass restrictions
    try:
        member = await message.bot.get_chat_member(message.chat.id, message.from_user.id)
        is_admin = member.status in ("administrator", "creator")
    except Exception:
        is_admin = False

    if is_admin:
        # Still check moderation for admins
        if settings.moderation_enabled and message.text:
            await _check_moderation(message, settings, db)
        return

    # 1. Check mandatory subscription
    if settings.subscription_enabled:
        subscribed, unsubscribed = await subscription_service.check_user_subscriptions(
            message.from_user.id, message.chat.id, message.bot, db, redis
        )
        if not subscribed:
            try:
                await message.delete()
            except Exception:
                pass
            msg_text, keyboard = await subscription_service.build_subscription_message(unsubscribed)
            try:
                await message.bot.send_message(
                    message.from_user.id,
                    msg_text,
                    reply_markup=keyboard,
                    parse_mode="HTML"
                )
            except Exception:
                try:
                    sent = await message.answer(
                        msg_text,
                        reply_markup=keyboard,
                        parse_mode="HTML"
                    )
                    import asyncio
                    await asyncio.sleep(5)
                    await sent.delete()
                except Exception:
                    pass
            return

    # 2. Check invite threshold
    if settings.invite_enabled:
        met, current, required = await invite_service.check_invite_threshold(
            message.from_user.id, message.chat.id, db
        )
        if not met:
            try:
                await message.delete()
            except Exception:
                pass
            progress_msg = invite_service.build_invite_progress_message(current, required)
            try:
                await message.bot.send_message(
                    message.from_user.id,
                    progress_msg,
                    parse_mode="HTML"
                )
            except Exception:
                pass
            return

    # 3. Check moderation (banned words)
    if settings.moderation_enabled and message.text:
        await _check_moderation(message, settings, db)


async def _check_moderation(message: Message, settings: GroupSettings, db: AsyncSession):
    """Check message for banned words and apply penalty."""
    banned_words = await moderation_service.get_banned_words(message.chat.id, db)
    if not banned_words:
        return

    matched = moderation_service.check_message(message.text, banned_words)
    if matched:
        await moderation_service.apply_penalty(
            message.bot,
            message.chat.id,
            message.from_user.id,
            message.message_id,
            matched,
            settings.ban_penalty,
            db
        )
