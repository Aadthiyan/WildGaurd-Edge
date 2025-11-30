#!/bin/bash
# WildGaurd-Edge Quick Deployment Script for Railway

echo "🚀 WildGaurd-Edge Quick Deployment"
echo "=================================="
echo ""

# Check if requirements.txt exists
if [ ! -f "requirements.txt" ]; then
    echo "📦 Creating requirements.txt..."
    pip freeze > requirements.txt
    echo "✅ requirements.txt created"
fi

# Check if runtime.txt exists
if [ ! -f "runtime.txt" ]; then
    echo "📝 Creating runtime.txt..."
    cat > runtime.txt << EOF
python-3.13.7
EOF
    echo "✅ runtime.txt created"
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚙️ Creating .env for production..."
    cat > .env << EOF
FLASK_ENV=production
FLASK_DEBUG=0
PORT=5000
NODE_ENV=production
EOF
    echo "✅ .env created"
fi

echo ""
echo "🔧 Next Steps:"
echo "1. Go to https://railway.app"
echo "2. Create account and connect GitHub"
echo "3. Create new project from WildGaurd-Edge repo"
echo "4. Railway will auto-detect Python + Node.js"
echo "5. Deploy!"
echo ""
echo "📚 For detailed instructions, see: DEPLOYMENT_GUIDE.md"
echo ""
echo "✨ Your app will be live in 2-3 minutes!"
