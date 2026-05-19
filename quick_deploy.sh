#!/bin/bash
# Quick deploy script for AlwaysData server

echo "🚀 Starting quick deployment..."

# Navigate to bot directory
cd /home/doniyoebrk/bot || exit 1

# Pull latest code
echo "📥 Pulling latest code..."
git pull origin main

# Stop existing bot
echo "🛑 Stopping existing bot..."
screen -X -S hudud_bot quit 2>/dev/null
pkill -f "python3 app/main.py" 2>/dev/null
sleep 1

# Start bot in screen
echo "▶️  Starting bot in screen session..."
screen -dmS hudud_bot bash -c 'cd /home/doniyoebrk/bot && python3 app/main.py'

# Wait a bit
sleep 3

# Check if bot is running
echo "📊 Checking bot status..."
if pgrep -f "python3 app/main.py" > /dev/null; then
    echo "✅ Bot is running!"
    echo "📋 Screen sessions:"
    screen -ls
    echo ""
    echo "🔍 To view logs: screen -r hudud_bot"
    echo "🚪 To detach: Ctrl+A then D"
else
    echo "❌ Bot failed to start!"
    echo "Check logs with: screen -r hudud_bot"
fi
