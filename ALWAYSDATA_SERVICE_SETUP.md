# AlwaysData Service Setup Instructions

## Problem
AlwaysData kills long-running processes automatically. To run the bot 24/7, you need to configure it as a **Service**.

## Solution: Configure Bot as AlwaysData Service

### Step 1: Push Code to GitHub

```bash
git add .
git commit -m "Add service configuration for AlwaysData"
git push origin main
```

### Step 2: SSH to AlwaysData Server

```bash
ssh doniyoebrk@ssh-doniyoebrk.alwaysdata.net
# Password: fs4-gMJ-XBu-ZJA
```

### Step 3: Pull Latest Code

```bash
cd bot
git pull origin main
```

### Step 4: Make Service Script Executable

```bash
chmod +x alwaysdata_service.sh
```

### Step 5: Configure Service via AlwaysData Web Panel

1. Go to https://admin.alwaysdata.com/
2. Login with your credentials
3. Navigate to **Web > Services**
4. Click **Add a service**
5. Fill in the form:
   - **Name**: `hudud-bot`
   - **Command**: `/home/doniyoebrk/bot/alwaysdata_service.sh`
   - **Working directory**: `/home/doniyoebrk/bot`
   - **Type**: `Program`
   - **Autostart**: ✅ Enabled
   - **Autorestart**: ✅ Enabled
6. Click **Submit**

### Step 6: Start the Service

The service will start automatically. You can also:
- **Start**: Click the ▶️ button in the Services panel
- **Stop**: Click the ⏹️ button
- **Restart**: Click the 🔄 button
- **View Logs**: Click on the service name to see logs

### Step 7: Verify Bot is Running

Test the bot on Telegram:
- Send `/start` to @GuruhAgent_bot
- Send `/help` to see all commands
- Send `/id` to get your ID

## Alternative: Quick Deploy via SSH (Temporary)

If you need to quickly restart the bot without configuring a service:

```bash
# SSH to server
ssh doniyoebrk@ssh-doniyoebrk.alwaysdata.net

# Navigate to bot directory
cd bot

# Pull latest code
git pull origin main

# Stop existing bot (if running)
screen -X -S hudud_bot quit

# Start bot in screen session
screen -dmS hudud_bot python3 working_bot.py

# Verify it's running
screen -ls

# To view bot logs (Ctrl+A then D to detach)
screen -r hudud_bot
```

**Note**: This method is temporary. The bot will be killed after running for too long. Use the Service configuration for permanent 24/7 operation.

## Troubleshooting

### Bot Not Responding
1. Check service status in AlwaysData panel
2. View service logs
3. Verify bot token is correct in `working_bot.py`
4. Test bot with `/start` command

### Service Won't Start
1. Check script permissions: `chmod +x alwaysdata_service.sh`
2. Verify Python is installed: `python3 --version`
3. Check working directory path is correct
4. View error logs in AlwaysData panel

### Bot Gets Killed
- This means you're NOT using the Service configuration
- Follow Step 5 above to configure as a Service
- Services are protected from automatic termination

## Current Bot Status

- **Bot Username**: @GuruhAgent_bot
- **Bot Token**: `8525111021:AAFUmLHZ3LZcHgw8pbbzIw6xRbYG35x2y1Q`
- **Super Admin ID**: `8674220680`
- **Working File**: `working_bot.py`

## Available Commands

All commands are implemented and working:

- `/start` - Welcome message
- `/help` - Command list
- `/admin` - Admin panel (super admin only)
- `/settings` - Group settings
- `/id` - Get your Telegram ID
- `/weather` - Weather module (placeholder)
- `/prayer` - Prayer times (placeholder)
- `/news` - News module (placeholder)
- `/jobs` - Jobs module (placeholder)
- `/ai [question]` - AI assistant (placeholder)

## Next Steps

After configuring the service, you can implement full functionality for each module by:
1. Connecting to database (SQLite)
2. Integrating external APIs (OpenWeatherMap, Aladhan, Gemini)
3. Implementing scheduler for automated posts
4. Adding admin panel with inline keyboards

For now, the bot responds to all commands with placeholder messages.
