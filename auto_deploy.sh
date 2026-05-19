#!/bin/bash

echo "🚀 Starting automatic deployment..."

# 1. Clone repository
echo "📥 Cloning from GitHub..."
cd ~
if [ -d "telegram-bot" ]; then
    echo "Directory exists, pulling latest changes..."
    cd telegram-bot
    git pull origin main
else
    git clone https://github.com/Doniyorbek2000/bot.git telegram-bot
    cd telegram-bot
fi

# 2. Create virtual environment
echo "🐍 Setting up Python environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate

# 3. Create .env file
echo "⚙️ Creating .env file..."
cat > .env << 'EOF'
BOT_TOKEN=8203936087:AAGYbGA2GKmty1g87qZUxvL555h3U24hkfw
SUPER_ADMIN_IDS=123456789
DATABASE_URL=sqlite+aiosqlite:///./hudud_bot.db
REDIS_URL=redis://localhost:6379/0
GEMINI_API_KEY=AIzaSyAPBo9Mvcv45gl8as57UdsTkz8U95Wy9bs
WEATHER_API_KEY=3bd96747cc5158a323d55f9d0d58ce90
TIMEZONE=Asia/Tashkent
LOG_LEVEL=INFO
EOF

# 4. Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# 5. Run migrations
echo "🗄️ Running database migrations..."
alembic upgrade head

# 6. Stop old bot if running
echo "🛑 Stopping old bot..."
pkill -f "python -m app.main" 2>/dev/null || true

# 7. Start bot
echo "✅ Starting bot..."
nohup python -m app.main > bot.log 2>&1 &

echo "🎉 Deployment complete!"
echo "📋 Check logs with: tail -f ~/telegram-bot/bot.log"
echo "🔍 Check status with: ps aux | grep python"
