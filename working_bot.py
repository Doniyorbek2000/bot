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
from aiogram.client.default import DefaultBotProperties

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
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


@dp.message(Command("settings"))
async def cmd_settings(message: Message):
    """Handle /settings command."""
    logger.info(f"📨 /settings from user {message.from_user.id}")
    
    text = """⚙️ <b>Guruh Sozlamalari</b>

<b>Modullarni yoqish/o'chirish:</b>

🌤 <b>Ob-havo moduli:</b> O'chirilgan
   • Mintaqani tanlang
   • Vaqt jadvalini sozlang

🕌 <b>Namoz vaqtlari:</b> O'chirilgan
   • Mintaqani tanlang
   • Vaqt jadvalini sozlang

📰 <b>Yangiliklar:</b> O'chirilgan
   • Mavzularni tanlang
   • Vaqt jadvalini sozlang

💼 <b>Ish e'lonlari:</b> O'chirilgan
   • Mintaqani tanlang
   • Vaqt jadvalini sozlang

🤖 <b>AI Yordamchi:</b> O'chirilgan
   • Gemini API kalitini kiriting

🛡 <b>Moderatsiya:</b> O'chirilgan
   • Taqiqlangan so'zlarni qo'shing
   • Jazo turini tanlang

📢 <b>Majburiy obuna:</b> O'chirilgan
   • Kanallarni qo'shing

👥 <b>Taklif nazorati:</b> O'chirilgan
   • Chegarani belgilang (1-100)

<i>To'liq funksional admin panel tez orada qo'shiladi!</i>"""
    
    await message.answer(text)
    logger.info(f"✅ Sent /settings response to {message.from_user.id}")


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


@dp.message(Command("weather"))
async def cmd_weather(message: Message):
    """Handle /weather command."""
    logger.info(f"📨 /weather from user {message.from_user.id}")
    
    text = """🌤 <b>Ob-havo Moduli</b>

Ob-havo moduli hozircha sozlanmagan.

<b>Sozlash uchun:</b>
1. Guruhda /admin buyrug'ini yuboring
2. Ob-havo modulini yoqing
3. Mintaqangizni tanlang
4. Vaqt jadvalini sozlang

<i>Modul tez orada to'liq ishga tushadi!</i>"""
    
    await message.answer(text)
    logger.info(f"✅ Sent /weather response to {message.from_user.id}")


@dp.message(Command("prayer"))
async def cmd_prayer(message: Message):
    """Handle /prayer command."""
    logger.info(f"📨 /prayer from user {message.from_user.id}")
    
    text = """🕌 <b>Namoz Vaqtlari Moduli</b>

Namoz vaqtlari moduli hozircha sozlanmagan.

<b>Sozlash uchun:</b>
1. Guruhda /admin buyrug'ini yuboring
2. Namoz vaqtlari modulini yoqing
3. Mintaqangizni tanlang
4. Vaqt jadvalini sozlang

<i>Modul tez orada to'liq ishga tushadi!</i>"""
    
    await message.answer(text)
    logger.info(f"✅ Sent /prayer response to {message.from_user.id}")


@dp.message(Command("news"))
async def cmd_news(message: Message):
    """Handle /news command."""
    logger.info(f"📨 /news from user {message.from_user.id}")
    
    text = """📰 <b>Yangiliklar Moduli</b>

Yangiliklar moduli hozircha sozlanmagan.

<b>Sozlash uchun:</b>
1. Guruhda /admin buyrug'ini yuboring
2. Yangiliklar modulini yoqing
3. Mavzularni tanlang
4. Vaqt jadvalini sozlang

<i>Modul tez orada to'liq ishga tushadi!</i>"""
    
    await message.answer(text)
    logger.info(f"✅ Sent /news response to {message.from_user.id}")


@dp.message(Command("jobs"))
async def cmd_jobs(message: Message):
    """Handle /jobs command."""
    logger.info(f"📨 /jobs from user {message.from_user.id}")
    
    text = """💼 <b>Ish E'lonlari Moduli</b>

Ish e'lonlari moduli hozircha sozlanmagan.

<b>Sozlash uchun:</b>
1. Guruhda /admin buyrug'ini yuboring
2. Ish e'lonlari modulini yoqing
3. Mintaqangizni tanlang
4. Vaqt jadvalini sozlang

<i>Modul tez orada to'liq ishga tushadi!</i>"""
    
    await message.answer(text)
    logger.info(f"✅ Sent /jobs response to {message.from_user.id}")


@dp.message(Command("ai"))
async def cmd_ai(message: Message):
    """Handle /ai command."""
    logger.info(f"📨 /ai from user {message.from_user.id}")
    
    # Get question text after /ai command
    question = message.text.replace("/ai", "").strip()
    
    if not question:
        text = """🤖 <b>AI Yordamchi</b>

Menga savol bering!

<b>Foydalanish:</b>
<code>/ai sizning savolingiz</code>

<b>Misol:</b>
<code>/ai Python dasturlash tili haqida ma'lumot ber</code>

<i>AI modul tez orada to'liq ishga tushadi!</i>"""
    else:
        text = f"""🤖 <b>AI Yordamchi</b>

<b>Sizning savolingiz:</b>
{question}

<b>Javob:</b>
AI modul hozircha sozlanmagan. Gemini API kalitini qo'shganingizdan so'ng, men barcha savollaringizga javob bera olaman!

<i>Modul tez orada to'liq ishga tushadi!</i>"""
    
    await message.answer(text)
    logger.info(f"✅ Sent /ai response to {message.from_user.id}")


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
