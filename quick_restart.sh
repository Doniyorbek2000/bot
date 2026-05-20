#!/bin/bash
# Quick restart script for Hududiy Agent Bot
# Use this for quick testing. For 24/7 operation, configure as AlwaysData Service.

echo "🚀 Quick Restart Script for Hududiy Agent Bot"
echo "=============================================="

# Navigate to bot directory
cd ~/bot || { echo "❌ Error: bot directory not found"; exit 1; }

# Pull latest code from GitHub
echo "📥 Pulling latest code from GitHub..."
git pull origin main

# Stop existing bot process
echo "🛑 Stopping existing bot..."
screen -X -S hudud_bot quit 2>/dev/null || echo "No existing bot process found"
pkill -f "python3 working_bot.py" 2>/dev/null || true

# Wait a moment
sleep 2

# Start bot in screen session
echo "▶️  Starting bot in screen session..."
screen -dmS hudud_bot python3 working_bot.py

# Wait for bot to start
sleep 3

# Check if bot is running
if screen -list | grep -q "hudud_bot"; then
    echo "✅ Bot is running in screen session 'hudud_bot'"
    echo ""
    echo "📊 To view bot logs:"
    echo "   screen -r hudud_bot"
    echo "   (Press Ctrl+A then D to detach)"
    echo ""
    echo "⚠️  WARNING: This is a temporary solution!"
    echo "   AlwaysData will kill long-running processes."
    echo "   Configure as a Service for 24/7 operation."
    echo "   See ALWAYSDATA_SERVICE_SETUP.md for instructions."
else
    echo "❌ Error: Bot failed to start"
    echo "Check logs with: tail -n 50 ~/bot/bot.log"
    exit 1
fi

echo ""
echo "🎉 Deployment completed!"
