# Enhanced Setup Script for Emergency Hospital Bed Booking System (Windows)
# PowerShell version for Windows users

param(
    [switch]$SkipRedis,
    [switch]$QuickSetup
)

# Color codes for output
function Write-Status {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

function Write-Step {
    param([string]$Message)
    Write-Host "[STEP] $Message" -ForegroundColor Blue
}

Write-Host "🚀 Enhanced Emergency Hospital Bed Booking System Setup (Windows)" -ForegroundColor Cyan
Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Status "This script will set up the enhanced system with:"
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
Write-Step "Checking Python installation..."

try {
    $pythonVersion = python --version 2>&1
    if ($pythonVersion -match "Python (\d+)\.(\d+)") {
        $major = [int]$matches[1]
        $minor = [int]$matches[2]
        
        if ($major -eq 3 -and $minor -ge 8) {
            Write-Status "Python $($matches[0]) found ✓"
            $pythonCmd = "python"
        }
        else {
            Write-Error "Python 3.8+ required. Found $($matches[0])"
            exit 1
        }
    }
    else {
        Write-Error "Could not determine Python version"
        exit 1
    }
}
catch {
    Write-Error "Python not found. Please install Python 3.8 or later from python.org"
    exit 1
}

# Check if pip is available
Write-Step "Checking pip installation..."
try {
    $pipVersion = pip --version 2>&1
    Write-Status "pip found ✓"
}
catch {
    Write-Error "pip not found. Please ensure pip is installed and in PATH"
    exit 1
}

# Create virtual environment
Write-Step "Setting up Python virtual environment..."

if (-not (Test-Path "venv")) {
    Write-Status "Creating virtual environment..."
    python -m venv venv
}
else {
    Write-Status "Virtual environment already exists ✓"
}

# Activate virtual environment
Write-Status "Activating virtual environment..."
& "venv\Scripts\Activate.ps1"

# Upgrade pip
Write-Status "Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
Write-Step "Installing Python dependencies..."

if (Test-Path "requirements.txt") {
    Write-Status "Installing from requirements.txt..."
    pip install -r requirements.txt
    Write-Status "Dependencies installed ✓"
}
else {
    Write-Error "requirements.txt not found!"
    exit 1
}

# Create necessary directories
Write-Step "Creating necessary directories..."

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
        Write-Status "Created directory: $dir"
    }
}

# Setup configuration files
Write-Step "Setting up configuration files..."

# Copy .env template if not exists
if (-not (Test-Path ".env")) {
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
        Write-Status "Created .env from template"
        Write-Warning "Please edit .env file with your actual configuration values"
    }
    else {
        Write-Error ".env.example not found!"
        exit 1
    }
}
else {
    Write-Status ".env file already exists ✓"
}

# Generate secure keys
Write-Step "Generating secure keys..."

$secretKey = python -c "import secrets; print(secrets.token_urlsafe(32))"
$csrfSecretKey = python -c "import secrets; print(secrets.token_urlsafe(32))"

# Update .env file with secure keys
if (Test-Path ".env") {
    $envContent = Get-Content ".env"
    
    # Replace or add SECRET_KEY
    if ($envContent -match "SECRET_KEY=") {
        $envContent = $envContent -replace "SECRET_KEY=.*", "SECRET_KEY=$secretKey"
    }
    else {
        $envContent += "SECRET_KEY=$secretKey"
    }
    
    # Replace or add CSRF_SECRET_KEY
    if ($envContent -match "CSRF_SECRET_KEY=") {
        $envContent = $envContent -replace "CSRF_SECRET_KEY=.*", "CSRF_SECRET_KEY=$csrfSecretKey"
    }
    else {
        $envContent += "CSRF_SECRET_KEY=$csrfSecretKey"
    }
    
    $envContent | Set-Content ".env"
    Write-Status "Secure keys generated and added to .env ✓"
}

# Check Redis (optional)
if (-not $SkipRedis) {
    Write-Step "Checking Redis installation..."
    
    try {
        redis-cli ping 2>&1 | Out-Null
        Write-Status "Redis is running ✓"
    }
    catch {
        Write-Warning "Redis not found or not running."
        Write-Host "Redis is recommended for enhanced real-time features."
        Write-Host "You can:"
        Write-Host "  1. Install Redis using WSL (Windows Subsystem for Linux)"
        Write-Host "  2. Use Redis Docker container"
        Write-Host "  3. Install Redis on Windows (memurai.com)"
        Write-Host "  4. Skip Redis for now (re-run with -SkipRedis)"
    }
}

# Create startup script
Write-Step "Creating startup scripts..."

# PowerShell startup script
$startAppContent = @'
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

$startAppContent | Out-File -FilePath "start_app.ps1" -Encoding UTF8

# Batch file for compatibility
$batchContent = @'
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

$batchContent | Out-File -FilePath "start_app.bat" -Encoding ASCII

Write-Status "Created startup scripts (start_app.ps1 and start_app.bat) ✓"

# Create database migration script
Write-Step "Creating development tools..."

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

# Test script
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

Write-Status "Created development tools ✓"

# Final output
Write-Host ""
Write-Host "🎉 Enhanced setup completed successfully!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

Write-Status "Next steps:"
Write-Host "1. Edit .env file with your actual configuration values"
Write-Host "2. Edit project\templates\config.json with database credentials"
Write-Host "3. Create MySQL database: CREATE DATABASE emergency_bed;"
Write-Host "4. Run database migration: python migrate_db.py"
Write-Host "5. Test the setup: python test_features.py"
Write-Host "6. Start the application: .\start_app.ps1 (or start_app.bat)"
Write-Host ""

Write-Warning "Important Security Notes:"
Write-Host "• Change default admin password after first login"
Write-Host "• Enable MFA for all admin accounts"
Write-Host "• Configure Firebase credentials for file uploads"
Write-Host "• Set up SSL/TLS for production deployment"
Write-Host ""

Write-Status "For detailed documentation, see ENHANCEMENT_ROADMAP.md"
Write-Host ""
Write-Status "Setup complete! Your enhanced emergency bed booking system is ready."

# Open .env file for editing if requested
if (-not $QuickSetup) {
    $editConfig = Read-Host "Would you like to edit the .env configuration file now? (y/N)"
    if ($editConfig -eq 'y' -or $editConfig -eq 'Y') {
        if (Get-Command notepad -ErrorAction SilentlyContinue) {
            notepad .env
        }
        else {
            Write-Host "Please edit .env file with your preferred text editor"
        }
    }
}
