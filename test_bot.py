#!/usr/bin/env python3
"""Test bot connectivity and basic functionality."""
import asyncio
import sys
from aiogram import Bot
from app.utils.config import settings

async def test_bot():
    """Test bot connection."""
    print("🔍 Testing bot connection...")
    print(f"Bot Token: {settings.BOT_TOKEN[:20]}...")
    
    try:
        bot = Bot(token=settings.BOT_TOKEN)
        me = await bot.get_me()
        
        print(f"\n✅ Bot is working!")
        print(f"Bot ID: {me.id}")
        print(f"Bot Name: {me.first_name}")
        print(f"Bot Username: @{me.username}")
        print(f"Can Join Groups: {me.can_join_groups}")
        
        # Test sending a message to super admin
        try:
            admin_id = int(settings.SUPER_ADMIN_IDS.split(',')[0])
            await bot.send_message(
                admin_id,
                "✅ Bot test muvaffaqiyatli! Bot ishlayapti va xabar yuborish mumkin."
            )
            print(f"\n✅ Test message sent to admin {admin_id}")
        except Exception as e:
            print(f"\n⚠️ Could not send test message: {e}")
        
        await bot.session.close()
        return True
        
    except Exception as e:
        print(f"\n❌ Bot test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(test_bot())
    sys.exit(0 if result else 1)
