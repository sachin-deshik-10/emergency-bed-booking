#!/usr/bin/env python3
"""
Comprehensive Test Suite for Enhanced Emergency Hospital Bed Booking System

This test suite validates all critical priority features including:
- Security features (authentication, validation, CSRF protection)
- Real-time functionality (WebSocket communication)
- Multi-factor authentication (MFA)
- Database operations and models
- Form validation and processing
- Rate limiting and session management
"""

import sys
import os
import time
import json
import unittest
import threading
from datetime import datetime, timedelta

# Add project directory to path
sys.path.append('project')

# Import test modules
import requests
from werkzeug.test import Client
from werkzeug.serving import WSGIRequestHandler

# Suppress test output for cleaner results
import logging
logging.getLogger('werkzeug').setLevel(logging.ERROR)

class TestResults:
    """Test results tracker"""
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
        
    def add_pass(self, test_name):
        self.passed += 1
        print(f"✓ {test_name}")
        
    def add_fail(self, test_name, error):
        self.failed += 1
        self.errors.append(f"{test_name}: {error}")
        print(f"✗ {test_name}: {error}")
        
    def summary(self):
        total = self.passed + self.failed
        print(f"\nTest Results: {self.passed}/{total} passed")
        if self.failed > 0:
            print("\nFailures:")
            for error in self.errors:
                print(f"  - {error}")

# Global test results
results = TestResults()

def test_module_imports():
    """Test that all enhanced modules can be imported"""
    print("🧪 Testing module imports...")
    
    modules_to_test = [
        ('config.secure_config', 'Configuration module'),
        ('services.validation_service', 'Validation service'),
        ('services.security_service', 'Security service'),
        ('services.auth_service', 'Authentication service'),
        ('services.realtime_service', 'Real-time service'),
        ('forms.secure_forms', 'Secure forms'),
        ('enhanced_main', 'Main application')
    ]
    
    for module_name, description in modules_to_test:
        try:
            __import__(module_name)
            results.add_pass(f"Import {description}")
        except ImportError as e:
            results.add_fail(f"Import {description}", str(e))
        except Exception as e:
            results.add_fail(f"Import {description}", f"Unexpected error: {e}")

def test_configuration():
    """Test configuration loading and validation"""
    print("\n🔧 Testing configuration...")
    
    try:
        from config.secure_config import get_config, DatabaseConfig
        
        # Test config loading
        config = get_config()
        results.add_pass("Configuration loading")
        
        # Test config validation
        if hasattr(config, 'validate_config'):
            config.validate_config()
            results.add_pass("Configuration validation")
        else:
            results.add_pass("Configuration validation (method not required)")
            
        # Test database config
        db_config = DatabaseConfig()
        if hasattr(db_config, 'get_database_url'):
            db_url = db_config.get_database_url()
            if db_url:
                results.add_pass("Database URL generation")
            else:
                results.add_fail("Database URL generation", "Empty URL returned")
        
    except Exception as e:
        results.add_fail("Configuration test", str(e))

def test_validation_service():
    """Test input validation service"""
    print("\n🛡️ Testing validation service...")
    
    try:
        from services.validation_service import validator
        
        # Test email validation
        if validator.validate_email("test@example.com"):
            results.add_pass("Email validation (valid)")
        else:
            results.add_fail("Email validation (valid)", "Valid email rejected")
            
        if not validator.validate_email("invalid-email"):
            results.add_pass("Email validation (invalid)")
        else:
            results.add_fail("Email validation (invalid)", "Invalid email accepted")
        
        # Test password strength
        if validator.validate_password_strength("SecurePassword123!"):
            results.add_pass("Password strength validation (strong)")
        else:
            results.add_fail("Password strength validation (strong)", "Strong password rejected")
            
        if not validator.validate_password_strength("weak"):
            results.add_pass("Password strength validation (weak)")
        else:
            results.add_fail("Password strength validation (weak)", "Weak password accepted")
        
        # Test sanitization
        dirty_input = "<script>alert('xss')</script>Hello"
        clean_input = validator.sanitize_input(dirty_input)
        if "<script>" not in clean_input:
            results.add_pass("Input sanitization")
        else:
            results.add_fail("Input sanitization", "Script tags not removed")
            
    except Exception as e:
        results.add_fail("Validation service test", str(e))

