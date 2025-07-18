# Enhanced Setup Script for Emergency Hospital Bed Booking System (Windows)
# PowerShell version - Simplified and Fixed

param(
    [switch]$SkipRedis,
    [switch]$QuickSetup
)

Write-Host "🚀 Enhanced Emergency Hospital Bed Booking System Setup (Windows)" -ForegroundColor Cyan
Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[INFO] This script will set up the enhanced system with:" -ForegroundColor Green
Write-Host "  • Multi-factor authentication (MFA)"
Write-Host "  • Real-time bed availability updates"
Write-Host "  • Advanced security features"
Write-Host "  • Input validation and CSRF protection"
Write-Host "  • Rate limiting and session management"
Write-Host "  • Comprehensive audit logging"
Write-Host ""

if (-not $QuickSetup) {
    $response = Read-Host "Continue with setup? (y/N)"
    if ($response -ne 'y' -and $response -ne 'Y') {
        Write-Host "Setup cancelled."
        exit 0
    }
}

# Check if Python 3.8+ is installed
Write-Host "[STEP] Checking Python installation..." -ForegroundColor Blue

try {
    $pythonVersion = python --version 2>&1
    if ($pythonVersion -match "Python (\d+)\.(\d+)") {
        $major = [int]$matches[1]
        $minor = [int]$matches[2]
        
        if ($major -eq 3 -and $minor -ge 8) {
            Write-Host "[INFO] Python $($matches[0]) found ✓" -ForegroundColor Green
            $pythonCmd = "python"
        } else {
            Write-Host "[ERROR] Python 3.8+ required. Found $($matches[0])" -ForegroundColor Red
            exit 1
        }
    } else {
        Write-Host "[ERROR] Could not determine Python version" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "[ERROR] Python not found. Please install Python 3.8 or later from python.org" -ForegroundColor Red
    exit 1
}

# Check if pip is available
Write-Host "[STEP] Checking pip installation..." -ForegroundColor Blue
try {
    $pipVersion = pip --version 2>&1
    Write-Host "[INFO] pip found ✓" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] pip not found. Please ensure pip is installed and in PATH" -ForegroundColor Red
    exit 1
}

# Create virtual environment
Write-Host "[STEP] Setting up Python virtual environment..." -ForegroundColor Blue

if (-not (Test-Path "venv")) {
    Write-Host "[INFO] Creating virtual environment..." -ForegroundColor Green
    python -m venv venv
} else {
    Write-Host "[INFO] Virtual environment already exists ✓" -ForegroundColor Green
}

# Activate virtual environment
Write-Host "[INFO] Activating virtual environment..." -ForegroundColor Green
& "venv\Scripts\Activate.ps1"

# Upgrade pip
Write-Host "[INFO] Upgrading pip..." -ForegroundColor Green
pip install --upgrade pip

# Install Python dependencies
Write-Host "[STEP] Installing Python dependencies..." -ForegroundColor Blue

if (Test-Path "requirements.txt") {
    Write-Host "[INFO] Installing from requirements.txt..." -ForegroundColor Green
    pip install -r requirements.txt
    Write-Host "[INFO] Dependencies installed ✓" -ForegroundColor Green
} else {
    Write-Host "[ERROR] requirements.txt not found!" -ForegroundColor Red
    exit 1
}

# Create necessary directories
Write-Host "[STEP] Creating necessary directories..." -ForegroundColor Blue

$directories = @(
    "logs",
    "project\credentials",
    "project\uploads", 
    "project\static\uploads",
    "backups"
)

foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "[INFO] Created directory: $dir" -ForegroundColor Green
    }
}

# Setup configuration files
Write-Host "[STEP] Setting up configuration files..." -ForegroundColor Blue

# Copy .env template if not exists
if (-not (Test-Path ".env")) {
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
        Write-Host "[INFO] Created .env from template" -ForegroundColor Green
        Write-Host "[WARNING] Please edit .env file with your actual configuration values" -ForegroundColor Yellow
    } else {
        Write-Host "[ERROR] .env.example not found!" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "[INFO] .env file already exists ✓" -ForegroundColor Green
}

# Generate secure keys
Write-Host "[STEP] Generating secure keys..." -ForegroundColor Blue

