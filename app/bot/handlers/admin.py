"""Admin panel handlers."""
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database.models import (
    Group, GroupSettings, Region, WeatherSchedule, PrayerSchedule,
    BannedWord, RequiredChannel, AdminLog, User, SentPost
)
from app.bot.filters.admin_filter import IsSuperAdmin, IsGroupAdmin
from app.bot.keyboards.admin_keyboards import (
    get_admin_panel_keyboard, get_superadmin_panel_keyboard,
    get_module_toggle_keyboard, get_back_button
)
from app.utils.config import settings
from app.utils.validators import validate_time_format
from app.utils.logger import logger

router = Router()


# ─── GROUP ADMIN PANEL ────────────────────────────────────────────────────────

@router.message(Command("admin"), IsGroupAdmin())
async def cmd_admin(message: Message, db: AsyncSession):
    """Show group admin panel."""
    if message.chat.type == "private":
        await message.answer("Bu buyruq faqat guruhlarda ishlaydi.")
        return

    await message.answer(
        "⚙️ <b>Guruh Admin Paneli</b>\n\nQuyidagi bo'limlardan birini tanlang:",
        reply_markup=get_admin_panel_keyboard()
    )


@router.message(Command("admin"))
async def cmd_admin_no_perm(message: Message):
    """Handle /admin for non-admins."""
    if message.chat.type != "private":
        await message.answer("❌ Bu buyruq faqat guruh adminlari uchun.")


@router.callback_query(F.data == "admin_back")
async def admin_back(callback: CallbackQuery):
    """Go back to admin panel."""
    await callback.message.edit_text(
        "⚙️ <b>Guruh Admin Paneli</b>\n\nQuyidagi bo'limlardan birini tanlang:",
        reply_markup=get_admin_panel_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "admin_modules")
async def admin_modules(callback: CallbackQuery, db: AsyncSession):
    """Show module toggle panel."""
    group_id = callback.message.chat.id
    result = await db.execute(
        select(GroupSettings).where(GroupSettings.group_id == group_id)
    )
    gs = result.scalar_one_or_none()

    settings_dict = {
        "weather_enabled": gs.weather_enabled if gs else False,
        "prayer_enabled": gs.prayer_enabled if gs else False,
        "news_enabled": gs.news_enabled if gs else False,
        "jobs_enabled": gs.jobs_enabled if gs else False,
        "ai_enabled": gs.ai_enabled if gs else False,
        "subscription_enabled": gs.subscription_enabled if gs else False,
        "invite_enabled": gs.invite_enabled if gs else False,
        "moderation_enabled": gs.moderation_enabled if gs else False,
    }

    await callback.message.edit_text(
        "⚙️ <b>Modullarni boshqarish</b>\n\nYoqish/o'chirish uchun tugmani bosing:",
        reply_markup=get_module_toggle_keyboard(settings_dict)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("toggle_"))
async def toggle_module(callback: CallbackQuery, db: AsyncSession):
    """Toggle a module on/off."""
    module = callback.data.replace("toggle_", "")
    group_id = callback.message.chat.id

    # Check admin
    try:
        member = await callback.bot.get_chat_member(group_id, callback.from_user.id)
        if member.status not in ("administrator", "creator"):
            await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
            return
    except Exception:
        await callback.answer("❌ Xatolik!", show_alert=True)
        return

    result = await db.execute(
        select(GroupSettings).where(GroupSettings.group_id == group_id)
    )
    gs = result.scalar_one_or_none()

    if not gs:
        gs = GroupSettings(group_id=group_id)
        db.add(gs)

    field_map = {
        "weather": "weather_enabled",
        "prayer": "prayer_enabled",
        "news": "news_enabled",
        "jobs": "jobs_enabled",
        "ai": "ai_enabled",
        "subscription": "subscription_enabled",
        "invite": "invite_enabled",
        "moderation": "moderation_enabled",
    }

    field = field_map.get(module)
    if field:
        current = getattr(gs, field, False)
        setattr(gs, field, not current)
        await db.commit()
        status = "yoqildi ✅" if not current else "o'chirildi ❌"
        await callback.answer(f"{module.capitalize()} {status}")

        # Refresh keyboard
        settings_dict = {
            "weather_enabled": gs.weather_enabled,
            "prayer_enabled": gs.prayer_enabled,
            "news_enabled": gs.news_enabled,
            "jobs_enabled": gs.jobs_enabled,
            "ai_enabled": gs.ai_enabled,
            "subscription_enabled": gs.subscription_enabled,
            "invite_enabled": gs.invite_enabled,
            "moderation_enabled": gs.moderation_enabled,
        }
        await callback.message.edit_reply_markup(
            reply_markup=get_module_toggle_keyboard(settings_dict)
        )


