# 🤖 Hududiy Agent Bot - O'rnatish va Ishga Tushirish

## 📋 Hozirgi Holat

✅ **Bot tayyor va ishlamoqda!**
- Bot nomi: `@GuruhAgent_bot`
- Barcha buyruqlar qo'shilgan
- Token: `8525111021:AAFUmLHZ3LZcHgw8pbbzIw6xRbYG35x2y1Q`
- Super Admin ID: `8674220680`

## 🚀 Tezkor Ishga Tushirish (3 Qadam)

### 1-Qadam: GitHub'ga Yuklash

```powershell
# PowerShell'da bajaring
git add .
git commit -m "Bot tayyor"
git push origin main
```

### 2-Qadam: Serverga Deploy Qilish

```powershell
# PowerShell'da bajaring
.\deploy_to_server.ps1
```

Yoki qo'lda:

```bash
# SSH orqali serverga kirish
ssh doniyoebrk@ssh-doniyoebrk.alwaysdata.net
# Parol: fs4-gMJ-XBu-ZJA

# Bot papkasiga o'tish
cd bot

# Yangi kodni olish
git pull origin main

# Botni ishga tushirish
chmod +x quick_restart.sh
./quick_restart.sh
```

### 3-Qadam: Botni Sinab Ko'rish

1. Telegram'ni oching
2. `@GuruhAgent_bot` ni qidiring
3. `/start` buyrug'ini yuboring
4. `/help` buyrug'ini yuboring
5. `/id` buyrug'ini yuboring

## ⚠️ MUHIM: 24/7 Ishlashi Uchun Service Sifatida Sozlang

Hozirgi deploy usuli vaqtinchalik. AlwaysData uzoq vaqt ishlaydigan jarayonlarni o'chiradi.

**24/7 ishlashi uchun Service sifatida sozlash kerak:**

1. https://admin.alwaysdata.com/ ga kiring
2. **Web > Services** bo'limiga o'ting
3. **Add a service** tugmasini bosing
4. Quyidagilarni to'ldiring:
   - **Name**: `hudud-bot`
   - **Command**: `/home/doniyoebrk/bot/alwaysdata_service.sh`
   - **Working directory**: `/home/doniyoebrk/bot`
   - **Autostart**: ✅ Yoqilgan
   - **Autorestart**: ✅ Yoqilgan
5. **Submit** tugmasini bosing

Batafsil ko'rsatma: `ALWAYSDATA_SERVICE_SETUP.md`

## 📱 Mavjud Buyruqlar

Barcha buyruqlar ishlaydi:

### Foydalanuvchilar Uchun
- `/start` - Botni boshlash
- `/help` - Yordam
- `/id` - Telegram ID'ingizni ko'rish
- `/weather` - Ob-havo (hozircha shablon)
- `/prayer` - Namoz vaqtlari (hozircha shablon)
- `/news` - Yangiliklar (hozircha shablon)
- `/jobs` - Ish e'lonlari (hozircha shablon)
- `/ai [savol]` - AI yordamchi (hozircha shablon)

### Adminlar Uchun
- `/admin` - Admin panel (faqat super admin)
- `/settings` - Guruh sozlamalari

## 🔧 Muammolarni Hal Qilish

### Bot javob bermayapti?

```bash
# Serverga kirish
ssh doniyoebrk@ssh-doniyoebrk.alwaysdata.net

# Bot ishlab turganini tekshirish
screen -ls

# Bot loglarini ko'rish
screen -r hudud_bot
# Chiqish: Ctrl+A keyin D

# Botni qayta ishga tushirish
cd bot
./quick_restart.sh
```

### Bot tez-tez o'chib qolyaptimi?

Bu Service sifatida sozlanmaganligini bildiradi. Yuqoridagi Service sozlash ko'rsatmasiga amal qiling.

### Buyruqlar ishlamayaptimi?

1. Bot ishlab turganini tekshiring: `screen -ls`
2. Loglarni ko'ring: `screen -r hudud_bot`
3. Bot tokenini tekshiring
4. `/start` buyrug'i bilan sinab ko'ring

## 📊 Keyingi Qadamlar

Deploy qilgandan keyin:

1. ✅ **Service sifatida sozlang** (24/7 ishlashi uchun)
2. 🔧 **To'liq funksionallikni qo'shing**:
   - SQLite bazasiga ulanish
   - OpenWeatherMap API integratsiyasi
   - Aladhan Prayer Times API integratsiyasi
   - Gemini AI API integratsiyasi
   - Avtomatik postlar uchun scheduler
   - Inline klaviaturali admin panel
3. 📈 **Loglarni kuzating**
4. 🧪 **Barcha funksiyalarni sinab ko'ring**

## 💡 Yordam

Muammo bo'lsa:
1. `ALWAYSDATA_SERVICE_SETUP.md` ni o'qing
2. Bot loglarini ko'ring: `screen -r hudud_bot`
3. AlwaysData admin panelida service loglarini tekshiring
4. Barcha ma'lumotlar to'g'riligini tekshiring

---

**Deploy qilishga tayyormisiz? `.\deploy_to_server.ps1` ni ishga tushiring!** 🚀
