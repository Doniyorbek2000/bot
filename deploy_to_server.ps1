# AlwaysData server deployment script (PowerShell)
# This script deploys the bot to AlwaysData server

Write-Host "🚀 Starting deployment to AlwaysData server..." -ForegroundColor Green

# Server details
$SERVER = "doniyoebrk@ssh-doniyoebrk.alwaysdata.net"
$PASSWORD = "fs4-gMJ-XBu-ZJA"

# Step 1: Pull latest code from GitHub
Write-Host "📥 Pulling latest code from GitHub..." -ForegroundColor Yellow
$pullCmd = @"
cd bot && git pull origin main && echo 'Code pulled successfully'
"@
echo $PASSWORD | ssh -o StrictHostKeyChecking=no $SERVER $pullCmd

# Step 2: Run database migrations
Write-Host "🗄️  Running database migrations..." -ForegroundColor Yellow
$migrateCmd = @"
cd bot && python3 -m alembic upgrade head && echo 'Migrations completed'
"@
echo $PASSWORD | ssh -o StrictHostKeyChecking=no $SERVER $migrateCmd

# Step 3: Stop existing bot process
Write-Host "🛑 Stopping existing bot process..." -ForegroundColor Yellow
$stopCmd = @"
pkill -f 'python3 app/main.py' || echo 'No existing bot process found'
"@
echo $PASSWORD | ssh -o StrictHostKeyChecking=no $SERVER $stopCmd

# Step 4: Start the bot
Write-Host "▶️  Starting bot..." -ForegroundColor Yellow
$startCmd = @"
cd bot && nohup python3 app/main.py > bot.log 2>&1 & echo 'Bot started'
"@
echo $PASSWORD | ssh -o StrictHostKeyChecking=no $SERVER $startCmd

# Step 5: Check bot status
Write-Host "📊 Checking bot status..." -ForegroundColor Yellow
Start-Sleep -Seconds 3
$statusCmd = @"
cd bot && if pgrep -f 'python3 app/main.py' > /dev/null; then echo 'Bot is running!'; tail -n 10 bot.log; else echo 'Bot not running. Logs:'; tail -n 20 bot.log; fi
"@
echo $PASSWORD | ssh -o StrictHostKeyChecking=no $SERVER $statusCmd

Write-Host "🎉 Deployment completed!" -ForegroundColor Green