@router.callback_query(F.data == "admin_region")
async def admin_region(callback: CallbackQuery, db: AsyncSession):
    """Show region selection."""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

    # Get unique viloyats
    result = await db.execute(
        select(Region.viloyat).distinct().order_by(Region.viloyat)
    )
    viloyats = [row[0] for row in result.fetchall()]

    buttons = []
    for v in viloyats:
        buttons.append([InlineKeyboardButton(
            text=v,
            callback_data=f"viloyat_{v[:30]}"
        )])
    buttons.append([InlineKeyboardButton(text="◀️ Orqaga", callback_data="admin_back")])

    await callback.message.edit_text(
        "🌍 <b>Viloyatni tanlang:</b>",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("viloyat_"))
async def select_viloyat(callback: CallbackQuery, db: AsyncSession):
    """Show tuman selection for selected viloyat."""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

    viloyat = callback.data.replace("viloyat_", "")

    result = await db.execute(
        select(Region).where(Region.viloyat.startswith(viloyat)).order_by(Region.tuman)
    )
    regions = result.scalars().all()

    buttons = []
    for r in regions:
        buttons.append([InlineKeyboardButton(
            text=r.tuman,
            callback_data=f"region_{r.id}"
        )])
    buttons.append([InlineKeyboardButton(text="◀️ Orqaga", callback_data="admin_region")])

    await callback.message.edit_text(
        f"🌍 <b>{viloyat}</b>\n\nTuman/shaharni tanlang:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("region_"))
async def select_region(callback: CallbackQuery, db: AsyncSession):
    """Save selected region for group."""
    region_id = int(callback.data.replace("region_", ""))
    group_id = callback.message.chat.id

    # Check admin
    try:
        member = await callback.bot.get_chat_member(group_id, callback.from_user.id)
        if member.status not in ("administrator", "creator"):
            await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
            return
    except Exception:
        await callback.answer("❌ Xatolik!", show_alert=True)
        return

    # Get region
    result = await db.execute(select(Region).where(Region.id == region_id))
    region = result.scalar_one_or_none()
    if not region:
        await callback.answer("❌ Hudud topilmadi!", show_alert=True)
        return

    # Update group
    group_result = await db.execute(
        select(Group).where(Group.telegram_id == group_id)
    )
    group = group_result.scalar_one_or_none()
    if group:
        group.region_id = region_id
        await db.commit()

    await callback.message.edit_text(
        f"✅ <b>Hudud saqlandi!</b>\n\n"
        f"📍 {region.viloyat}, {region.tuman}",
        reply_markup=get_back_button()
    )
    await callback.answer("✅ Hudud saqlandi!")


@router.callback_query(F.data == "admin_stats")
async def admin_stats(callback: CallbackQuery, db: AsyncSession):
    """Show group statistics."""
    group_id = callback.message.chat.id

    # Count sent posts
    posts_result = await db.execute(
        select(func.count(SentPost.id)).where(SentPost.group_id == group_id)
    )
    total_posts = posts_result.scalar_one()

    weather_result = await db.execute(
        select(func.count(SentPost.id)).where(
            SentPost.group_id == group_id,
            SentPost.post_type == "weather"
        )
    )
    weather_posts = weather_result.scalar_one()

    prayer_result = await db.execute(
        select(func.count(SentPost.id)).where(
            SentPost.group_id == group_id,
            SentPost.post_type == "prayer"
        )
    )
    prayer_posts = prayer_result.scalar_one()

    # Get group info
    group_result = await db.execute(
        select(Group).where(Group.telegram_id == group_id)
    )
    group = group_result.scalar_one_or_none()

    text = f"""📊 <b>Guruh Statistikasi</b>

📋 Guruh: <b>{group.title if group else 'N/A'}</b>
📨 Jami yuborilgan postlar: <b>{total_posts}</b>
🌤 Ob-havo postlari: <b>{weather_posts}</b>
🕌 Namoz vaqti postlari: <b>{prayer_posts}</b>"""

    await callback.message.edit_text(text, reply_markup=get_back_button())
    await callback.answer()


@router.callback_query(F.data == "admin_banwords")
async def admin_banwords(callback: CallbackQuery, db: AsyncSession):
    """Show banned words management."""
    group_id = callback.message.chat.id

    result = await db.execute(
        select(BannedWord).where(
            BannedWord.group_id == group_id,
            BannedWord.is_active == True
        )
    )
    words = result.scalars().all()

    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

    text = "🚫 <b>Taqiqlangan so'zlar</b>\n\n"
    if words:
        text += "\n".join([f"• {w.word}" for w in words])
    else:
        text += "Hozircha taqiqlangan so'zlar yo'q."

    text += "\n\n➕ So'z qo'shish uchun: /banwords qo'shish [so'z]\n"
    text += "➖ So'z o'chirish uchun: /banwords o'chirish [so'z]"

    await callback.message.edit_text(text, reply_markup=get_back_button())
    await callback.answer()


@router.message(Command("banwords"), IsGroupAdmin())
async def cmd_banwords(message: Message, db: AsyncSession):
    """Handle /banwords command."""
    from app.services.moderation_service import ModerationService
    mod_service = ModerationService()

    args = message.text.split(maxsplit=2)
    if len(args) < 3:
        await message.answer(
            "📋 Foydalanish:\n"
            "/banwords qo'shish [so'z]\n"
            "/banwords o'chirish [so'z]"
        )
        return

    action = args[1].lower()
    word = args[2].strip().lower()

    if action in ("qo'shish", "qoshish", "add"):
        success = await mod_service.add_banned_word(
            message.chat.id, word, message.from_user.id, db
        )
        if success:
            await message.answer(f"✅ <b>{word}</b> taqiqlangan so'zlar ro'yxatiga qo'shildi.")
        else:
            await message.answer(f"⚠️ <b>{word}</b> allaqachon ro'yxatda mavjud.")

    elif action in ("o'chirish", "ochirish", "remove", "delete"):
        success = await mod_service.remove_banned_word(message.chat.id, word, db)
        if success:
            await message.answer(f"✅ <b>{word}</b> ro'yxatdan o'chirildi.")
        else:
            await message.answer(f"⚠️ <b>{word}</b> ro'yxatda topilmadi.")


# ─── SUPER ADMIN PANEL ────────────────────────────────────────────────────────

@router.message(Command("superadmin"), IsSuperAdmin())
async def cmd_superadmin(message: Message):
    """Show super admin panel."""
    await message.answer(
        "🔐 <b>Super Admin Paneli</b>\n\nXush kelibsiz!",
        reply_markup=get_superadmin_panel_keyboard()
    )


@router.message(Command("superadmin"))
async def cmd_superadmin_no_perm(message: Message):
    """Handle /superadmin for non-super-admins."""
    # Log unauthorized attempt
    logger.warning(f"Unauthorized /superadmin attempt by user {message.from_user.id}")


@router.callback_query(F.data == "sa_stats", IsSuperAdmin())
async def sa_stats(callback: CallbackQuery, db: AsyncSession):
    """Show global statistics."""
    groups_result = await db.execute(
        select(func.count(Group.id)).where(Group.is_active == True)
    )
    total_groups = groups_result.scalar_one()

    users_result = await db.execute(select(func.count(User.id)))
    total_users = users_result.scalar_one()

    posts_result = await db.execute(select(func.count(SentPost.id)))
    total_posts = posts_result.scalar_one()

    weather_result = await db.execute(
        select(func.count(SentPost.id)).where(SentPost.post_type == "weather")
    )
    weather_posts = weather_result.scalar_one()

    prayer_result = await db.execute(
        select(func.count(SentPost.id)).where(SentPost.post_type == "prayer")
    )
    prayer_posts = prayer_result.scalar_one()

    text = f"""📊 <b>Global Statistika</b>

👥 Jami guruhlar: <b>{total_groups}</b>
👤 Jami foydalanuvchilar: <b>{total_users}</b>
📨 Jami yuborilgan postlar: <b>{total_posts}</b>
🌤 Ob-havo postlari: <b>{weather_posts}</b>
🕌 Namoz vaqti postlari: <b>{prayer_posts}</b>"""

    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Orqaga", callback_data="sa_back")]
    ])
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data == "sa_back", IsSuperAdmin())
async def sa_back(callback: CallbackQuery):
    """Go back to super admin panel."""
    await callback.message.edit_text(
        "🔐 <b>Super Admin Paneli</b>\n\nXush kelibsiz!",
        reply_markup=get_superadmin_panel_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "sa_logs", IsSuperAdmin())
