"""Admin panel keyboards."""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_admin_panel_keyboard() -> InlineKeyboardMarkup:
    """Get group admin panel keyboard."""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🌍 Hududni sozlash", callback_data="admin_region")],
        [InlineKeyboardButton(text="🌤 Ob-havo sozlamalari", callback_data="admin_weather")],
        [InlineKeyboardButton(text="🕌 Namoz vaqti sozlamalari", callback_data="admin_prayer")],
        [InlineKeyboardButton(text="📰 Yangiliklar sozlamalari", callback_data="admin_news")],
        [InlineKeyboardButton(text="💼 Ish e'lonlari sozlamalari", callback_data="admin_jobs")],
        [InlineKeyboardButton(text="📢 Majburiy obuna", callback_data="admin_subscription")],
        [InlineKeyboardButton(text="👥 Odam qo'shish sharti", callback_data="admin_invite")],
        [InlineKeyboardButton(text="🚫 Taqiqlangan so'zlar", callback_data="admin_banwords")],
        [InlineKeyboardButton(text="🤖 AI sozlamalari", callback_data="admin_ai")],
        [InlineKeyboardButton(text="📊 Statistika", callback_data="admin_stats")],
        [InlineKeyboardButton(text="⚙️ Modullarni boshqarish", callback_data="admin_modules")],
    ])
    return keyboard


def get_superadmin_panel_keyboard() -> InlineKeyboardMarkup:
    """Get super admin panel keyboard."""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Barcha guruhlar", callback_data="sa_groups")],
        [InlineKeyboardButton(text="📺 Barcha kanallar", callback_data="sa_channels")],
        [InlineKeyboardButton(text="⚙️ Global sozlamalar", callback_data="sa_settings")],
        [InlineKeyboardButton(text="🔑 API sozlamalari", callback_data="sa_api")],
        [InlineKeyboardButton(text="📰 Yangilik manbalari", callback_data="sa_news_sources")],
        [InlineKeyboardButton(text="💼 Ish manbalari", callback_data="sa_job_sources")],
        [InlineKeyboardButton(text="📢 Global obuna", callback_data="sa_global_sub")],
        [InlineKeyboardButton(text="📣 Reklama yuborish", callback_data="sa_broadcast")],
        [InlineKeyboardButton(text="📊 Statistika", callback_data="sa_stats")],
        [InlineKeyboardButton(text="📝 Loglar", callback_data="sa_logs")],
        [InlineKeyboardButton(text="🚫 Bloklash/Ochish", callback_data="sa_block")],
    ])
    return keyboard


def get_module_toggle_keyboard(settings: dict) -> InlineKeyboardMarkup:
    """Get module toggle keyboard."""
    def status(enabled: bool) -> str:
        return "✅" if enabled else "❌"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=f"{status(settings.get('weather_enabled'))} Ob-havo",
            callback_data="toggle_weather"
        )],
        [InlineKeyboardButton(
            text=f"{status(settings.get('prayer_enabled'))} Namoz vaqti",
            callback_data="toggle_prayer"
        )],
        [InlineKeyboardButton(
            text=f"{status(settings.get('news_enabled'))} Yangiliklar",
            callback_data="toggle_news"
        )],
        [InlineKeyboardButton(
            text=f"{status(settings.get('jobs_enabled'))} Ish e'lonlari",
            callback_data="toggle_jobs"
        )],
        [InlineKeyboardButton(
            text=f"{status(settings.get('ai_enabled'))} AI yordamchi",
            callback_data="toggle_ai"
        )],
        [InlineKeyboardButton(
            text=f"{status(settings.get('subscription_enabled'))} Majburiy obuna",
            callback_data="toggle_subscription"
        )],
        [InlineKeyboardButton(
            text=f"{status(settings.get('invite_enabled'))} Odam qo'shish",
            callback_data="toggle_invite"
        )],
        [InlineKeyboardButton(
            text=f"{status(settings.get('moderation_enabled'))} Moderatsiya",
            callback_data="toggle_moderation"
        )],
        [InlineKeyboardButton(text="◀️ Orqaga", callback_data="admin_back")],
    ])
    return keyboard


def get_back_button() -> InlineKeyboardMarkup:
    """Get back button keyboard."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Orqaga", callback_data="admin_back")]
    ])
