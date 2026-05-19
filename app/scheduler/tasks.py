"""Scheduled tasks for weather, prayer, news, jobs."""
import asyncio
from datetime import datetime
from aiogram import Bot
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import redis.asyncio as aioredis

from app.database.models import Group, GroupSettings, WeatherSchedule, PrayerSchedule
from app.database.session import AsyncSessionLocal
from app.services.weather_service import WeatherService
from app.services.prayer_service import PrayerService
from app.services.news_service import NewsService
from app.services.jobs_service import JobsService
from app.services.gemini_service import GeminiService
from app.utils.config import settings
from app.utils.logger import logger


async def run_weather_task(bot: Bot, redis_client):
    """Run weather posting task for all scheduled groups."""
    logger.info("Running weather task...")
    weather_service = WeatherService()
    gemini_service = GeminiService()

    async with AsyncSessionLocal() as db:
        try:
            # Get all active weather schedules
            current_time = datetime.now().strftime("%H:%M")
            result = await db.execute(
                select(WeatherSchedule).where(
                    WeatherSchedule.is_active == True,
                    WeatherSchedule.schedule_time == current_time
                )
            )
            schedules = result.scalars().all()

            for schedule in schedules:
                # Check if group is active
                group_result = await db.execute(
                    select(Group).where(
                        Group.telegram_id == schedule.group_id,
                        Group.is_active == True,
                        Group.is_blocked == False
                    )
                )
                group = group_result.scalar_one_or_none()
                if not group:
                    continue

                # Check if weather module is enabled
                settings_result = await db.execute(
                    select(GroupSettings).where(GroupSettings.group_id == schedule.group_id)
                )
                group_settings = settings_result.scalar_one_or_none()
                if not group_settings or not group_settings.weather_enabled:
                    continue

                # Send weather
                try:
                    await weather_service.send_weather_to_group(
                        schedule.group_id, db, bot, gemini_service
                    )
                    logger.info(f"Weather sent to group {schedule.group_id}")
                except Exception as e:
                    logger.error(f"Failed to send weather to {schedule.group_id}: {e}")

            await db.commit()
        except Exception as e:
            logger.error(f"Weather task error: {e}")
            await db.rollback()


async def run_prayer_task(bot: Bot, redis_client):
    """Run prayer times posting task for all scheduled groups."""
    logger.info("Running prayer task...")
    prayer_service = PrayerService()

    async with AsyncSessionLocal() as db:
        try:
            current_time = datetime.now().strftime("%H:%M")
            result = await db.execute(
                select(PrayerSchedule).where(
                    PrayerSchedule.is_active == True,
                    PrayerSchedule.schedule_time == current_time
                )
            )
            schedules = result.scalars().all()

            for schedule in schedules:
                group_result = await db.execute(
                    select(Group).where(
                        Group.telegram_id == schedule.group_id,
                        Group.is_active == True,
                        Group.is_blocked == False
                    )
                )
                group = group_result.scalar_one_or_none()
                if not group:
                    continue

                settings_result = await db.execute(
                    select(GroupSettings).where(GroupSettings.group_id == schedule.group_id)
                )
                group_settings = settings_result.scalar_one_or_none()
                if not group_settings or not group_settings.prayer_enabled:
                    continue

                try:
                    await prayer_service.send_prayer_to_group(
                        schedule.group_id, db, redis_client, bot
                    )
                    logger.info(f"Prayer times sent to group {schedule.group_id}")
                except Exception as e:
                    logger.error(f"Failed to send prayer to {schedule.group_id}: {e}")

            await db.commit()
        except Exception as e:
            logger.error(f"Prayer task error: {e}")
            await db.rollback()


async def run_news_task(bot: Bot):
    """Run news posting task for all groups with news enabled."""
    logger.info("Running news task...")
    news_service = NewsService()
    gemini_service = GeminiService()

    async with AsyncSessionLocal() as db:
        try:
            result = await db.execute(
                select(Group).where(
                    Group.is_active == True,
                    Group.is_blocked == False
                )
            )
            groups = result.scalars().all()

            for group in groups:
                settings_result = await db.execute(
                    select(GroupSettings).where(GroupSettings.group_id == group.telegram_id)
                )
                group_settings = settings_result.scalar_one_or_none()
                if not group_settings or not group_settings.news_enabled:
                    continue

                try:
                    count = await news_service.send_news_to_group(
                        group.telegram_id, db, bot, gemini_service
                    )
                    if count > 0:
                        logger.info(f"Sent {count} news to group {group.telegram_id}")
                except Exception as e:
                    logger.error(f"Failed to send news to {group.telegram_id}: {e}")

            await db.commit()
        except Exception as e:
            logger.error(f"News task error: {e}")
            await db.rollback()


async def run_jobs_task(bot: Bot):
    """Run jobs posting task for all groups with jobs enabled."""
    logger.info("Running jobs task...")
    jobs_service = JobsService()

    async with AsyncSessionLocal() as db:
        try:
            result = await db.execute(
                select(Group).where(
                    Group.is_active == True,
                    Group.is_blocked == False
                )
            )
            groups = result.scalars().all()

            for group in groups:
                settings_result = await db.execute(
                    select(GroupSettings).where(GroupSettings.group_id == group.telegram_id)
                )
                group_settings = settings_result.scalar_one_or_none()
                if not group_settings or not group_settings.jobs_enabled:
                    continue

                try:
                    count = await jobs_service.send_jobs_to_group(
                        group.telegram_id, db, bot
                    )
                    if count > 0:
                        logger.info(f"Sent {count} jobs to group {group.telegram_id}")
                except Exception as e:
                    logger.error(f"Failed to send jobs to {group.telegram_id}: {e}")

            await db.commit()
        except Exception as e:
            logger.error(f"Jobs task error: {e}")
            await db.rollback()
