"""Gemini AI service."""
import hashlib
from typing import Optional
import google.generativeai as genai
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database.models import AILog, GlobalSettings
from app.utils.config import settings
from app.utils.logger import logger


class GeminiService:
    """Service for Gemini AI interactions."""
    
    def __init__(self):
        """Initialize Gemini service."""
        self.api_key = settings.GEMINI_API_KEY
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-pro')
        else:
            self.model = None
    
    async def get_api_key(self, db: AsyncSession) -> Optional[str]:
        """
        Get Gemini API key from global settings or env.
        
        Args:
            db: Database session
            
        Returns:
            API key or None
        """
        if self.api_key:
            return self.api_key
        
        # Try to get from database
        result = await db.execute(
            select(GlobalSettings).where(GlobalSettings.key == "gemini_api_key")
        )
        setting = result.scalar_one_or_none()
        if setting and setting.value:
            self.api_key = setting.value
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-pro')
            return self.api_key
        
        return None
    
    async def generate_response(
        self,
        prompt: str,
        db: AsyncSession,
        user_id: Optional[int] = None,
        group_id: Optional[int] = None,
        max_tokens: int = 1000
    ) -> str:
        """
        Generate AI response using Gemini.
        
        Args:
            prompt: Input prompt
            db: Database session
            user_id: User ID for logging
            group_id: Group ID for logging
            max_tokens: Maximum response tokens
            
        Returns:
            Generated response text
        """
        input_hash = hashlib.sha256(prompt.encode()).hexdigest()
        
        try:
            # Check if API key is available
            api_key = await self.get_api_key(db)
            if not api_key or not self.model:
                fallback = "AI xizmati hozirda mavjud emas. Iltimos, keyinroq urinib ko'ring."
                await self._log_request(db, user_id, group_id, input_hash, None, prompt, fallback, "no_api_key")
                return fallback
            
            # Generate response
            response = self.model.generate_content(prompt)
            response_text = response.text if response.text else "Javob olinmadi."
            response_hash = hashlib.sha256(response_text.encode()).hexdigest()
            
            # Log successful request
            await self._log_request(db, user_id, group_id, input_hash, response_hash, prompt, response_text, "success")
            
            return response_text
            
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            fallback = "Xatolik yuz berdi. Iltimos, keyinroq urinib ko'ring."
            await self._log_request(db, user_id, group_id, input_hash, None, prompt, None, "error", str(e))
            return fallback
    
    async def format_weather_recommendation(
        self,
        weather_data: dict,
        db: AsyncSession
    ) -> str:
        """
        Format weather data with AI recommendation.
        
        Args:
            weather_data: Raw weather data
            db: Database session
            
        Returns:
            Formatted weather text with recommendation
        """
        prompt = f"""
Quyidagi ob-havo ma'lumotlariga asoslanib, o'zbek tilida qisqa tavsiya yozing (2-3 jumla):

Harorat: {weather_data.get('temp')}°C
Seziladigan harorat: {weather_data.get('feels_like')}°C
Shamol: {weather_data.get('wind_speed')} km/soat
Namlik: {weather_data.get('humidity')}%
Yog'ingarchilik: {weather_data.get('precipitation')}%

Faqat tavsiya matnini yozing, boshqa hech narsa qo'shmang.
"""
        
        recommendation = await self.generate_response(prompt, db)
        return recommendation
    
    async def format_news_summary(
        self,
        news_title: str,
        news_content: str,
        db: AsyncSession
    ) -> str:
        """
        Format news item with AI summary.
        
        Args:
            news_title: News title
            news_content: News content
            db: Database session
            
        Returns:
            Formatted news summary
        """
        prompt = f"""
Quyidagi yangilikni o'zbek tilida qisqa va tushunarli qilib yozing (3-4 jumla):

Sarlavha: {news_title}
Matn: {news_content[:500]}

Faqat qisqacha mazmunni yozing, manba va havolani o'zgartirmang.
"""
        
        summary = await self.generate_response(prompt, db)
        return summary
    
    async def _log_request(
        self,
        db: AsyncSession,
        user_id: Optional[int],
        group_id: Optional[int],
        input_hash: str,
        response_hash: Optional[str],
        input_text: str,
        response_text: Optional[str],
        status: str,
        error_message: Optional[str] = None
    ):
        """Log AI request to database."""
        try:
            log = AILog(
                user_id=user_id,
                group_id=group_id,
                input_hash=input_hash,
                response_hash=response_hash,
                input_text=input_text[:1000] if input_text else None,
                response_text=response_text[:2000] if response_text else None,
                status=status,
                error_message=error_message
            )
            db.add(log)
            await db.commit()
        except Exception as e:
            logger.error(f"Failed to log AI request: {e}")
