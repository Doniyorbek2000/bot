"""Main bot application."""
import asyncio
import sys
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
import redis.asyncio as aioredis

from app.utils.config import settings
from app.utils.logger import logger
from app.database.session import check_db_connection, close_db
from app.bot.handlers import common, admin, user_commands, group_events
from app.bot.middlewares.database import DatabaseMiddleware
from app.bot.middlewares.rate_limit import RateLimitMiddleware
from app.bot.middlewares.redis_middleware import RedisMiddleware


async def on_startup(bot: Bot):
    """Actions on bot startup."""
    logger.info("Bot starting up...")
    
    # Check database connection
    try:
        await check_db_connection()
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        sys.exit(1)
    
    # Run migrations
    try:
        from alembic.config import Config
        from alembic import command
        alembic_cfg = Config("alembic.ini")
        command.upgrade(alembic_cfg, "head")
        logger.info("Database migrations applied")
    except Exception as e:
        logger.warning(f"Migration error (may be already applied): {e}")
    
    logger.info("Bot started successfully")


async def on_shutdown(bot: Bot):
    """Actions on bot shutdown."""
    logger.info("Bot shutting down...")
    await close_db()
    logger.info("Bot stopped")


async def main():
    """Main bot function."""
    # Initialize bot
    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    
    # Initialize dispatcher
    dp = Dispatcher()
    
    # Initialize Redis
    try:
        redis_client = aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )
        await redis_client.ping()
        logger.info("Redis connected")
    except Exception as e:
        logger.error(f"Redis connection failed: {e}")
        redis_client = None
    
    # Add middlewares
    dp.update.middleware(DatabaseMiddleware())
    dp.message.middleware(RateLimitMiddleware(redis_client))
    dp.update.middleware(RedisMiddleware(redis_client))
    
    # Store redis in dispatcher data
    dp["redis"] = redis_client
    
    # Register handlers
    dp.include_router(common.router)
    dp.include_router(admin.router)
    dp.include_router(user_commands.router)
    dp.include_router(group_events.router)
    
    # Startup/shutdown
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    
    # Start polling
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()
        if redis_client:
            await redis_client.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
