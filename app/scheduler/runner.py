"""Scheduler runner using APScheduler."""
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz
import redis.asyncio as aioredis
from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.utils.config import settings
from app.utils.logger import logger
from app.scheduler.tasks import (
    run_weather_task,
    run_prayer_task,
    run_news_task,
    run_jobs_task,
)


async def main():
    """Main scheduler function."""
    logger.info("Scheduler starting...")

    # Initialize bot
    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    # Initialize Redis
    try:
        redis_client = aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )
        await redis_client.ping()
        logger.info("Scheduler Redis connected")
    except Exception as e:
        logger.error(f"Scheduler Redis connection failed: {e}")
        redis_client = None

    # Initialize scheduler
    tz = pytz.timezone(settings.TIMEZONE)
    scheduler = AsyncIOScheduler(timezone=tz)

    # Run weather and prayer tasks every minute (they check their own schedules)
    scheduler.add_job(
        run_weather_task,
        CronTrigger(minute="*", timezone=tz),
        args=[bot, redis_client],
        id="weather_task",
        replace_existing=True,
        max_instances=1
    )

    scheduler.add_job(
        run_prayer_task,
        CronTrigger(minute="*", timezone=tz),
        args=[bot, redis_client],
        id="prayer_task",
        replace_existing=True,
        max_instances=1
    )

    # Run news task every 2 hours
    scheduler.add_job(
        run_news_task,
        CronTrigger(minute=0, hour="*/2", timezone=tz),
        args=[bot],
        id="news_task",
        replace_existing=True,
        max_instances=1
    )

    # Run jobs task every 4 hours
    scheduler.add_job(
        run_jobs_task,
        CronTrigger(minute=0, hour="*/4", timezone=tz),
        args=[bot],
        id="jobs_task",
        replace_existing=True,
        max_instances=1
    )

    scheduler.start()
    logger.info("Scheduler started. Running tasks...")

    try:
        # Keep running
        while True:
            await asyncio.sleep(60)
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler stopping...")
        scheduler.shutdown()
        await bot.session.close()
        if redis_client:
            await redis_client.close()
        logger.info("Scheduler stopped")


if __name__ == "__main__":
    asyncio.run(main())
