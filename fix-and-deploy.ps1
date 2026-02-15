# Decision Audit System - Complete Fix and Deploy Script

$ErrorActionPreference = "Continue"

Write-Host "=================================" -ForegroundColor Cyan
Write-Host "Decision Audit System - Auto Fix" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""

$PROJECT_ROOT = "C:\Users\91832\Desktop\decision-audit-system"
$MONGODB_URL = "mongodb+srv://admin:ceay9evfdBcpBcoi@decision-audit-cluster.ybumdfm.mongodb.net/decision_audit?retryWrites=true&w=majority&appName=decision-audit-cluster"

Set-Location $PROJECT_ROOT

# Step 1: Fix requirements.txt
Write-Host "Step 1: Fixing requirements.txt..." -ForegroundColor Yellow

@"
fastapi==0.109.0
uvicorn[standard]==0.27.0
gunicorn==21.2.0
motor==3.3.2
pymongo==4.6.1
pydantic==2.5.3
pydantic-settings==2.1.0
python-dotenv==1.0.0
"@ | Out-File -FilePath "backend\requirements.txt" -Encoding ascii

Write-Host "Done: requirements.txt updated" -ForegroundColor Green

# Step 2: Create runtime.txt
Write-Host "Step 2: Creating runtime.txt..." -ForegroundColor Yellow
"python-3.11.0" | Out-File -FilePath "backend\runtime.txt" -Encoding ascii
Write-Host "Done: runtime.txt created" -ForegroundColor Green

# Step 3: Create Procfile
Write-Host "Step 3: Creating Procfile..." -ForegroundColor Yellow
'web: gunicorn app.main:app --workers 1 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT --timeout 120' | Out-File -FilePath "backend\Procfile" -Encoding ascii -NoNewline
Write-Host "Done: Procfile created" -ForegroundColor Green

# Step 4: Test MongoDB
Write-Host ""
Write-Host "Step 4: Testing MongoDB connection..." -ForegroundColor Yellow

Set-Location backend
& ..\venv\Scripts\Activate.ps1

$env:MONGODB_URL = $MONGODB_URL

python -c "import asyncio; from motor.motor_asyncio import AsyncIOMotorClient; asyncio.run(AsyncIOMotorClient('$MONGODB_URL').admin.command('ping')); print('MongoDB OK')"

# Step 5: Install dependencies
Write-Host ""
Write-Host "Step 5: Installing dependencies..." -ForegroundColor Yellow
pip install -q -r requirements.txt
Write-Host "Done: Dependencies installed" -ForegroundColor Green

# Step 6: Test startup
Write-Host ""
Write-Host "Step 6: Testing backend..." -ForegroundColor Yellow
$env:DATABASE_NAME = "decision_audit"
$env:SECRET_KEY = "test-key"

python -c "import asyncio; from app.core.database import connect_db; asyncio.run(connect_db()); print('Backend OK')"

Set-Location ..

# Step 7: Push to GitHub
Write-Host ""
Write-Host "Step 7: Pushing to GitHub..." -ForegroundColor Yellow
git add .
git commit -m "Fix for deployment"
git push
Write-Host "Done: Pushed to GitHub" -ForegroundColor Green

Write-Host ""
Write-Host "=================================" -ForegroundColor Green
Write-Host "ALL FIXES COMPLETE!" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green
Write-Host ""
Write-Host "NEXT: Deploy on Render" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Go to: https://render.com" -ForegroundColor White
Write-Host "2. Sign in with GitHub" -ForegroundColor White
Write-Host "3. New -> Web Service" -ForegroundColor White
Write-Host "4. Connect: decision-audit-system" -ForegroundColor White
Write-Host "5. Settings:" -ForegroundColor White
Write-Host "   Root Directory: backend" -ForegroundColor Gray
Write-Host "   Build: pip install -r requirements.txt" -ForegroundColor Gray  
Write-Host "   Start: gunicorn app.main:app -w 1 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:`$PORT" -ForegroundColor Gray
Write-Host "6. Add these Environment Variables:" -ForegroundColor White
Write-Host "   MONGODB_URL" -ForegroundColor Gray
Write-Host "   DATABASE_NAME = decision_audit" -ForegroundColor Gray
Write-Host "   SECRET_KEY = production-key-123" -ForegroundColor Gray
Write-Host ""
Write-Host "MongoDB URL (copy this):" -ForegroundColor Yellow
Write-Host $MONGODB_URL -ForegroundColor White
Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")