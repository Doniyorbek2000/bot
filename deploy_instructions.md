# AlwaysData'ga Deploy qilish yo'riqnomasi

## 1. SSH orqali serverga ulanish

```bash
ssh doniyoebrk@ssh-doniyoebrk.alwaysdata.net
```
Parol: `fs4-gMJ-XBu-ZJA`

## 2. GitHub'dan loyihani clone qilish

```bash
cd ~
git clone https://github.com/Doniyorbek2000/bot.git telegram-bot
cd telegram-bot
```

## 3. Virtual environment yaratish

```bash
python3 -m venv venv
source venv/bin/activate
```

## 4. .env faylini yaratish

```bash
nano .env
```

Quyidagi ma'lumotlarni kiriting:

```env
BOT_TOKEN=8203936087:AAGYbGA2GKmty1g87qZUxvL555h3U24hkfw
SUPER_ADMIN_IDS=123456789
DATABASE_URL=sqlite+aiosqlite:///./hudud_bot.db
REDIS_URL=redis://localhost:6379/0
GEMINI_API_KEY=AIzaSyAPBo9Mvcv45gl8as57UdsTkz8U95Wy9bs
WEATHER_API_KEY=3bd96747cc5158a323d55f9d0d58ce90
TIMEZONE=Asia/Tashkent
LOG_LEVEL=INFO
```

Ctrl+X, Y, Enter bilan saqlang.

## 5. Paketlarni o'rnatish

```bash
pip install -r requirements.txt
```

## 6. Database yaratish

```bash
alembic upgrade head
```

## 7. Botni ishga tushirish

### A. Test rejimida (to'g'ri ishlashini tekshirish):
```bash
python -m app.main
```

Ctrl+C bilan to'xtatish mumkin.

### B. Background'da ishga tushirish (doimiy):
```bash
nohup python -m app.main > bot.log 2>&1 &
```

## 8. Bot holatini tekshirish

```bash
# Loglarni ko'rish
tail -f bot.log

# Jarayonni topish
ps aux | grep python

# Botni to'xtatish (agar kerak bo'lsa)
pkill -f "python -m app.main"
```

## 9. Yangilanishlarni olish

```bash
cd ~/telegram-bot
git pull origin main
pip install -r requirements.txt
alembic upgrade head

# Botni qayta ishga tushirish
pkill -f "python -m app.main"
nohup python -m app.main > bot.log 2>&1 &
```

## 10. AlwaysData Sites orqali (avtomatik restart)

1. AlwaysData admin panelda **Sites** bo'limiga o'ting
2. **Add a site** tugmasini bosing
3. Quyidagilarni to'ldiring:
   - **Name**: telegram-bot
   - **Type**: Python
   - **Python version**: 3.11 yoki yuqori
   - **Command**: `python -m app.main`
   - **Working directory**: `/home/doniyoebrk/telegram-bot`
   - **Environment variables**: .env fayldagi ma'lumotlarni kiriting

4. **Save** tugmasini bosing

Bu yo'l bilan bot avtomatik ishga tushadi va server restart bo'lganda ham qayta ishga tushadi.
