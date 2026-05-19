"""Prayer times service using Aladhan API."""
import hashlib
import json
from datetime import date
from typing import Optional, Dict, Any
import aiohttp
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database.models import Group, Region, SentPost, AdminLog
from app.utils.logger import logger
from app.utils.validators import sanitize_text


class PrayerService:
    """Service for fetching and formatting prayer times."""

    BASE_URL = "https://api.aladhan.com/v1/timingsByCity"
    BASE_URL_COORDS = "https://api.aladhan.com/v1/timings"

    async def fetch_prayer_times(
        self,
        latitude: float,
        longitude: float,
        prayer_date: Optional[date] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Fetch prayer times from Aladhan API.

        Args:
            latitude: Location latitude
            longitude: Location longitude
            prayer_date: Date for prayer times (default: today)

        Returns:
            Prayer times dict or None on error
        """
        if prayer_date is None:
            prayer_date = date.today()

        date_str = prayer_date.strftime("%d-%m-%Y")
        url = f"{self.BASE_URL_COORDS}/{date_str}"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "method": 3,  # Muslim World League
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url,
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("code") == 200:
                            return self._parse_timings(data["data"]["timings"])
                    logger.error(f"Aladhan API error: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Prayer fetch error: {e}")
            return None

    def _parse_timings(self, timings: dict) -> Dict[str, str]:
        """Parse Aladhan timings response."""
        return {
            "Bomdod": timings.get("Fajr", ""),
            "Quyosh": timings.get("Sunrise", ""),
            "Peshin": timings.get("Dhuhr", ""),
            "Asr": timings.get("Asr", ""),
            "Shom": timings.get("Maghrib", ""),
            "Xufton": timings.get("Isha", ""),
        }

    def format_prayer_message(
        self,
        timings: Dict[str, str],
        region_name: str,
        prayer_date: Optional[date] = None
    ) -> str:
        """
        Format prayer times into a Telegram message.

        Args:
            timings: Prayer times dict
            region_name: Region name
            prayer_date: Date for the prayer times

        Returns:
            Formatted message string
        """
        if prayer_date is None:
            prayer_date = date.today()

        date_str = prayer_date.strftime("%d.%m.%Y")

        msg = f"""🕌 <b>{sanitize_text(region_name)}</b> — Namoz Vaqtlari
📅 <b>{date_str}</b>

🌅 Bomdod:  <b>{timings.get('Bomdod', '—')}</b>
☀️ Quyosh:  <b>{timings.get('Quyosh', '—')}</b>
🌞 Peshin:  <b>{timings.get('Peshin', '—')}</b>
🌇 Asr:     <b>{timings.get('Asr', '—')}</b>
🌆 Shom:    <b>{timings.get('Shom', '—')}</b>
🌙 Xufton:  <b>{timings.get('Xufton', '—')}</b>

📡 <i>Manba: Aladhan API</i>"""
        return msg

    async def send_prayer_to_group(
        self,
        group_id: int,
        db: AsyncSession,
        redis_client=None,
        bot=None
    ) -> bool:
        """
        Fetch and send prayer times to a group.

        Args:
            group_id: Telegram group ID
            db: Database session
            redis_client: Redis client for caching
            bot: Aiogram bot instance

        Returns:
            True if sent successfully
        """
        try:
            result = await db.execute(
                select(Group).where(Group.telegram_id == group_id)
            )
            group = result.scalar_one_or_none()
            if not group or not group.region_id:
                return False

            result = await db.execute(
                select(Region).where(Region.id == group.region_id)
            )
            region = result.scalar_one_or_none()
            if not region or not region.latitude:
                return False

            today = date.today()
            cache_key = f"prayer:{region.id}:{today.isoformat()}"

            timings = None

            # Try Redis cache first
            if redis_client:
                try:
                    cached = await redis_client.get(cache_key)
                    if cached:
                        timings = json.loads(cached)
                except Exception:
                    pass

            if not timings:
                timings = await self.fetch_prayer_times(region.latitude, region.longitude, today)
                if not timings:
                    await self._log_error(db, group_id, "Aladhan API returned no data")
                    return False
                # Cache for 24 hours
                if redis_client:
                    try:
                        await redis_client.setex(cache_key, 86400, json.dumps(timings))
                    except Exception:
                        pass

            # Check duplicate
            content_hash = hashlib.sha256(
                f"prayer_{group_id}_{today.isoformat()}".encode()
            ).hexdigest()

            existing = await db.execute(
                select(SentPost).where(
                    SentPost.group_id == group_id,
                    SentPost.content_hash == content_hash
                )
            )
            if existing.scalar_one_or_none():
                return True

            region_name = f"{region.viloyat}, {region.tuman}"
            message = self.format_prayer_message(timings, region_name, today)

            if bot:
                await bot.send_message(group_id, message, parse_mode="HTML")

            sent_post = SentPost(
                group_id=group_id,
                post_type="prayer",
                content_hash=content_hash
            )
            db.add(sent_post)
            await db.commit()
            return True

        except Exception as e:
            logger.error(f"Error sending prayer to group {group_id}: {e}")
            await self._log_error(db, group_id, str(e))
            return False

    async def _log_error(self, db: AsyncSession, group_id: int, error: str):
        """Log error to admin_logs."""
        try:
            log = AdminLog(
                group_id=group_id,
                action="prayer_error",
                details=error,
                level="error"
            )
            db.add(log)
            await db.commit()
        except Exception:
            pass
