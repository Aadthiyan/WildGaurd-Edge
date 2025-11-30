# WildGaurd-Edge Quick Deployment Script for Windows
# This script prepares your app for public deployment

Write-Host "🚀 WildGaurd-Edge Deployment Preparation" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Create requirements.txt if not exists
if (!(Test-Path "requirements.txt")) {
    Write-Host "📦 Creating requirements.txt..." -ForegroundColor Yellow
    & .\.venv\Scripts\pip freeze | Out-File -Encoding UTF8 requirements.txt
    Write-Host "✅ requirements.txt created" -ForegroundColor Green
}

# Create runtime.txt if not exists
if (!(Test-Path "runtime.txt")) {
    Write-Host "📝 Creating runtime.txt..." -ForegroundColor Yellow
    @"
python-3.13.7
"@ | Out-File -Encoding UTF8 runtime.txt
    Write-Host "✅ runtime.txt created" -ForegroundColor Green
}

# Create .env if not exists
if (!(Test-Path ".env")) {
    Write-Host "⚙️ Creating .env for production..." -ForegroundColor Yellow
    @"
FLASK_ENV=production
FLASK_DEBUG=0
PORT=5000
NODE_ENV=production
"@ | Out-File -Encoding UTF8 .env
    Write-Host "✅ .env created" -ForegroundColor Green
}

Write-Host ""
Write-Host "🌐 Deployment Platforms (Choose One):" -ForegroundColor Cyan
Write-Host ""
Write-Host "1️⃣ Railway (⭐ Recommended)" -ForegroundColor Green
Write-Host "   - Cost: \$5-20/month"
Write-Host "   - Setup: Very easy"
Write-Host "   - Deploy: https://railway.app"
Write-Host ""

Write-Host "2️⃣ Heroku" -ForegroundColor Blue
Write-Host "   - Cost: \$7-50/month (no free tier)"
Write-Host "   - Setup: Very easy"
Write-Host "   - Deploy: https://www.heroku.com"
Write-Host ""

Write-Host "3️⃣ AWS" -ForegroundColor Magenta
Write-Host "   - Cost: Free 1 year, then \$10+/month"
Write-Host "   - Setup: Medium difficulty"
Write-Host "   - Deploy: https://aws.amazon.com"
Write-Host ""

Write-Host "4️⃣ DigitalOcean" -ForegroundColor Cyan
Write-Host "   - Cost: \$4-6/month"
Write-Host "   - Setup: Medium difficulty"
Write-Host "   - Deploy: https://www.digitalocean.com"
Write-Host ""

Write-Host "📚 Full deployment guide:" -ForegroundColor Yellow
Write-Host "   See DEPLOYMENT_GUIDE.md for detailed instructions"
Write-Host ""

Write-Host "🎯 Quick Start with Railway:" -ForegroundColor Green
Write-Host "   1. Go to https://railway.app"
Write-Host "   2. Click 'Create Project' → 'Deploy from GitHub'"
Write-Host "   3. Select WildGaurd-Edge repository"
Write-Host "   4. Click 'Deploy'"
Write-Host "   5. Wait 2-3 minutes for your public URL"
Write-Host ""

Write-Host "✨ Your app will be publicly accessible in minutes!" -ForegroundColor Green
Write-Host ""

# Optional: Commit changes
Write-Host "💡 Tip: Commit these files to GitHub before deploying:" -ForegroundColor Cyan
Write-Host "   git add requirements.txt runtime.txt .env"
Write-Host "   git commit -m 'Prepare for public deployment'"
Write-Host "   git push origin main"
Write-Host ""
