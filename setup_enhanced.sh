#!/bin/bash

# Enhanced Setup Script for Emergency Hospital Bed Booking System
# Installs all critical priority features including security and real-time functionality

set -e  # Exit on any error

echo "🚀 Setting up Enhanced Emergency Hospital Bed Booking System..."
echo "=================================================="

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Check if Python 3.8+ is installed
check_python() {
    print_step "Checking Python installation..."
    
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
        PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
        PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
        
        if [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -ge 8 ]; then
            print_status "Python $PYTHON_VERSION found ✓"
            PYTHON_CMD="python3"
        else
            print_error "Python 3.8+ required. Found Python $PYTHON_VERSION"
            exit 1
        fi
    else
        print_error "Python 3 not found. Please install Python 3.8 or later."
        exit 1
    fi
}

# Check if MySQL is available
check_mysql() {
    print_step "Checking MySQL installation..."
    
    if command -v mysql &> /dev/null; then
        print_status "MySQL client found ✓"
    else
        print_warning "MySQL client not found. Please ensure MySQL is installed and accessible."
    fi
}

# Check if Redis is available
check_redis() {
    print_step "Checking Redis installation..."
    
    if command -v redis-server &> /dev/null; then
        print_status "Redis server found ✓"
        
        # Check if Redis is running
        if redis-cli ping &> /dev/null; then
            print_status "Redis is running ✓"
        else
            print_warning "Redis is not running. Starting Redis..."
            if command -v systemctl &> /dev/null; then
                sudo systemctl start redis-server || print_warning "Could not start Redis automatically"
            else
                print_warning "Please start Redis manually: redis-server"
            fi
        fi
    else
        print_warning "Redis not found. Installing Redis is recommended for enhanced features."
        echo "To install Redis:"
        echo "  Ubuntu/Debian: sudo apt-get install redis-server"
        echo "  CentOS/RHEL: sudo yum install redis"
        echo "  macOS: brew install redis"
    fi
}

# Create virtual environment
setup_virtual_environment() {
    print_step "Setting up Python virtual environment..."
    
    if [ ! -d "venv" ]; then
        print_status "Creating virtual environment..."
        $PYTHON_CMD -m venv venv
    else
        print_status "Virtual environment already exists ✓"
    fi
    
    # Activate virtual environment
    print_status "Activating virtual environment..."
    source venv/bin/activate
    
    # Upgrade pip
    print_status "Upgrading pip..."
    pip install --upgrade pip
}

# Install Python dependencies
install_dependencies() {
    print_step "Installing Python dependencies..."
    
    if [ -f "requirements.txt" ]; then
        print_status "Installing from requirements.txt..."
        pip install -r requirements.txt
        print_status "Dependencies installed ✓"
    else
        print_error "requirements.txt not found!"
        exit 1
    fi
}

# Create necessary directories
create_directories() {
    print_step "Creating necessary directories..."
    
    directories=(
        "logs"
        "project/credentials"
        "project/uploads"
        "project/static/uploads"
        "backups"
    )
    
    for dir in "${directories[@]}"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir"
            print_status "Created directory: $dir"
        fi
    done
}

# Setup configuration files
setup_configuration() {
    print_step "Setting up configuration files..."
    
    # Copy .env template if not exists
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            cp .env.example .env
            print_status "Created .env from template"
            print_warning "Please edit .env file with your actual configuration values"
        else
            print_error ".env.example not found!"
            exit 1
        fi
    else
        print_status ".env file already exists ✓"
    fi
    
    # Create config.json template if not exists
    if [ ! -f "project/templates/config.json" ]; then
        if [ -f "project/templates/config.json.example" ]; then
            cp project/templates/config.json.example project/templates/config.json
            print_status "Created config.json from template"
            print_warning "Please edit project/templates/config.json with your database credentials"
        fi
    fi
}

# Generate secure keys
generate_secure_keys() {
    print_step "Generating secure keys..."
    
    # Generate SECRET_KEY for Flask
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
    CSRF_SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
    
    # Update .env file with secure keys
    if [ -f ".env" ]; then
        # Replace or add SECRET_KEY
        if grep -q "SECRET_KEY=" .env; then
            sed -i "s/SECRET_KEY=.*/SECRET_KEY=$SECRET_KEY/" .env
        else
            echo "SECRET_KEY=$SECRET_KEY" >> .env
        fi
        
        # Replace or add CSRF_SECRET_KEY
        if grep -q "CSRF_SECRET_KEY=" .env; then
            sed -i "s/CSRF_SECRET_KEY=.*/CSRF_SECRET_KEY=$CSRF_SECRET_KEY/" .env
        else
            echo "CSRF_SECRET_KEY=$CSRF_SECRET_KEY" >> .env
        fi
        
        print_status "Secure keys generated and added to .env ✓"
    fi
}