$secretKey = python -c "import secrets; print(secrets.token_urlsafe(32))"
$csrfSecretKey = python -c "import secrets; print(secrets.token_urlsafe(32))"

# Update .env file with secure keys
if (Test-Path ".env") {
    $envContent = Get-Content ".env"
    
    # Replace or add SECRET_KEY
    if ($envContent -match "SECRET_KEY=") {
        $envContent = $envContent -replace "SECRET_KEY=.*", "SECRET_KEY=$secretKey"
    } else {
        $envContent += "SECRET_KEY=$secretKey"
    }
    
    # Replace or add CSRF_SECRET_KEY
    if ($envContent -match "CSRF_SECRET_KEY=") {
        $envContent = $envContent -replace "CSRF_SECRET_KEY=.*", "CSRF_SECRET_KEY=$csrfSecretKey"
    } else {
        $envContent += "CSRF_SECRET_KEY=$csrfSecretKey"
    }
    
    $envContent | Set-Content ".env"
    Write-Host "[INFO] Secure keys generated and added to .env ✓" -ForegroundColor Green
}

# Check Redis (optional)
if (-not $SkipRedis) {
    Write-Host "[STEP] Checking Redis installation..." -ForegroundColor Blue
    
    try {
        redis-cli ping 2>&1 | Out-Null
        Write-Host "[INFO] Redis is running ✓" -ForegroundColor Green
    } catch {
        Write-Host "[WARNING] Redis not found or not running." -ForegroundColor Yellow
        Write-Host "Redis is recommended for enhanced real-time features."
        Write-Host "You can:"
        Write-Host "  1. Install Redis using WSL (Windows Subsystem for Linux)"
        Write-Host "  2. Use Redis Docker container"
        Write-Host "  3. Install Redis on Windows (memurai.com)"
        Write-Host "  4. Skip Redis for now (re-run with -SkipRedis)"
    }
}

# Create startup scripts
Write-Host "[STEP] Creating startup scripts..." -ForegroundColor Blue

# Create PowerShell startup script
$startAppPS1 = @'
# Startup script for Enhanced Emergency Hospital Bed Booking System (Windows)

Write-Host "🚀 Starting Enhanced Emergency Hospital Bed Booking System..." -ForegroundColor Cyan

# Activate virtual environment
& "venv\Scripts\Activate.ps1"

# Check if Redis is running (for real-time features)
try {
    redis-cli ping 2>$null | Out-Null
    Write-Host "📡 Redis connected - Real-time features enabled" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Warning: Redis is not running. Real-time features will be limited." -ForegroundColor Yellow
    Write-Host "   You can start Redis or use Docker: docker run -d -p 6379:6379 redis"
}

# Set environment variables
$env:FLASK_APP = "project.enhanced_main"
$env:FLASK_ENV = "development"

# Start the application
Write-Host "🌐 Starting with real-time WebSocket support..." -ForegroundColor Blue
python project\enhanced_main.py
'@

$startAppPS1 | Out-File -FilePath "start_app.ps1" -Encoding UTF8

# Create batch file for compatibility
$startAppBat = @'
@echo off
echo 🚀 Starting Enhanced Emergency Hospital Bed Booking System...

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Check for Redis
redis-cli ping >nul 2>&1
if %errorlevel% equ 0 (
    echo 📡 Redis connected - Real-time features enabled
) else (
    echo ⚠️  Warning: Redis is not running. Real-time features will be limited.
)

REM Set environment variables
set FLASK_APP=project.enhanced_main
set FLASK_ENV=development

REM Start the application
echo 🌐 Starting with real-time WebSocket support...
python project\enhanced_main.py

pause
'@

$startAppBat | Out-File -FilePath "start_app.bat" -Encoding ASCII

Write-Host "[INFO] Created startup scripts (start_app.ps1 and start_app.bat) ✓" -ForegroundColor Green

# Create database migration script
Write-Host "[STEP] Creating development tools..." -ForegroundColor Blue

$migrationScript = @'
#!/usr/bin/env python3
"""
Database migration utility for Emergency Hospital Bed Booking System (Windows)
"""

import sys
import os
sys.path.append('project')

from enhanced_main import app, db, User, Hospitaluser, Hospitaldata

