# AlwaysData server deployment script (PowerShell)
# This script deploys the bot to AlwaysData server
# Uses working_bot.py for reliable operation

Write-Host "🚀 Starting deployment to AlwaysData server..." -ForegroundColor Green
Write-Host ""

# Server details
$SERVER = "doniyoebrk@ssh-doniyoebrk.alwaysdata.net"

Write-Host "⚠️  IMPORTANT: For 24/7 operation, configure bot as AlwaysData Service" -ForegroundColor Yellow
Write-Host "   See ALWAYSDATA_SERVICE_SETUP.md for instructions" -ForegroundColor Yellow
Write-Host ""

# Step 1: Push to GitHub
Write-Host "� Pushing code to GitHub..." -ForegroundColor Cyan
git add .
git commit -m "Update bot configuration"
git push origin main
Write-Host "✅ Code pushed to GitHub" -ForegroundColor Green
Write-Host ""

# Step 2: Connect to server and run deployment script
Write-Host "� Connecting to AlwaysData server..." -ForegroundColor Cyan
Write-Host "   Server: $SERVER" -ForegroundColor Gray
Write-Host ""

$deployCmd = @"
cd ~/bot && \
git pull origin main && \
chmod +x quick_restart.sh && \
chmod +x alwaysdata_service.sh && \
./quick_restart.sh
"@

Write-Host "� Executing deployment on server..." -ForegroundColor Cyan
ssh -o StrictHostKeyChecking=no $SERVER $deployCmd

Write-Host ""
Write-Host "🎉 Deployment completed!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Next Steps:" -ForegroundColor Yellow
Write-Host "   1. Test bot: Send /start to @GuruhAgent_bot" -ForegroundColor White
Write-Host "   2. For 24/7 operation: Configure as Service (see ALWAYSDATA_SERVICE_SETUP.md)" -ForegroundColor White
Write-Host "   3. View logs: ssh $SERVER 'screen -r hudud_bot'" -ForegroundColor White
Write-Host ""
