"""
Secure Configuration Management for Emergency Hospital Bed Booking System
Handles environment variables, validation, and security settings
"""

import os
import secrets
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration class with security defaults"""
    
    # Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_urlsafe(32)
    FLASK_ENV = os.environ.get('FLASK_ENV', 'production')
    FLASK_DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Database Configuration
    DATABASE_URL = os.environ.get('DATABASE_URL')
    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
    MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD')
    MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE', 'emergency_bed')
    
    # Security Configuration
    SESSION_TIMEOUT_MINUTES = int(os.environ.get('SESSION_TIMEOUT_MINUTES', 30))
    MAX_LOGIN_ATTEMPTS = int(os.environ.get('MAX_LOGIN_ATTEMPTS', 5))
    ACCOUNT_LOCKOUT_MINUTES = int(os.environ.get('ACCOUNT_LOCKOUT_MINUTES', 15))
    CSRF_SECRET_KEY = os.environ.get('CSRF_SECRET_KEY') or secrets.token_urlsafe(32)
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS_PER_MINUTE = int(os.environ.get('RATE_LIMIT_REQUESTS_PER_MINUTE', 60))
    RATE_LIMIT_STORAGE_URL = os.environ.get('RATE_LIMIT_STORAGE_URL', 'redis://localhost:6379/1')
    
    # WebSocket Configuration
    SOCKETIO_REDIS_URL = os.environ.get('SOCKETIO_REDIS_URL', 'redis://localhost:6379/0')
    SOCKETIO_ASYNC_MODE = os.environ.get('SOCKETIO_ASYNC_MODE', 'eventlet')
    
    # Firebase Configuration
    FIREBASE_CONFIG = {
        "apiKey": os.environ.get('FIREBASE_API_KEY'),
        "authDomain": os.environ.get('FIREBASE_AUTH_DOMAIN'),
        "projectId": os.environ.get('FIREBASE_PROJECT_ID'),
        "storageBucket": os.environ.get('FIREBASE_STORAGE_BUCKET'),
        "messagingSenderId": os.environ.get('FIREBASE_MESSAGING_SENDER_ID'),
        "appId": os.environ.get('FIREBASE_APP_ID'),
        "measurementId": os.environ.get('FIREBASE_MEASUREMENT_ID')
    }
    
    # Email Configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 465))
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'True').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    # Logging Configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', 'logs/app.log')
    
    @classmethod
    def validate_config(cls) -> bool:
        """Validate that all required configuration values are present"""
        required_vars = [
            'SECRET_KEY',
            'MYSQL_PASSWORD',
            'FIREBASE_API_KEY'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not getattr(cls, var, None):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        return True
    
    @classmethod
    def get_database_url(cls) -> str:
        """Generate SQLAlchemy database URL"""
        if cls.DATABASE_URL:
            return cls.DATABASE_URL
        
        return f"mysql+mysqldb://{cls.MYSQL_USER}:{cls.MYSQL_PASSWORD}@{cls.MYSQL_HOST}/{cls.MYSQL_DATABASE}"

class DevelopmentConfig(Config):
    """Development environment configuration"""
    FLASK_DEBUG = True
    FLASK_ENV = 'development'

class ProductionConfig(Config):
    """Production environment configuration"""
    FLASK_DEBUG = False
    FLASK_ENV = 'production'
    SESSION_TIMEOUT_MINUTES = 15  # Shorter timeout for production

class TestingConfig(Config):
    """Testing environment configuration"""
    TESTING = True
    FLASK_DEBUG = True
    MYSQL_DATABASE = 'emergency_bed_test'

# Configuration mapping
config_map = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config(env: Optional[str] = None) -> Config:
    """Get configuration based on environment"""
    env = env or os.environ.get('FLASK_ENV', 'development')
    return config_map.get(env, config_map['default'])