# Set secure file permissions
set_secure_permissions() {
    print_step "Setting secure file permissions..."
    
    # Secure configuration files
    if [ -f ".env" ]; then
        chmod 600 .env
        print_status "Set secure permissions for .env"
    fi
    
    if [ -f "project/templates/config.json" ]; then
        chmod 600 project/templates/config.json
        print_status "Set secure permissions for config.json"
    fi
    
    # Secure credentials directory
    if [ -d "project/credentials" ]; then
        chmod 700 project/credentials
        print_status "Set secure permissions for credentials directory"
    fi
    
    # Secure logs directory
    if [ -d "logs" ]; then
        chmod 755 logs
        print_status "Set permissions for logs directory"
    fi
}

# Create database
setup_database() {
    print_step "Setting up database..."
    
    print_warning "Database setup requires manual configuration:"
    echo "1. Create MySQL database: CREATE DATABASE emergency_bed;"
    echo "2. Update database credentials in .env file"
    echo "3. Update database credentials in project/templates/config.json"
    echo ""
    echo "The application will create tables automatically on first run."
}

# Create startup script
create_startup_script() {
    print_step "Creating startup script..."
    
    cat > start_app.sh << 'EOF'
#!/bin/bash

# Startup script for Enhanced Emergency Hospital Bed Booking System

echo "🚀 Starting Enhanced Emergency Hospital Bed Booking System..."

# Activate virtual environment
source venv/bin/activate

# Check if Redis is running (for real-time features)
if ! redis-cli ping &> /dev/null; then
    echo "⚠️  Warning: Redis is not running. Real-time features will be limited."
    echo "   Start Redis with: redis-server"
fi

# Set environment variables
export FLASK_APP=project.enhanced_main
export FLASK_ENV=development

# Start the application
echo "📡 Starting with real-time WebSocket support..."
python project/enhanced_main.py

EOF
    
    chmod +x start_app.sh
    print_status "Created start_app.sh script ✓"
}

# Create development tools
create_dev_tools() {
    print_step "Creating development tools..."
    
    # Database migration script
    cat > migrate_db.py << 'EOF'
#!/usr/bin/env python3
"""
Database migration utility for Emergency Hospital Bed Booking System
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
    print("You can now start the application with: ./start_app.sh")

EOF
    
    chmod +x migrate_db.py
    print_status "Created database migration script ✓"
    
    # Test script
    cat > test_features.py << 'EOF'
#!/usr/bin/env python3
"""
Test script for enhanced features
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
    
    if passed == len(tests):
        print("🎉 All tests passed! The enhanced system is ready.")
    else:
        print("⚠️  Some tests failed. Please check the configuration.")

EOF
    
    chmod +x test_features.py
    print_status "Created test script ✓"
}

# Main setup function
main() {
    echo "🚀 Enhanced Emergency Hospital Bed Booking System Setup"
    echo "======================================================="
    echo ""
    
    print_status "This script will set up the enhanced system with:"
    echo "  • Multi-factor authentication (MFA)"
    echo "  • Real-time bed availability updates"
    echo "  • Advanced security features"
    echo "  • Input validation and CSRF protection"
    echo "  • Rate limiting and session management"
    echo "  • Comprehensive audit logging"
    echo ""
    
    read -p "Continue with setup? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Setup cancelled."
        exit 0
    fi
    
    # Run setup steps
    check_python
    check_mysql
    check_redis
    setup_virtual_environment
    install_dependencies
    create_directories
    setup_configuration
    generate_secure_keys
    set_secure_permissions
    setup_database
    create_startup_script
    create_dev_tools
    
    echo ""
    echo "🎉 Enhanced setup completed successfully!"
    echo "========================================"
    echo ""
    print_status "Next steps:"
    echo "1. Edit .env file with your actual configuration values"
    echo "2. Edit project/templates/config.json with database credentials"
    echo "3. Create MySQL database: CREATE DATABASE emergency_bed;"
    echo "4. Run database migration: python migrate_db.py"
    echo "5. Test the setup: python test_features.py"
    echo "6. Start the application: ./start_app.sh"
    echo ""
    print_warning "Important Security Notes:"
    echo "• Change default admin password after first login"
    echo "• Enable MFA for all admin accounts"
    echo "• Configure Firebase credentials for file uploads"
    echo "• Set up SSL/TLS for production deployment"
    echo ""
    print_status "For detailed documentation, see ENHANCEMENT_ROADMAP.md"
    echo ""
    print_status "Setup complete! Your enhanced emergency bed booking system is ready."
}

# Run main function
main
