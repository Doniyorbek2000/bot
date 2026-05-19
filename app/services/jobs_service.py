"""Jobs service for fetching job listings."""
import hashlib
from typing import List, Dict, Any
import aiohttp
import feedparser
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database.models import Group, Region, JobSource, SentPost, AdminLog, BannedWord
from app.utils.logger import logger
from app.utils.validators import sanitize_text, truncate_text


class JobsService:
    """Service for fetching and formatting job listings."""

    async def fetch_job_feed(self, url: str, region_name: str = "") -> List[Dict[str, Any]]:
        """
        Fetch job listings from RSS or API.

        Args:
            url: Job feed URL
            region_name: Region name for filtering

        Returns:
            List of job items
        """
        try:
            # Add region to search if URL supports it
            search_url = url
            if region_name and "?" in url:
                search_url = f"{url}&text={region_name}"

            async with aiohttp.ClientSession() as session:
                async with session.get(
                    search_url,
                    timeout=aiohttp.ClientTimeout(total=15),
                    headers={"User-Agent": "HududAgentBot/1.0"}
                ) as response:
                    if response.status != 200:
                        return []
                    content = await response.text()

            feed = feedparser.parse(content)
            items = []
            for entry in feed.entries[:10]:
                item = {
                    "title": entry.get("title", ""),
                    "description": entry.get("summary", entry.get("description", "")),
                    "link": entry.get("link", ""),
                    "company": entry.get("author", ""),
                    "location": "",
                    "salary": "",
                    "source": feed.feed.get("title", url),
                }
                # Strip HTML
                item["description"] = self._strip_html(item["description"])
                # Try to extract location and salary from description
                self._extract_job_details(item)
                items.append(item)
            return items

        except Exception as e:
            logger.error(f"Job feed fetch error for {url}: {e}")
            return []

    def _strip_html(self, text: str) -> str:
        """Strip HTML tags from text."""
        import re
        clean = re.compile('<.*?>')
        return re.sub(clean, '', text).strip()

    def _extract_job_details(self, item: Dict[str, Any]):
        """Extract location and salary from job description."""
        desc = item["description"].lower()
        # Simple extraction - can be improved
        if "toshkent" in desc:
            item["location"] = "Toshkent"
        elif "samarqand" in desc:
            item["location"] = "Samarqand"
        # Add more regions as needed

    def format_job_message(self, item: Dict[str, Any]) -> str:
        """
        Format a job listing into a Telegram message.

        Args:
            item: Job item dict

        Returns:
            Formatted message string
        """
        title = sanitize_text(item.get("title", ""))
        company = sanitize_text(item.get("company", "Noma'lum"))
        location = sanitize_text(item.get("location", ""))
        salary = sanitize_text(item.get("salary", ""))
        description = truncate_text(sanitize_text(item.get("description", "")), 200)
        link = item.get("link", "")
        source = sanitize_text(item.get("source", ""))

        msg = f"""💼 <b>{title}</b>

🏢 Kompaniya: <b>{company}</b>"""

        if location:
            msg += f"\n📍 Joylashuv: <b>{location}</b>"
        if salary:
            msg += f"\n💰 Maosh: <b>{salary}</b>"

        msg += f"\n\n{description}"
        msg += f"\n\n🔗 <a href=\"{link}\">Batafsil ma'lumot</a>"
        msg += f"\n📡 <i>Manba: {source}</i>"

        return msg

    async def send_jobs_to_group(
        self,
        group_id: int,
        db: AsyncSession,
        bot=None
    ) -> int:
        """
        Fetch and send job listings to a group.

        Args:
            group_id: Telegram group ID
            db: Database session
            bot: Aiogram bot instance

        Returns:
            Number of jobs sent
        """
        sent_count = 0
        try:
            # Get group region
            result = await db.execute(
                select(Group).where(Group.telegram_id == group_id)
            )
            group = result.scalar_one_or_none()
            region_name = ""
            if group and group.region_id:
                region_result = await db.execute(
                    select(Region).where(Region.id == group.region_id)
                )
                region = region_result.scalar_one_or_none()
                if region:
                    region_name = f"{region.viloyat} {region.tuman}"

            # Get banned words
            bw_result = await db.execute(
                select(BannedWord.word).where(
                    BannedWord.group_id == group_id,
                    BannedWord.is_active == True
                )
            )
            banned_words = [row[0].lower() for row in bw_result.fetchall()]

            # Get active job sources
            sources_result = await db.execute(
                select(JobSource).where(JobSource.is_active == True)
            )
            sources = sources_result.scalars().all()

            for source in sources:
                items = await self.fetch_job_feed(source.url, region_name)
                for item in items:
                    # Check banned words
                    text_lower = (item["title"] + " " + item["description"]).lower()
                    if any(bw in text_lower for bw in banned_words):
                        continue

                    # Check duplicate
                    content_hash = hashlib.sha256(
                        (item["title"] + item["link"]).encode()
                    ).hexdigest()

                    existing = await db.execute(
                        select(SentPost).where(
                            SentPost.group_id == group_id,
                            SentPost.content_hash == content_hash
                        )
                    )
                    if existing.scalar_one_or_none():
                        continue

                    message = self.format_job_message(item)

                    if bot:
                        try:
                            await bot.send_message(
                                group_id, message,
                                parse_mode="HTML",
                                disable_web_page_preview=False
                            )
                        except Exception as e:
                            logger.error(f"Failed to send job to {group_id}: {e}")
                            continue

                    # Record sent post
                    sent_post = SentPost(
                        group_id=group_id,
                        post_type="job",
                        content_hash=content_hash,
                        source_url=item["link"]
                    )
                    db.add(sent_post)
                    await db.commit()
                    sent_count += 1

                    # Max 3 jobs per run
                    if sent_count >= 3:
                        return sent_count

        except Exception as e:
            logger.error(f"Error sending jobs to group {group_id}: {e}")
            await self._log_error(db, group_id, str(e))

        return sent_count

    async def _log_error(self, db: AsyncSession, group_id: int, error: str):
        """Log error to admin_logs."""
        try:
            log = AdminLog(
                group_id=group_id,
                action="jobs_error",
                details=error,
                level="error"
            )
            db.add(log)
            await db.commit()
        except Exception:
            pass
