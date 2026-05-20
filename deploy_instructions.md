# 🚀 AlwaysData Serverga Bot Deploy Qilish

## SSH orqali ulanish:
```bash
ssh doniyoebrk@ssh-doniyoebrk.alwaysdata.net
# Parol: fs4-gMJ-XBu-ZJA
```

## 1. Bot papkasiga o'tish:
```bash
cd bot
```

## 2. Eng yangi kodni tortish:
```bash
git pull origin main
```

## 3. Dependencies o'rnatish (agar kerak bo'lsa):
```bash
pip3 install --user -r requirements.txt
```

## 4. Database migratsiyasini ishga tushirish:
```bash
python3 -m alembic upgrade head
```

## 5. Botni ishga tushirish (screen yordamida):
```bash
# Eski screen session'ni o'chirish
screen -X -S hudud_bot quit 2>/dev/null

# Yangi screen session yaratish va botni ishga tushirish
screen -dmS hudud_bot bash -c 'cd /home/doniyoebrk/bot && python3 app/main.py'

# Screen session'ni ko'rish
screen -ls

# Screen session'ga ulanish (loglarni ko'rish uchun)
screen -r hudud_bot
# (Chiqish uchun: Ctrl+A, keyin D)
```

## 6. Bot ishlayotganini tekshirish:
```bash
# Process'ni tekshirish
ps aux | grep "python3 app/main.py" | grep -v grep

# Yoki
pgrep -f "python3 app/main.py"
```

## 7. Botni to'xtatish:
```bash
# Screen session orqali
screen -X -S hudud_bot quit

# Yoki to'g'ridan-to'g'ri process'ni o'chirish
pkill -f "python3 app/main.py"
```

## 🔄 Tez Deploy (Barcha qadamlar):
```bash
cd bot && \
git pull origin main && \
screen -X -S hudud_bot quit 2>/dev/null && \
screen -dmS hudud_bot bash -c 'cd /home/doniyoebrk/bot && python3 app/main.py' && \
sleep 2 && \
screen -ls && \
pgrep -f "python3 app/main.py" && \
echo "✅ Bot muvaffaqiyatli ishga tushdi!"
```

## 📱 Bot Ma'lumotlari:
- **Bot Username:** @GuruhAgent_bot
- **Bot Link:** https://t.me/GuruhAgent_bot
- **Super Admin ID:** 8674220680

## 🔍 Loglarni Ko'rish:
```bash
# Screen session'ga ulanish
screen -r hudud_bot

# Yoki agar bot log faylga yozayotgan bo'lsa
tail -f bot.log
```

## ⚠️ Muhim Eslatmalar:
1. AlwaysData serverda uzoq vaqt ishlaydigan process'lar avtomatik o'chirilishi mumkin
2. 24/7 ishlash uchun **Services** bo'limidan sozlash tavsiya etiladi
3. Screen session ishlamasa, tmux ishlatishingiz mumkin

## 🛠️ Muammolarni Hal Qilish:

### Bot javob bermasa:
```bash
# Loglarni tekshirish
screen -r hudud_bot

# Process ishlayotganini tekshirish
ps aux | grep python3

# Botni qayta ishga tushirish
screen -X -S hudud_bot quit
screen -dmS hudud_bot bash -c 'cd /home/doniyoebrk/bot && python3 app/main.py'
```

### Database xatoligi:
```bash
cd bot
python3 -m alembic upgrade head
```

### Dependencies xatoligi:
```bash
cd bot
pip3 install --user -r requirements.txt
```
