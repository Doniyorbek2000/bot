#!/bin/bash

# Quick deployment script with new token
# Run this on AlwaysData server

echo "🚀 Starting quick deployment..."

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. Remove old installation
echo -e "${YELLOW}📦 Removing old installation...${NC}"
cd ~
rm -rf telegram-bot

# 2. Clone repository
echo -e "${YELLOW}📥 Cloning from GitHub...${NC}"
git clone https://github.com/Doniyorbek2000/bot.git telegram-bot
cd telegram-bot

# 3. Create virtual environment
echo -e "${YELLOW}🐍 Setting up Python environment...${NC}"
python3 -m venv venv
source venv/bin/activate

# 4. Create .env file with NEW TOKEN
echo -e "${YELLOW}⚙️ Creating .env file...${NC}"
cat > .env << 'EOF'
BOT_TOKEN=8525111021:AAFUmLHZ3LZcHgw8pbbzIw6xRbYG35x2y1Q
SUPER_ADMIN_IDS=8674220680
DATABASE_URL=sqlite+aiosqlite:///./hudud_bot.db
REDIS_URL=redis://localhost:6379/0
GEMINI_API_KEY=AIzaSyAPBo9Mvcv45gl8as57UdsTkz8U95Wy9bs
WEATHER_API_KEY=3bd96747cc5158a323d55f9d0d58ce90
TIMEZONE=Asia/Tashkent
LOG_LEVEL=INFO
EOF

# 5. Install dependencies
echo -e "${YELLOW}📦 Installing dependencies...${NC}"
pip install -r requirements.txt

# 6. Run migrations
echo -e "${YELLOW}🗄️ Running database migrations...${NC}"
alembic upgrade head

# 7. Stop old bot if running
echo -e "${YELLOW}🛑 Stopping old bot...${NC}"
pkill -f "python -m app.main" 2>/dev/null || true
sleep 2

# 8. Start bot
echo -e "${GREEN}✅ Starting bot...${NC}"
nohup python -m app.main > bot.log 2>&1 &

# Wait a bit
sleep 3

# 9. Check if bot is running
if ps aux | grep -v grep | grep "python -m app.main" > /dev/null; then
    echo -e "${GREEN}🎉 Bot is running successfully!${NC}"
    echo -e "${GREEN}📋 Check logs with: tail -f ~/telegram-bot/bot.log${NC}"
    echo -e "${GREEN}🔍 Check status with: ps aux | grep python${NC}"
else
    echo -e "${YELLOW}⚠️ Bot may not be running. Check logs:${NC}"
    tail -20 bot.log
fi
