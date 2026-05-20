#!/bin/bash

# AlwaysData server deployment script
# This script deploys the bot to AlwaysData server

echo "🚀 Starting deployment to AlwaysData server..."

# Server details
SERVER="doniyoebrk@ssh-doniyoebrk.alwaysdata.net"
BOT_DIR="bot"

# Step 1: Pull latest code from GitHub
echo "📥 Pulling latest code from GitHub..."
ssh -o StrictHostKeyChecking=no $SERVER << 'ENDSSH'
cd bot
git pull origin main
echo "✅ Code pulled successfully"
ENDSSH

# Step 2: Run database migrations
echo "🗄️  Running database migrations..."
ssh -o StrictHostKeyChecking=no $SERVER << 'ENDSSH'
cd bot
python3 -m alembic upgrade head
echo "✅ Migrations completed"
ENDSSH

# Step 3: Stop existing bot process (if running)
echo "🛑 Stopping existing bot process..."
ssh -o StrictHostKeyChecking=no $SERVER << 'ENDSSH'
pkill -f "python3 app/main.py" || echo "No existing bot process found"
ENDSSH

# Step 4: Start the bot
echo "▶️  Starting bot..."
ssh -o StrictHostKeyChecking=no $SERVER << 'ENDSSH'
cd bot
nohup python3 app/main.py > bot.log 2>&1 &
echo "✅ Bot started successfully"
ENDSSH

# Step 5: Check bot status
echo "📊 Checking bot status..."
ssh -o StrictHostKeyChecking=no $SERVER << 'ENDSSH'
cd bot
sleep 3
if pgrep -f "python3 app/main.py" > /dev/null; then
    echo "✅ Bot is running!"
    echo "📝 Last 10 lines of log:"
    tail -n 10 bot.log
else
    echo "❌ Bot is not running. Check logs:"
    tail -n 20 bot.log
fi
ENDSSH

echo "🎉 Deployment completed!"