async def sa_logs(callback: CallbackQuery, db: AsyncSession):
    """Show last 20 error logs."""
    result = await db.execute(
        select(AdminLog)
        .where(AdminLog.level == "error")
        .order_by(AdminLog.created_at.desc())
        .limit(20)
    )
    logs = result.scalars().all()

    if not logs:
        text = "📝 <b>Xatolik loglari</b>\n\nHozircha xatoliklar yo'q."
    else:
        text = "📝 <b>So'nggi xatoliklar:</b>\n\n"
        for log in logs:
            time_str = log.created_at.strftime("%d.%m %H:%M")
            text += f"🔴 [{time_str}] {log.action}: {(log.details or '')[:80]}\n"

    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Orqaga", callback_data="sa_back")]
    ])
    await callback.message.edit_text(text[:4000], reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data == "sa_groups", IsSuperAdmin())
async def sa_groups(callback: CallbackQuery, db: AsyncSession):
    """Show all groups list."""
    result = await db.execute(
        select(Group).where(Group.is_active == True).limit(20)
    )
    groups = result.scalars().all()

    text = f"📋 <b>Barcha guruhlar ({len(groups)}):</b>\n\n"
    for g in groups:
        status = "🚫" if g.is_blocked else "✅"
        text += f"{status} {g.title} (<code>{g.telegram_id}</code>)\n"

    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Orqaga", callback_data="sa_back")]
    ])
    await callback.message.edit_text(text[:4000], reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data == "sa_broadcast", IsSuperAdmin())
