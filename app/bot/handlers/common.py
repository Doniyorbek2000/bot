"""Common handlers: /start, /help."""
from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database.models import User, Group
from app.utils.config import settings
from app.utils.logger import logger

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, db: AsyncSession):
    """Handle /start command."""
    user = message.from_user

    # Register or update user
    result = await db.execute(
        select(User).where(User.telegram_id == user.id)
    )
    db_user = result.scalar_one_or_none()
    if not db_user:
        db_user = User(
            telegram_id=user.id,
            username=user.username,
            full_name=user.full_name
        )
        db.add(db_user)
        await db.commit()

    if message.chat.type == "private":
        text = f"""👋 <b>Assalomu alaykum, {user.first_name}!</b>

🤖 <b>Hududiy Agent Bot</b>ga xush kelibsiz!

Bu bot guruh va kanallar uchun mo'ljallangan professional avtomatlashtirish botidir.

<b>Bot imkoniyatlari:</b>
🌤 Ob-havo ma'lumotlari
🕌 Namoz vaqtlari
📰 Yangiliklar
💼 Ish e'lonlari
🤖 Gemini AI yordamchi
🛡 Guruh moderatsiyasi
📢 Majburiy obuna
👥 Odam qo'shish sharti

<b>Botni guruhingizga qo'shing va /admin buyrug'ini yuboring!</b>

📋 Barcha buyruqlar: /help"""
    else:
        text = f"""👋 <b>Hududiy Agent Bot</b> guruhga qo'shildi!

Guruh adminlari /admin buyrug'i orqali botni sozlashlari mumkin."""

    await message.answer(text)


@router.message(Command("help"))
async def cmd_help(message: Message):
    """Handle /help command."""
    text = """📋 <b>Bot buyruqlari:</b>

<b>Umumiy:</b>
/start — Botni ishga tushirish
/help — Yordam

<b>Ma'lumotlar:</b>
/weather — Ob-havo
/prayer — Namoz vaqtlari
/news — Yangiliklar
/jobs — Ish e'lonlari
/ai [savol] — AI yordamchi

<b>Adminlar uchun:</b>
/admin — Guruh admin paneli
/settings — Guruh sozlamalari
/banwords — Taqiqlangan so'zlar
/stats — Statistika

<b>Super Admin:</b>
/superadmin — Super admin paneli

<b>Foydalanuvchilar uchun:</b>
/subscribe — Obuna holati"""

    await message.answer(text)
