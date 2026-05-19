"""Weather service using OpenWeatherMap API."""
import hashlib
from typing import Optional, Dict, Any
import aiohttp
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database.models import Group, Region, SentPost, AdminLog, GlobalSettings
from app.utils.config import settings
from app.utils.logger import logger
from app.utils.validators import sanitize_text


WEATHER_ICONS = {
    "Clear": "☀️",
    "Clouds": "☁️",
    "Rain": "🌧️",
    "Drizzle": "🌦️",
    "Thunderstorm": "⛈️",
    "Snow": "❄️",
    "Mist": "🌫️",
    "Fog": "🌫️",
    "Haze": "🌫️",
}


class WeatherService:
    """Service for fetching and formatting weather data."""
    
    BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
    
    def __init__(self):
        """Initialize weather service."""
        self.api_key = settings.WEATHER_API_KEY
    
    async def get_api_key(self, db: AsyncSession) -> Optional[str]:
        """Get weather API key from settings or database."""
        if self.api_key:
            return self.api_key
        result = await db.execute(
            select(GlobalSettings).where(GlobalSettings.key == "weather_api_key")
        )
        setting = result.scalar_one_or_none()
        if setting and setting.value:
            self.api_key = setting.value
            return self.api_key
        return None
    
    async def fetch_weather(
        self,
        latitude: float,
        longitude: float,
        db: AsyncSession
    ) -> Optional[Dict[str, Any]]:
        """
        Fetch weather data from OpenWeatherMap API.
        
        Args:
            latitude: Location latitude
            longitude: Location longitude
            db: Database session
            
        Returns:
            Weather data dict or None on error
        """
        api_key = await self.get_api_key(db)
        if not api_key:
            logger.warning("Weather API key not configured")
            return None
        
        params = {
            "lat": latitude,
            "lon": longitude,
            "appid": api_key,
            "units": "metric",
            "lang": "uz"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    self.BASE_URL,
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_weather(data)
                    else:
                        logger.error(f"Weather API error: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Weather fetch error: {e}")
            return None
    
    def _parse_weather(self, data: dict) -> Dict[str, Any]:
        """Parse OpenWeatherMap API response."""
        main = data.get("main", {})
        wind = data.get("wind", {})
        weather = data.get("weather", [{}])[0]
        rain = data.get("rain", {})
        
        condition = weather.get("main", "Clear")
        icon = WEATHER_ICONS.get(condition, "🌤️")
        
        return {
            "city": data.get("name", ""),
            "temp": round(main.get("temp", 0)),
            "feels_like": round(main.get("feels_like", 0)),
            "humidity": main.get("humidity", 0),
            "wind_speed": round(wind.get("speed", 0) * 3.6, 1),  # m/s to km/h
            "description": weather.get("description", ""),
            "condition": condition,
            "icon": icon,
            "precipitation": round(rain.get("1h", 0) * 100, 0) if rain else 0,
        }
    
    def format_weather_message(
        self,
        weather: Dict[str, Any],
        region_name: str,
        recommendation: str = ""
    ) -> str:
        """
        Format weather data into a Telegram message.
        
        Args:
            weather: Parsed weather data
            region_name: Region name to display
            recommendation: AI-generated recommendation
            
        Returns:
            Formatted message string
        """
        icon = weather.get("icon", "🌤️")
        
        msg = f"""🌍 <b>{sanitize_text(region_name)}</b> — Ob-havo

{icon} <b>{sanitize_text(weather.get('description', '').capitalize())}</b>

🌡 Harorat: <b>{weather.get('temp')}°C</b>
🤔 Seziladigan: <b>{weather.get('feels_like')}°C</b>
💨 Shamol: <b>{weather.get('wind_speed')} km/soat</b>
💧 Namlik: <b>{weather.get('humidity')}%</b>
🌧 Yog'ingarchilik: <b>{weather.get('precipitation')}%</b>"""
        
        if recommendation:
            msg += f"\n\n💡 <b>Tavsiya:</b> {sanitize_text(recommendation)}"
        
        msg += "\n\n📡 <i>Manba: OpenWeatherMap</i>"
        return msg
    
    async def send_weather_to_group(
        self,
        group_id: int,
        db: AsyncSession,
        bot=None,
        gemini_service=None
    ) -> bool:
        """
        Fetch and send weather to a group.
        
        Args:
            group_id: Telegram group ID
            db: Database session
            bot: Aiogram bot instance
            gemini_service: Gemini service instance
            
        Returns:
            True if sent successfully
        """
        try:
            # Get group with region
            result = await db.execute(
                select(Group).where(Group.telegram_id == group_id)
            )
            group = result.scalar_one_or_none()
            
            if not group or not group.region_id:
                logger.warning(f"Group {group_id} has no region configured")
                return False
            
            # Get region
            result = await db.execute(
                select(Region).where(Region.id == group.region_id)
            )
            region = result.scalar_one_or_none()
            
            if not region or not region.latitude:
                logger.warning(f"Region for group {group_id} has no coordinates")
                return False
            
            # Fetch weather
            weather = await self.fetch_weather(region.latitude, region.longitude, db)
            if not weather:
                await self._log_error(db, group_id, "Weather API returned no data")
                return False
            
            # Check for duplicate
            content = f"weather_{group_id}_{weather.get('temp')}_{weather.get('description')}"
            content_hash = hashlib.sha256(content.encode()).hexdigest()
            
            existing = await db.execute(
                select(SentPost).where(
                    SentPost.group_id == group_id,
                    SentPost.content_hash == content_hash
                )
            )
            if existing.scalar_one_or_none():
                return True  # Already sent
            
            # Get AI recommendation if enabled
            recommendation = ""
            if gemini_service:
                try:
                    recommendation = await gemini_service.format_weather_recommendation(weather, db)
                except Exception:
                    pass
            
            # Format message
            region_name = f"{region.viloyat}, {region.tuman}"
            message = self.format_weather_message(weather, region_name, recommendation)
            
            # Send to group
            if bot:
                await bot.send_message(group_id, message, parse_mode="HTML")
            
            # Record sent post
            sent_post = SentPost(
                group_id=group_id,
                post_type="weather",
                content_hash=content_hash
            )
            db.add(sent_post)
            await db.commit()
            
            return True
            
        except Exception as e:
            logger.error(f"Error sending weather to group {group_id}: {e}")
            await self._log_error(db, group_id, str(e))
            return False
    
    async def _log_error(self, db: AsyncSession, group_id: int, error: str):
        """Log error to admin_logs."""
        try:
            log = AdminLog(
                group_id=group_id,
                action="weather_error",
                details=error,
                level="error"
            )
            db.add(log)
            await db.commit()
        except Exception:
            pass
