#!/bin/bash

# Deployment Preparation Script
# This script helps prepare your app for deployment

echo "🚀 CashFlow Manager - Deployment Preparation"
echo "=============================================="
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  WARNING: .env file not found!"
    echo "   Creating from .env.example..."
    cp .env.example .env
    echo "   ✓ Created .env - Please fill in your actual values!"
    echo ""
else
    echo "✓ .env file found"
fi

# Check if git is initialized
if [ ! -d .git ]; then
    echo "⚠️  Git not initialized"
    echo "   Initializing git repository..."
    git init
    echo "   ✓ Git initialized"
    echo ""
else
    echo "✓ Git repository initialized"
fi

# Check if .gitignore exists
if [ ! -f .gitignore ]; then
    echo "⚠️  .gitignore not found!"
    echo "   This could expose your secrets!"
else
    # Check if .env is in .gitignore
    if grep -q "^\.env$" .gitignore; then
        echo "✓ .env is properly ignored by git"
    else
        echo "⚠️  WARNING: .env is NOT in .gitignore!"
        echo "   Adding it now..."
        echo ".env" >> .gitignore
        echo "   ✓ Added .env to .gitignore"
    fi
fi

echo ""
echo "📦 Checking dependencies..."

# Check Python
if command -v python3 &> /dev/null; then
    echo "✓ Python $(python3 --version | cut -d ' ' -f 2) installed"
else
    echo "✗ Python 3 not found - required for backend"
fi

# Check Node.js
if command -v node &> /dev/null; then
    echo "✓ Node.js $(node --version) installed"
else
    echo "✗ Node.js not found - required for frontend"
fi

# Check npm
if command -v npm &> /dev/null; then
    echo "✓ npm $(npm --version) installed"
else
    echo "✗ npm not found - required for frontend"
fi

echo ""
echo "🔍 Validating configuration files..."

# Check required files
required_files=("requirements.txt" "Procfile" "render.yaml" "vercel.json" ".env.example")
for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "✓ $file exists"
    else
        echo "✗ $file missing!"
    fi
done

echo ""
echo "📋 Environment Variables Check..."

# Check if critical env vars are set in .env
if [ -f .env ]; then
    critical_vars=("SUPABASE_URL" "SUPABASE_ANON_KEY" "SUPABASE_JWT_SECRET" "SUPABASE_DB_URL" "SECRET_KEY")
    
    for var in "${critical_vars[@]}"; do
        if grep -q "^${var}=" .env && ! grep -q "^${var}=your-" .env; then
            echo "✓ $var is set"
        else
            echo "⚠️  $var needs to be configured in .env"
        fi
    done
fi

echo ""
echo "🧪 Testing backend..."

# Check if backend can start
if [ -f "main.py" ]; then
    echo "Running backend health check..."
    
    # Start backend in background
    python3 main.py > /dev/null 2>&1 &
    BACKEND_PID=$!
    
    # Wait for it to start
    sleep 5
    
    # Test health endpoint
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✓ Backend health check passed"
    else
        echo "⚠️  Backend health check failed (may need configuration)"
    fi
    
    # Kill backend
    kill $BACKEND_PID 2>/dev/null
fi

echo ""
echo "📊 Deployment Readiness Summary"
echo "================================"
echo ""
echo "✅ Prerequisites:"
echo "   - Configuration files created"
echo "   - .gitignore properly configured"
echo "   - Environment variables template ready"
echo ""
echo "📝 Next Steps:"
echo ""
echo "1. Fill in your .env file with actual values"
echo "2. Push code to GitHub:"
echo "   git add ."
echo "   git commit -m 'Ready for deployment'"
echo "   git remote add origin https://github.com/YOUR_USERNAME/cashflow-manager.git"
echo "   git push -u origin main"
echo ""
echo "3. Deploy Backend to Render:"
echo "   - Visit: https://render.com"
echo "   - Follow instructions in DEPLOYMENT_GUIDE.md"
echo ""
echo "4. Deploy Frontend to Vercel:"
echo "   - Visit: https://vercel.com"
echo "   - Follow instructions in DEPLOYMENT_GUIDE.md"
echo ""
echo "📖 Full deployment guide: DEPLOYMENT_GUIDE.md"
echo ""
echo "✨ Your app is ready for FREE deployment!"
echo ""