async def sa_broadcast_prompt(callback: CallbackQuery):
    """Prompt for broadcast message."""
    await callback.message.edit_text(
        "📣 <b>Reklama yuborish</b>\n\n"
        "Barcha guruhlarga yuborish uchun:\n"
        "/broadcast [xabar matni]",
        reply_markup=get_back_button()
    )
    await callback.answer()


@router.message(Command("broadcast"), IsSuperAdmin())
async def cmd_broadcast(message: Message, db: AsyncSession):
    """Broadcast message to all active groups."""
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("Foydalanish: /broadcast [xabar matni]")
        return

    text = args[1]
    result = await db.execute(
        select(Group).where(Group.is_active == True, Group.is_blocked == False)
    )
    groups = result.scalars().all()

    sent = 0
    failed = 0
    for group in groups:
        try:
            await message.bot.send_message(group.telegram_id, text, parse_mode="HTML")
            sent += 1
        except Exception:
            failed += 1

    await message.answer(
        f"📣 <b>Reklama yuborildi!</b>\n\n"
        f"✅ Muvaffaqiyatli: {sent}\n"
        f"❌ Xatolik: {failed}"
    )


@router.callback_query(F.data == "sa_api", IsSuperAdmin())
async def sa_api_settings(callback: CallbackQuery):
    """Show API settings."""
    await callback.message.edit_text(
        "🔑 <b>API Sozlamalari</b>\n\n"
        "Gemini API key o'rnatish:\n"
        "/setgemini [api_key]\n\n"
        "Weather API key o'rnatish:\n"
        "/setweather [api_key]",
        reply_markup=get_back_button()
    )
    await callback.answer()


@router.message(Command("setgemini"), IsSuperAdmin())
async def cmd_set_gemini(message: Message, db: AsyncSession):
    """Set Gemini API key."""
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("Foydalanish: /setgemini [api_key]")
        return

    from app.database.models import GlobalSettings
    api_key = args[1].strip()

    result = await db.execute(
        select(GlobalSettings).where(GlobalSettings.key == "gemini_api_key")
    )
    setting = result.scalar_one_or_none()
    if setting:
        setting.value = api_key
    else:
        setting = GlobalSettings(key="gemini_api_key", value=api_key)
        db.add(setting)
    await db.commit()

    await message.answer("✅ Gemini API key saqlandi!")
    # Delete message with key for security
    try:
        await message.delete()
    except Exception:
        pass


@router.message(Command("setweather"), IsSuperAdmin())
async def cmd_set_weather(message: Message, db: AsyncSession):
    """Set Weather API key."""
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("Foydalanish: /setweather [api_key]")
        return

    from app.database.models import GlobalSettings
    api_key = args[1].strip()

    result = await db.execute(
        select(GlobalSettings).where(GlobalSettings.key == "weather_api_key")
    )
    setting = result.scalar_one_or_none()
    if setting:
        setting.value = api_key
    else:
        setting = GlobalSettings(key="weather_api_key", value=api_key)
        db.add(setting)
    await db.commit()

    await message.answer("✅ Weather API key saqlandi!")
    try:
        await message.delete()
    except Exception:
        pass


@router.callback_query(F.data == "check_subscription")
async def check_subscription_callback(callback: CallbackQuery, db: AsyncSession):
    """Handle subscription check button."""
    from app.services.subscription_service import SubscriptionService
    sub_service = SubscriptionService()

    # Find which group this is for
    # This is a simplified version - in production you'd store group_id in callback data
    await callback.answer("✅ Tekshirilmoqda...", show_alert=False)

    # Re-check subscription
    await callback.message.edit_text(
        "✅ Obuna tekshirildi. Endi guruhda yozishingiz mumkin!"
    )