def create_tables():
    """Create all database tables"""
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        print("✓ Tables created successfully")

def create_admin_user():
    """Create default admin user"""
    with app.app_context():
        admin = User.query.filter_by(email='admin@hospital.com').first()
        if not admin:
            admin = User(
                email='admin@hospital.com',
                is_admin=True,
                dob='1990-01-01'
            )
            admin.set_password('SecureAdmin123!')
            db.session.add(admin)
            db.session.commit()
            print("✓ Default admin user created: admin@hospital.com / SecureAdmin123!")
        else:
            print("✓ Admin user already exists")

if __name__ == '__main__':
    create_tables()
    create_admin_user()
    print("\n🎉 Database setup complete!")
    print("You can now start the application with: start_app.ps1")
'@

$migrationScript | Out-File -FilePath "migrate_db.py" -Encoding UTF8

# Create test script
$testScript = @'
#!/usr/bin/env python3
"""
Test script for enhanced features (Windows)
"""

import sys
import os
sys.path.append('project')

def test_imports():
    """Test if all enhanced modules can be imported"""
    try:
        from services.validation_service import validator
        from services.security_service import SecurityService
        from services.auth_service import AuthenticationService
        from services.realtime_service import RealTimeService
        from forms.secure_forms import UserRegistrationForm
        print("✓ All enhanced modules imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_config():
    """Test configuration loading"""
    try:
        from config.secure_config import get_config
        config = get_config()
        print("✓ Configuration loaded successfully")
        return True
    except Exception as e:
        print(f"✗ Configuration error: {e}")
        return False

def test_redis_connection():
    """Test Redis connection"""
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.ping()
        print("✓ Redis connection successful")
        return True
    except Exception as e:
        print(f"✗ Redis connection failed: {e}")
        print("  Note: Redis is optional but recommended for real-time features")
        return False

if __name__ == '__main__':
    print("🧪 Testing enhanced features...\n")
    
    tests = [
        ("Module imports", test_imports),
        ("Configuration", test_config),
        ("Redis connection", test_redis_connection)
    ]
    
    passed = 0
    for test_name, test_func in tests:
        print(f"Testing {test_name}...")
        if test_func():
            passed += 1
        print()
    
    print(f"Results: {passed}/{len(tests)} tests passed")
    
    if passed >= 2:  # Redis is optional
        print("🎉 Essential tests passed! The enhanced system is ready.")
    else:
        print("⚠️  Some critical tests failed. Please check the configuration.")
'@

$testScript | Out-File -FilePath "test_features.py" -Encoding UTF8

Write-Host "[INFO] Created development tools ✓" -ForegroundColor Green

# Final output
Write-Host ""
Write-Host "🎉 Enhanced setup completed successfully!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

Write-Host "[INFO] Next steps:" -ForegroundColor Green
Write-Host "1. Edit .env file with your actual configuration values"
Write-Host "2. Edit project\templates\config.json with database credentials"
Write-Host "3. Create MySQL database: CREATE DATABASE emergency_bed;"
Write-Host "4. Run database migration: python migrate_db.py"
Write-Host "5. Test the setup: python test_features.py"
Write-Host "6. Start the application: .\start_app.ps1 (or start_app.bat)"
Write-Host ""

Write-Host "[WARNING] Important Security Notes:" -ForegroundColor Yellow
Write-Host "• Change default admin password after first login"
Write-Host "• Enable MFA for all admin accounts"
Write-Host "• Configure Firebase credentials for file uploads"
Write-Host "• Set up SSL/TLS for production deployment"
Write-Host ""

Write-Host "[INFO] For detailed documentation, see ENHANCED_USER_GUIDE.md" -ForegroundColor Green
Write-Host ""
Write-Host "[INFO] Setup complete! Your enhanced emergency bed booking system is ready." -ForegroundColor Green

# Open .env file for editing if requested
if (-not $QuickSetup) {
    $editConfig = Read-Host "Would you like to edit the .env configuration file now? (y/N)"
    if ($editConfig -eq 'y' -or $editConfig -eq 'Y') {
        if (Get-Command notepad -ErrorAction SilentlyContinue) {
            notepad .env
        } else {
            Write-Host "Please edit .env file with your preferred text editor"
        }
    }
}
