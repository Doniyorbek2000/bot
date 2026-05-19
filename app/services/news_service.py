"""News service using RSS feeds."""
import hashlib
from typing import List, Dict, Any, Optional
import aiohttp
import feedparser
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database.models import Group, GroupSettings, NewsSource, SentPost, AdminLog, BannedWord
from app.utils.logger import logger
from app.utils.validators import sanitize_text, truncate_text


class NewsService:
    """Service for fetching and formatting news."""

    async def fetch_rss_feed(self, url: str) -> List[Dict[str, Any]]:
        """
        Fetch and parse RSS feed.

        Args:
            url: RSS feed URL

        Returns:
            List of news items
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url,
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
                    "summary": entry.get("summary", entry.get("description", "")),
                    "link": entry.get("link", ""),
                    "published": entry.get("published", ""),
                    "source": feed.feed.get("title", url),
                }
                # Strip HTML from summary
                item["summary"] = self._strip_html(item["summary"])
                items.append(item)
            return items

        except Exception as e:
            logger.error(f"RSS fetch error for {url}: {e}")
            return []

    def _strip_html(self, text: str) -> str:
        """Strip HTML tags from text."""
        import re
        clean = re.compile('<.*?>')
        return re.sub(clean, '', text).strip()

    def format_news_message(self, item: Dict[str, Any], summary: str = "") -> str:
        """
        Format a news item into a Telegram message.

        Args:
            item: News item dict
            summary: AI-generated summary (optional)

        Returns:
            Formatted message string
        """
        title = sanitize_text(item.get("title", ""))
        source = sanitize_text(item.get("source", ""))
        link = item.get("link", "")
        published = item.get("published", "")

        content = summary if summary else truncate_text(
            sanitize_text(item.get("summary", "")), 300
        )

        msg = f"""📰 <b>{title}</b>

{content}

🔗 <a href="{link}">To'liq o'qish</a>
📡 <i>Manba: {source}</i>"""

        if published:
            msg += f"\n🕐 <i>{published[:16]}</i>"

        return msg

    async def send_news_to_group(
        self,
        group_id: int,
        db: AsyncSession,
        bot=None,
        gemini_service=None
    ) -> int:
        """
        Fetch and send news to a group.

        Args:
            group_id: Telegram group ID
            db: Database session
            bot: Aiogram bot instance
            gemini_service: Gemini service instance

        Returns:
            Number of news items sent
        """
        sent_count = 0
        try:
            # Get group settings
            result = await db.execute(
                select(GroupSettings).where(GroupSettings.group_id == group_id)
            )
            settings = result.scalar_one_or_none()
            topics = settings.news_topics if settings and settings.news_topics else ["local"]

            # Get banned words for this group
            bw_result = await db.execute(
                select(BannedWord.word).where(
                    BannedWord.group_id == group_id,
                    BannedWord.is_active == True
                )
            )
            banned_words = [row[0].lower() for row in bw_result.fetchall()]

            # Get active news sources matching topics
            sources_result = await db.execute(
                select(NewsSource).where(
                    NewsSource.is_active == True,
                    NewsSource.topic.in_(topics)
                )
            )
            sources = sources_result.scalars().all()

            for source in sources:
                items = await self.fetch_rss_feed(source.url)
                for item in items:
                    # Check banned words
                    text_lower = (item["title"] + " " + item["summary"]).lower()
                    if any(bw in text_lower for bw in banned_words):
                        await self._log_skip(db, group_id, item["title"], "banned_word")
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

                    # AI summary if enabled
                    ai_summary = ""
                    if gemini_service and settings and settings.ai_enabled:
                        try:
                            ai_summary = await gemini_service.format_news_summary(
                                item["title"], item["summary"], db
                            )
                        except Exception:
                            pass

                    message = self.format_news_message(item, ai_summary)

                    if bot:
                        try:
                            await bot.send_message(
                                group_id, message,
                                parse_mode="HTML",
                                disable_web_page_preview=False
                            )
                        except Exception as e:
                            logger.error(f"Failed to send news to {group_id}: {e}")
                            continue

                    # Record sent post
                    sent_post = SentPost(
                        group_id=group_id,
                        post_type="news",
                        content_hash=content_hash,
                        source_url=item["link"]
                    )
                    db.add(sent_post)
                    await db.commit()
                    sent_count += 1

                    # Max 3 news per run to avoid spam
                    if sent_count >= 3:
                        return sent_count

        except Exception as e:
            logger.error(f"Error sending news to group {group_id}: {e}")
            await self._log_error(db, group_id, str(e))

        return sent_count

    async def _log_skip(self, db: AsyncSession, group_id: int, title: str, reason: str):
        """Log skipped news item."""
        try:
            log = AdminLog(
                group_id=group_id,
                action=f"news_skip_{reason}",
                details=title[:200],
                level="info"
            )
            db.add(log)
            await db.commit()
        except Exception:
            pass

    async def _log_error(self, db: AsyncSession, group_id: int, error: str):
        """Log error to admin_logs."""
        try:
            log = AdminLog(
                group_id=group_id,
                action="news_error",
                details=error,
                level="error"
            )
            db.add(log)
            await db.commit()
        except Exception:
            pass