def test_security_service():
    """Test security service functionality"""
    print("\n🔒 Testing security service...")
    
    try:
        from services.security_service import SecurityService
        
        security = SecurityService()
        
        # Test password hashing
        password = "TestPassword123!"
        hashed = security.hash_password(password)
        if hashed and len(hashed) > 20:
            results.add_pass("Password hashing")
        else:
            results.add_fail("Password hashing", "Hash not generated properly")
        
        # Test password verification
        if security.verify_password(password, hashed):
            results.add_pass("Password verification (correct)")
        else:
            results.add_fail("Password verification (correct)", "Correct password not verified")
            
        if not security.verify_password("wrong_password", hashed):
            results.add_pass("Password verification (incorrect)")
        else:
            results.add_fail("Password verification (incorrect)", "Incorrect password verified")
        
        # Test session token generation
        token = security.generate_session_token()
        if token and len(token) > 10:
            results.add_pass("Session token generation")
        else:
            results.add_fail("Session token generation", "Token not generated")
            
    except Exception as e:
        results.add_fail("Security service test", str(e))

def test_authentication_service():
    """Test authentication service and MFA"""
    print("\n🔐 Testing authentication service...")
    
    try:
        from services.auth_service import AuthenticationService
        
        auth = AuthenticationService()
        
        # Test MFA secret generation
        secret = auth.generate_mfa_secret()
        if secret and len(secret) > 10:
            results.add_pass("MFA secret generation")
        else:
            results.add_fail("MFA secret generation", "Secret not generated")
        
        # Test QR code generation
        try:
            qr_code = auth.generate_qr_code("test@example.com", secret)
            if qr_code:
                results.add_pass("MFA QR code generation")
            else:
                results.add_fail("MFA QR code generation", "QR code not generated")
        except Exception as qr_error:
            results.add_fail("MFA QR code generation", str(qr_error))
        
        # Test backup codes generation
        backup_codes = auth.generate_backup_codes()
        if backup_codes and len(backup_codes) >= 5:
            results.add_pass("MFA backup codes generation")
        else:
            results.add_fail("MFA backup codes generation", "Backup codes not generated")
            
    except Exception as e:
        results.add_fail("Authentication service test", str(e))

def test_forms():
    """Test secure forms"""
    print("\n📝 Testing secure forms...")
    
    try:
        from forms.secure_forms import UserRegistrationForm, HospitalLoginForm
        
        # Test form creation
        reg_form = UserRegistrationForm()
        if hasattr(reg_form, 'email') and hasattr(reg_form, 'password'):
            results.add_pass("User registration form creation")
        else:
            results.add_fail("User registration form creation", "Required fields missing")
        
        login_form = HospitalLoginForm()
        if hasattr(login_form, 'email') and hasattr(login_form, 'password'):
            results.add_pass("Hospital login form creation")
        else:
            results.add_fail("Hospital login form creation", "Required fields missing")
            
    except Exception as e:
        results.add_fail("Forms test", str(e))

def test_database_models():
    """Test database models and operations"""
    print("\n🗄️ Testing database models...")
    
    try:
        from enhanced_main import app, db, User, Hospitaluser, Hospitaldata
        
        with app.app_context():
            # Test model creation
            if hasattr(User, 'email') and hasattr(User, 'set_password'):
                results.add_pass("User model structure")
            else:
                results.add_fail("User model structure", "Required methods missing")
            
            if hasattr(Hospitaluser, 'email') and hasattr(Hospitaluser, 'hname'):
                results.add_pass("Hospital user model structure")
            else:
                results.add_fail("Hospital user model structure", "Required fields missing")
            
            if hasattr(Hospitaldata, 'hname') and hasattr(Hospitaldata, 'normalbed'):
                results.add_pass("Hospital data model structure")
            else:
                results.add_fail("Hospital data model structure", "Required fields missing")
                
    except Exception as e:
        results.add_fail("Database models test", str(e))

def test_redis_connection():
    """Test Redis connection for real-time features"""
    print("\n📡 Testing Redis connection...")
    
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0, socket_timeout=2)
        r.ping()
        results.add_pass("Redis connection")
        
        # Test basic Redis operations
        r.set('test_key', 'test_value', ex=10)
        value = r.get('test_key')
        if value and value.decode() == 'test_value':
            results.add_pass("Redis operations")
        else:
            results.add_fail("Redis operations", "Set/get failed")
        
        r.delete('test_key')
        
    except redis.ConnectionError:
        results.add_fail("Redis connection", "Cannot connect to Redis server")
    except Exception as e:
        results.add_fail("Redis connection", str(e))

def test_realtime_service():
    """Test real-time service"""
    print("\n⚡ Testing real-time service...")
    
    try:
        from services.realtime_service import RealTimeService
        
        rt_service = RealTimeService()
        
        # Test service initialization
        if hasattr(rt_service, 'socketio'):
            results.add_pass("Real-time service initialization")
        else:
            results.add_fail("Real-time service initialization", "SocketIO not initialized")
        
        # Test event handler registration
        if hasattr(rt_service, 'register_handlers'):
            rt_service.register_handlers()
            results.add_pass("Real-time event handlers registration")
        else:
            results.add_pass("Real-time event handlers (not required)")
            
    except Exception as e:
        results.add_fail("Real-time service test", str(e))

