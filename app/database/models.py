"""SQLAlchemy ORM models."""
from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    BigInteger, Boolean, DateTime, Float, ForeignKey,
    Integer, String, Text, UniqueConstraint, Index
)
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    """Base model class."""
    pass


class Region(Base):
    """Geographic region model."""
    __tablename__ = "regions"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    viloyat: Mapped[str] = mapped_column(String(100), nullable=False)
    tuman: Mapped[str] = mapped_column(String(100), nullable=False)
    latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    timezone: Mapped[str] = mapped_column(String(50), default="Asia/Tashkent")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        UniqueConstraint("viloyat", "tuman", name="uq_region_viloyat_tuman"),
    )


class User(Base):
    """Telegram user model."""
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    username: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    full_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_blocked: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        Index("ix_users_telegram_id", "telegram_id"),
    )


class Group(Base):
    """Telegram group/channel model."""
    __tablename__ = "groups"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    username: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    chat_type: Mapped[str] = mapped_column(String(20), default="group")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_blocked: Mapped[bool] = mapped_column(Boolean, default=False)
    region_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("regions.id", ondelete="SET NULL"), nullable=True)
    added_by: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    region: Mapped[Optional["Region"]] = relationship("Region", lazy="select")
    settings: Mapped[Optional["GroupSettings"]] = relationship("GroupSettings", back_populates="group", uselist=False)
    
    __table_args__ = (
        Index("ix_groups_telegram_id", "telegram_id"),
    )


class GroupSettings(Base):
    """Group settings model."""
    __tablename__ = "group_settings"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    group_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("groups.telegram_id", ondelete="CASCADE"), unique=True)
    weather_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    prayer_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    news_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    jobs_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    ai_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    subscription_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    invite_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    moderation_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    news_topics: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), nullable=True)
    ban_penalty: Mapped[str] = mapped_column(String(20), default="warn")
    invite_threshold: Mapped[int] = mapped_column(Integer, default=3)
    language: Mapped[str] = mapped_column(String(10), default="uz")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    group: Mapped["Group"] = relationship("Group", back_populates="settings")


class WeatherSchedule(Base):
    """Weather posting schedule model."""
    __tablename__ = "weather_schedules"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    group_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("groups.telegram_id", ondelete="CASCADE"))
    schedule_time: Mapped[str] = mapped_column(String(5), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class PrayerSchedule(Base):
    """Prayer times posting schedule model."""
    __tablename__ = "prayer_schedules"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    group_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("groups.telegram_id", ondelete="CASCADE"))
    schedule_time: Mapped[str] = mapped_column(String(5), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class NewsSource(Base):
    """News source model."""
    __tablename__ = "news_sources"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    url: Mapped[str] = mapped_column(String(500), unique=True, nullable=False)
    source_type: Mapped[str] = mapped_column(String(20), default="rss")
    topic: Mapped[str] = mapped_column(String(50), default="local")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class JobSource(Base):
    """Job listing source model."""
    __tablename__ = "job_sources"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    url: Mapped[str] = mapped_column(String(500), unique=True, nullable=False)
    source_type: Mapped[str] = mapped_column(String(20), default="rss")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class SentPost(Base):
    """Sent post tracking model."""
    __tablename__ = "sent_posts"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    group_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    post_type: Mapped[str] = mapped_column(String(20), nullable=False)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    source_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        Index("ix_sent_posts_group_hash", "group_id", "content_hash"),
    )


class RequiredChannel(Base):
    """Required subscription channel model."""
    __tablename__ = "required_channels"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    group_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("groups.telegram_id", ondelete="CASCADE"))
    channel_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    channel_username: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    channel_title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    invite_link: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    is_global: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class UserSubscription(Base):
    """User subscription status model."""
    __tablename__ = "user_subscriptions"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    group_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    is_subscribed: Mapped[bool] = mapped_column(Boolean, default=False)
    checked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        UniqueConstraint("user_id", "group_id", name="uq_user_group_subscription"),
    )


class InviteTracking(Base):
    """Invite tracking model."""
    __tablename__ = "invite_tracking"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    inviter_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    invited_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    group_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    is_valid: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        UniqueConstraint("inviter_id", "invited_id", "group_id", name="uq_invite_tracking"),
        Index("ix_invite_tracking_inviter_group", "inviter_id", "group_id"),
    )


class BannedWord(Base):
    """Banned word model."""
    __tablename__ = "banned_words"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    group_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("groups.telegram_id", ondelete="CASCADE"))
    word: Mapped[str] = mapped_column(String(200), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    added_by: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        UniqueConstraint("group_id", "word", name="uq_banned_word_group"),
    )


class Warning(Base):
    """User warning model."""
    __tablename__ = "warnings"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    group_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    reason: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    warned_by: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        Index("ix_warnings_user_group", "user_id", "group_id"),
    )


class AILog(Base):
    """AI request/response log model."""
    __tablename__ = "ai_logs"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    group_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    input_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    response_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    input_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    response_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="success")
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class AdminLog(Base):
    """Admin action log model."""
    __tablename__ = "admin_logs"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    admin_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    group_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    level: Mapped[str] = mapped_column(String(20), default="info")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        Index("ix_admin_logs_level", "level"),
        Index("ix_admin_logs_created_at", "created_at"),
    )


class GlobalSettings(Base):
    """Global settings model."""
    __tablename__ = "global_settings"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    key: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class ScheduledPost(Base):
    """Scheduled advertisement post model."""
    __tablename__ = "scheduled_posts"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    group_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("groups.telegram_id", ondelete="CASCADE"))
    content: Mapped[str] = mapped_column(Text, nullable=False)
    media_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    scheduled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_sent: Mapped[bool] = mapped_column(Boolean, default=False)
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_by: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
