# 🚀 Deployment Guide - Hududiy Agent Bot

## Current Status

✅ **Bot is ready to deploy!**
- Bot Username: `@GuruhAgent_bot`
- All commands implemented
- Working file: `working_bot.py`

## Quick Deploy (3 Steps)

### Option 1: PowerShell (Windows)

```powershell
# Run this command in PowerShell
.\deploy_to_server.ps1
```

### Option 2: Manual SSH

```bash
# 1. Push to GitHub (on your computer)
git add .
git commit -m "Deploy bot"
git push origin main

# 2. SSH to server
ssh doniyoebrk@ssh-doniyoebrk.alwaysdata.net
# Password: fs4-gMJ-XBu-ZJA

# 3. Run deployment script
cd bot
git pull origin main
chmod +x quick_restart.sh
./quick_restart.sh
```

## Test the Bot

After deployment, test these commands on Telegram:

1. Open Telegram
2. Search for `@GuruhAgent_bot`
3. Send `/start` - Should get welcome message
4. Send `/help` - Should see command list
5. Send `/id` - Should see your Telegram ID

## ⚠️ Important: Configure as Service for 24/7 Operation

The quick deployment runs the bot in a screen session, but **AlwaysData will kill it after some time**.

For **permanent 24/7 operation**, you MUST configure it as a Service:

1. Go to https://admin.alwaysdata.com/
2. Navigate to **Web > Services**
3. Click **Add a service**
4. Configure:
   - Name: `hudud-bot`
   - Command: `/home/doniyoebrk/bot/alwaysdata_service.sh`
   - Working directory: `/home/doniyoebrk/bot`
   - Autostart: ✅ Enabled
   - Autorestart: ✅ Enabled
5. Click **Submit**

See `ALWAYSDATA_SERVICE_SETUP.md` for detailed instructions.

## Available Commands

All commands work and respond:

### User Commands
- `/start` - Welcome message
- `/help` - Command list
- `/id` - Get your Telegram ID
- `/weather` - Weather info (placeholder)
- `/prayer` - Prayer times (placeholder)
- `/news` - News feed (placeholder)
- `/jobs` - Job listings (placeholder)
- `/ai [question]` - AI assistant (placeholder)

### Admin Commands
- `/admin` - Admin panel (super admin only)
- `/settings` - Group settings

## Troubleshooting

### Bot not responding?

```bash
# SSH to server
ssh doniyoebrk@ssh-doniyoebrk.alwaysdata.net

# Check if bot is running
screen -ls

# View bot logs
screen -r hudud_bot
# Press Ctrl+A then D to detach

# Restart bot
cd bot
./quick_restart.sh
```

### Bot keeps getting killed?

This means you haven't configured it as a Service. Follow the Service setup instructions above.

### Commands not working?

1. Check bot is running: `screen -ls`
2. View logs: `screen -r hudud_bot`
3. Verify bot token in `working_bot.py`
4. Test with `/start` command

## Next Steps

After deployment, you can:

1. ✅ **Configure as Service** (for 24/7 operation)
2. 🔧 **Implement full functionality** for each module:
   - Connect to SQLite database
   - Integrate OpenWeatherMap API
   - Integrate Aladhan Prayer Times API
   - Integrate Gemini AI API
   - Add scheduler for automated posts
   - Build admin panel with inline keyboards
3. 📊 **Monitor logs** via AlwaysData panel
4. 🧪 **Test all features** in your Telegram group

## Support

If you encounter issues:
1. Check `ALWAYSDATA_SERVICE_SETUP.md` for detailed setup
2. View bot logs: `screen -r hudud_bot`
3. Check AlwaysData service logs in admin panel
4. Verify all credentials are correct

---

**Ready to deploy? Run `.\deploy_to_server.ps1` now!** 🚀
