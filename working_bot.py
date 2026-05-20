#!/usr/bin/env python3
"""Working bot with all handlers."""
import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from aiogram.enums import ParseMode

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

# Bot configuration
BOT_TOKEN = "8525111021:AAFUmLHZ3LZcHgw8pbbzIw6xRbYG35x2y1Q"
SUPER_ADMIN_ID = 8674220680

# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()


@dp.message(CommandStart())
async def cmd_start(message: Message):
    """Handle /start command."""
    logger.info(f"📨 /start from user {message.from_user.id}")
    
    user = message.from_user
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
    
    await message.answer(text)
    logger.info(f"✅ Sent /start response to {message.from_user.id}")


@dp.message(Command("help"))
async def cmd_help(message: Message):
    """Handle /help command."""
    logger.info(f"📨 /help from user {message.from_user.id}")
    
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

<b>Foydalanuvchilar uchun:</b>
/id — Sizning ID'ingiz"""
    
    await message.answer(text)
    logger.info(f"✅ Sent /help response to {message.from_user.id}")


@dp.message(Command("admin"))
async def cmd_admin(message: Message):
    """Handle /admin command."""
    logger.info(f"📨 /admin from user {message.from_user.id}")
    
    if message.from_user.id == SUPER_ADMIN_ID:
        text = """👨‍💼 <b>Admin Panel</b>

Siz super admin sifatida tizimga kirgansiz!

<b>Mavjud modullar:</b>
• Ob-havo moduli
• Namoz vaqtlari
• Yangiliklar
• Ish e'lonlari
• AI yordamchi
• Moderatsiya
• Obuna nazorati
• Taklif nazorati

Har bir modulni sozlash uchun guruhda /settings buyrug'ini ishlating."""
    else:
        text = "⛔ Bu buyruq faqat adminlar uchun!"
    
    await message.answer(text)
    logger.info(f"✅ Sent /admin response to {message.from_user.id}")


@dp.message(Command("id"))
async def cmd_id(message: Message):
    """Handle /id command."""
    logger.info(f"📨 /id from user {message.from_user.id}")
    
    text = f"""🆔 <b>Sizning ma'lumotlaringiz:</b>

👤 Ism: {message.from_user.full_name}
🆔 ID: <code>{message.from_user.id}</code>
📱 Username: @{message.from_user.username or 'yo\'q'}"""
    
    if message.chat.type != "private":
        text += f"\n\n💬 Guruh ID: <code>{message.chat.id}</code>"
        text += f"\n📝 Guruh nomi: {message.chat.title}"
    
    await message.answer(text)
    logger.info(f"✅ Sent /id response to {message.from_user.id}")


@dp.message(F.text)
async def echo_message(message: Message):
    """Echo all text messages."""
    logger.info(f"📨 Text message from {message.from_user.id}: {message.text[:50]}")
    
    # Don't echo in groups
    if message.chat.type == "private":
        await message.answer(f"Echo: {message.text}")
        logger.info(f"✅ Echoed message to {message.from_user.id}")


async def on_startup():
    """Actions on startup."""
    logger.info("=" * 60)
    logger.info("🚀 Bot starting...")
    logger.info(f"Bot token: {BOT_TOKEN[:20]}...")
    logger.info(f"Super admin ID: {SUPER_ADMIN_ID}")
    
    # Get bot info
    me = await bot.get_me()
    logger.info(f"✅ Bot connected: @{me.username} ({me.first_name})")
    logger.info("=" * 60)


async def on_shutdown():
    """Actions on shutdown."""
    logger.info("⛔ Bot shutting down...")
    await bot.session.close()


async def main():
    """Main function."""
    # Register startup/shutdown
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    
    # Start polling
    logger.info("🔄 Starting polling...")
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("⛔ Bot stopped by user")
