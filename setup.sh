#!/bin/bash

# Emergency Hospital Bed Booking System - Setup Script
# This script helps set up the application securely

echo "🏥 Emergency Hospital Bed Booking System Setup"
echo "=============================================="

# Check if running on Windows (Git Bash/WSL)
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" || "$OSTYPE" == "win32" ]]; then
    IS_WINDOWS=true
else
    IS_WINDOWS=false
fi

# Create virtual environment
echo "📦 Setting up Python virtual environment..."
python -m venv venv

if [ "$IS_WINDOWS" = true ]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

# Install dependencies
echo "📥 Installing Python dependencies..."
pip install -r requirements.txt

# Setup environment file
echo "⚙️ Setting up environment configuration..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✅ Created .env file from template"
    echo "⚠️  Please edit .env with your actual configuration values"
else
    echo "ℹ️  .env file already exists"
fi

# Setup config file
echo "🗄️ Setting up database configuration..."
if [ ! -f project/templates/config.json ]; then
    cp project/templates/config.json.example project/templates/config.json
    echo "✅ Created config.json from template"
    echo "⚠️  Please edit project/templates/config.json with your database credentials"
else
    echo "ℹ️  config.json file already exists"
fi

# Set secure permissions (Unix/Linux/Mac only)
if [ "$IS_WINDOWS" = false ]; then
    echo "🔒 Setting secure file permissions..."
    chmod 600 .env 2>/dev/null || echo "⚠️  Could not set permissions for .env"
    chmod 600 project/templates/config.json 2>/dev/null || echo "⚠️  Could not set permissions for config.json"
fi

# Firebase setup reminder
echo ""
echo "🔥 Firebase Setup Required:"
echo "1. Go to https://console.firebase.google.com/"
echo "2. Create or select your project"
echo "3. Go to Project Settings → Service Accounts"
echo "4. Click 'Generate new private key'"
echo "5. Save the downloaded file as: project/firebase-credentials.json"

if [ "$IS_WINDOWS" = false ]; then
    echo "6. Run: chmod 600 project/firebase-credentials.json"
fi

echo ""
echo "📋 Next Steps:"
echo "1. Edit .env with your configuration"
echo "2. Edit project/templates/config.json with your database credentials"
echo "3. Set up Firebase credentials as described above"
echo "4. Create MySQL database: CREATE DATABASE emergency_bed;"
echo "5. Run: python project/main.py"
echo ""
echo "⚠️  SECURITY REMINDER:"
echo "   Never commit .env, config.json, or firebase-credentials.json to version control!"
echo ""
echo "✅ Setup complete! Please follow the next steps above."
