#!/usr/bin/env python3
"""Simple test bot to verify basic functionality."""
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.enums import ParseMode

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot token
BOT_TOKEN = "8525111021:AAFUmLHZ3LZcHgw8pbbzIw6xRbYG35x2y1Q"

# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """Handle /start command."""
    logger.info(f"Received /start from {message.from_user.id}")
    await message.answer(
        f"👋 Salom, {message.from_user.first_name}!\n\n"
        f"✅ Bot ishlayapti!\n"
        f"🆔 Sizning ID: {message.from_user.id}"
    )


@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    """Handle /help command."""
    logger.info(f"Received /help from {message.from_user.id}")
    await message.answer(
        "📋 Buyruqlar:\n"
        "/start - Botni ishga tushirish\n"
        "/help - Yordam"
    )


@dp.message()
async def echo(message: types.Message):
    """Echo all other messages."""
    logger.info(f"Received message from {message.from_user.id}: {message.text}")
    await message.answer(f"Echo: {message.text}")


async def main():
    """Start bot."""
    logger.info("Starting simple test bot...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
