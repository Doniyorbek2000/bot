"""Configuration management."""
import os
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings."""
    
    # Bot
    BOT_TOKEN: str = Field(..., env="BOT_TOKEN")
    SUPER_ADMIN_IDS: str = Field(..., env="SUPER_ADMIN_IDS")
    
    # Database
    DATABASE_URL: str = Field(..., env="DATABASE_URL")
    
    # Redis
    REDIS_URL: str = Field(..., env="REDIS_URL")
    
    # API Keys
    GEMINI_API_KEY: str = Field(default="", env="GEMINI_API_KEY")
    WEATHER_API_KEY: str = Field(default="", env="WEATHER_API_KEY")
    
    # Timezone
    TIMEZONE: str = Field(default="Asia/Tashkent", env="TIMEZONE")
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    
    # Service Type
    SERVICE_TYPE: str = Field(default="bot", env="SERVICE_TYPE")
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    @property
    def super_admin_ids_list(self) -> List[int]:
        """Parse super admin IDs from comma-separated string."""
        return [int(id.strip()) for id in self.SUPER_ADMIN_IDS.split(",") if id.strip()]
    
    @property
    def database_url_async(self) -> str:
        """Get async database URL."""
        if self.DATABASE_URL.startswith("sqlite"):
            return self.DATABASE_URL
        return self.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")


settings = Settings()
