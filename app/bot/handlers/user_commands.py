"""User command handlers: /weather, /prayer, /news, /jobs, /ai."""
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database.models import Group, GroupSettings, Region
from app.services.weather_service import WeatherService
from app.services.prayer_service import PrayerService
from app.services.news_service import NewsService
from app.services.jobs_service import JobsService
from app.services.gemini_service import GeminiService
from app.utils.logger import logger

router = Router()

weather_service = WeatherService()
prayer_service = PrayerService()
news_service = NewsService()
jobs_service = JobsService()
gemini_service = GeminiService()


@router.message(Command("weather"))
async def cmd_weather(message: Message, db: AsyncSession):
    """Handle /weather command."""
    if message.chat.type == "private":
        await message.answer("Bu buyruq faqat guruhlarda ishlaydi.")
        return

    group_id = message.chat.id

    # Get group and region
    result = await db.execute(select(Group).where(Group.telegram_id == group_id))
    group = result.scalar_one_or_none()

    if not group or not group.region_id:
        await message.answer("⚠️ Guruh hududi sozlanmagan. Admin /admin buyrug'ini yuborsin.")
        return

    region_result = await db.execute(select(Region).where(Region.id == group.region_id))
    region = region_result.scalar_one_or_none()

    if not region or not region.latitude:
        await message.answer("⚠️ Hudud koordinatalari topilmadi.")
        return

    await message.answer("⏳ Ob-havo ma'lumotlari olinmoqda...")

    weather = await weather_service.fetch_weather(region.latitude, region.longitude, db)
    if not weather:
        await message.answer("❌ Ob-havo ma'lumotlarini olishda xatolik yuz berdi.")
        return

    # Check if AI enabled
    settings_result = await db.execute(
        select(GroupSettings).where(GroupSettings.group_id == group_id)
    )
    group_settings = settings_result.scalar_one_or_none()
    ai_enabled = group_settings.ai_enabled if group_settings else False

    recommendation = ""
    if ai_enabled:
        try:
            recommendation = await gemini_service.format_weather_recommendation(weather, db)
        except Exception:
            pass

    region_name = f"{region.viloyat}, {region.tuman}"
    msg = weather_service.format_weather_message(weather, region_name, recommendation)
    await message.answer(msg)


@router.message(Command("prayer"))
async def cmd_prayer(message: Message, db: AsyncSession):
    """Handle /prayer command."""
    if message.chat.type == "private":
        await message.answer("Bu buyruq faqat guruhlarda ishlaydi.")
        return

    group_id = message.chat.id

    result = await db.execute(select(Group).where(Group.telegram_id == group_id))
    group = result.scalar_one_or_none()

    if not group or not group.region_id:
        await message.answer("⚠️ Guruh hududi sozlanmagan. Admin /admin buyrug'ini yuborsin.")
        return

    region_result = await db.execute(select(Region).where(Region.id == group.region_id))
    region = region_result.scalar_one_or_none()

    if not region or not region.latitude:
        await message.answer("⚠️ Hudud koordinatalari topilmadi.")
        return

    await message.answer("⏳ Namoz vaqtlari olinmoqda...")

    timings = await prayer_service.fetch_prayer_times(region.latitude, region.longitude)
    if not timings:
        await message.answer("❌ Namoz vaqtlarini olishda xatolik yuz berdi.")
        return

    region_name = f"{region.viloyat}, {region.tuman}"
    msg = prayer_service.format_prayer_message(timings, region_name)
    await message.answer(msg)


@router.message(Command("news"))
async def cmd_news(message: Message, db: AsyncSession):
    """Handle /news command."""
    if message.chat.type == "private":
        await message.answer("Bu buyruq faqat guruhlarda ishlaydi.")
        return

    await message.answer("⏳ Yangiliklar olinmoqda...")
    count = await news_service.send_news_to_group(
        message.chat.id, db, message.bot, gemini_service
    )
    if count == 0:
        await message.answer("📭 Hozircha yangi yangiliklar yo'q.")


@router.message(Command("jobs"))
async def cmd_jobs(message: Message, db: AsyncSession):
    """Handle /jobs command."""
    if message.chat.type == "private":
        await message.answer("Bu buyruq faqat guruhlarda ishlaydi.")
        return

    await message.answer("⏳ Ish e'lonlari olinmoqda...")
    count = await jobs_service.send_jobs_to_group(message.chat.id, db, message.bot)
    if count == 0:
        await message.answer("📭 Hozircha yangi ish e'lonlari yo'q.")


@router.message(Command("ai"))
async def cmd_ai(message: Message, db: AsyncSession):
    """Handle /ai command."""
    # Get question from message
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("❓ Savol kiriting: /ai [savol]")
        return

    question = args[1].strip()

    # Check if AI enabled for group
    if message.chat.type != "private":
        settings_result = await db.execute(
            select(GroupSettings).where(GroupSettings.group_id == message.chat.id)
        )
        group_settings = settings_result.scalar_one_or_none()
        if not group_settings or not group_settings.ai_enabled:
            await message.answer("❌ Bu guruhda AI yordamchi yoqilmagan.")
            return

    # Check rate limit (10 per hour)
    # This is handled by Redis in a real implementation
    await message.answer("⏳ Javob tayyorlanmoqda...")

    response = await gemini_service.generate_response(
        question, db,
        user_id=message.from_user.id,
        group_id=message.chat.id if message.chat.type != "private" else None
    )
    await message.answer(f"🤖 <b>AI Javob:</b>\n\n{response}")


@router.message(Command("subscribe"))
async def cmd_subscribe(message: Message, db: AsyncSession):
    """Handle /subscribe command - show subscription status."""
    if message.chat.type == "private":
        await message.answer("Bu buyruq faqat guruhlarda ishlaydi.")
        return

    from app.database.models import RequiredChannel
    result = await db.execute(
        select(RequiredChannel).where(
            RequiredChannel.group_id == message.chat.id,
            RequiredChannel.is_active == True
        )
    )
    channels = result.scalars().all()

    if not channels:
        await message.answer("✅ Bu guruhda majburiy obuna yo'q.")
        return

    text = "📢 <b>Majburiy obuna kanallari:</b>\n\n"
    for ch in channels:
        name = ch.channel_title or ch.channel_username or str(ch.channel_id)
        text += f"• {name}\n"

    await message.answer(text)