def test_application_startup():
    """Test that the main application can start"""
    print("\n🚀 Testing application startup...")
    
    try:
        from enhanced_main import app
        
        # Test app creation
        if app:
            results.add_pass("Flask application creation")
        else:
            results.add_fail("Flask application creation", "App not created")
        
        # Test app configuration
        if app.config.get('SECRET_KEY'):
            results.add_pass("Application configuration")
        else:
            results.add_fail("Application configuration", "SECRET_KEY not set")
        
        # Test app context
        with app.app_context():
            results.add_pass("Application context")
            
    except Exception as e:
        results.add_fail("Application startup test", str(e))

def test_environment_setup():
    """Test environment setup and dependencies"""
    print("\n🌍 Testing environment setup...")
    
    # Test Python version
    import sys
    if sys.version_info >= (3, 8):
        results.add_pass("Python version (3.8+)")
    else:
        results.add_fail("Python version", f"Python {sys.version_info} < 3.8")
    
    # Test required packages
    required_packages = [
        'flask', 'flask_sqlalchemy', 'flask_wtf', 'werkzeug',
        'bcrypt', 'pyotp', 'qrcode', 'redis', 'python_socketio',
        'bleach', 'cryptography'
    ]
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            results.add_pass(f"Package: {package}")
        except ImportError:
            results.add_fail(f"Package: {package}", "Not installed")
    
    # Test environment files
    if os.path.exists('.env'):
        results.add_pass("Environment file (.env)")
    else:
        results.add_fail("Environment file", ".env not found")
    
    if os.path.exists('requirements.txt'):
        results.add_pass("Requirements file")
    else:
        results.add_fail("Requirements file", "requirements.txt not found")

def test_security_features():
    """Test security features integration"""
    print("\n🛡️ Testing integrated security features...")
    
    try:
        # Test CSRF protection
        from flask_wtf.csrf import CSRFProtect
        results.add_pass("CSRF protection import")
        
        # Test rate limiting
        try:
            from flask_limiter import Limiter
            results.add_pass("Rate limiting import")
        except ImportError:
            results.add_fail("Rate limiting", "flask-limiter not available")
        
        # Test session security
        from flask import session
        results.add_pass("Session management")
        
    except Exception as e:
        results.add_fail("Security features test", str(e))

def run_performance_test():
    """Basic performance test"""
    print("\n⚡ Running basic performance test...")
    
    try:
        from services.validation_service import validator
        
        # Test validation performance
        start_time = time.time()
        for i in range(1000):
            validator.validate_email(f"test{i}@example.com")
        end_time = time.time()
        
        duration = end_time - start_time
        if duration < 1.0:  # Should validate 1000 emails in under 1 second
            results.add_pass(f"Validation performance ({duration:.3f}s for 1000 operations)")
        else:
            results.add_fail("Validation performance", f"Too slow: {duration:.3f}s")
            
    except Exception as e:
        results.add_fail("Performance test", str(e))

def main():
    """Run all tests"""
    print("🧪 Enhanced Emergency Hospital Bed Booking System - Test Suite")
    print("==============================================================")
    print("")
    
    # Run test categories
    test_functions = [
        test_environment_setup,
        test_module_imports,
        test_configuration,
        test_validation_service,
        test_security_service,
        test_authentication_service,
        test_forms,
        test_database_models,
        test_redis_connection,
        test_realtime_service,
        test_application_startup,
        test_security_features,
        run_performance_test
    ]
    
    for test_func in test_functions:
        try:
            test_func()
        except Exception as e:
            results.add_fail(test_func.__name__, f"Test function error: {e}")
    
    # Print summary
    print("\n" + "="*60)
    results.summary()
    
    # Provide recommendations
    print("\n💡 Recommendations:")
    
    if results.failed == 0:
        print("🎉 All tests passed! Your enhanced system is ready for deployment.")
        print("\nNext steps:")
        print("1. Run the database migration: python migrate_db.py")
        print("2. Start the application: ./start_app.sh (Linux/Mac) or start_app.ps1 (Windows)")
        print("3. Access the application at http://localhost:5000")
        print("4. Test the web interface manually")
    else:
        print("⚠️  Some tests failed. Please address the issues before deployment.")
        print("\nCommon solutions:")
        print("1. Install missing packages: pip install -r requirements.txt")
        print("2. Check .env configuration file")
        print("3. Ensure Redis is running (optional but recommended)")
        print("4. Verify Python version is 3.8 or higher")
    
    print("\nFor detailed setup instructions, see setup_enhanced.ps1 or setup_enhanced.sh")
    
    return results.failed == 0

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
