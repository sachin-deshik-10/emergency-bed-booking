"""
Advanced Security Service for Emergency Hospital Bed Booking System
Handles authentication, session management, rate limiting, and security monitoring
"""

import hashlib
import secrets
import time
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
from functools import wraps
from flask import request, session, flash, redirect, url_for, current_app
from flask_login import current_user, logout_user
import redis

class SecurityService:
    """Comprehensive security service for the application"""
    
    def __init__(self, redis_url: Optional[str] = None):
        """Initialize security service with optional Redis for rate limiting"""
        self.redis_client = None
        if redis_url:
            try:
                self.redis_client = redis.from_url(redis_url)
            except Exception as e:
                print(f"Redis connection failed: {e}")
    
    def generate_secure_token(self, length: int = 32) -> str:
        """Generate cryptographically secure random token"""
        return secrets.token_urlsafe(length)
    
    def hash_password(self, password: str, salt: Optional[str] = None) -> Tuple[str, str]:
        """
        Hash password with salt using PBKDF2
        Returns tuple of (hashed_password, salt)
        """
        if salt is None:
            salt = secrets.token_hex(16)
        
        # Use PBKDF2 with SHA256
        hashed = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000  # 100,000 iterations
        )
        
        return hashed.hex(), salt
    
    def verify_password(self, password: str, hashed_password: str, salt: str) -> bool:
        """Verify password against hash"""
        try:
            # Hash the provided password with the stored salt
            test_hash, _ = self.hash_password(password, salt)
            # Use constant-time comparison to prevent timing attacks
            return secrets.compare_digest(test_hash, hashed_password)
        except Exception:
            return False
    
    def get_client_ip(self) -> str:
        """Get client IP address, handling proxy headers"""
        # Check for common proxy headers
        ip = request.headers.get('X-Forwarded-For', 
                               request.headers.get('X-Real-IP', 
                                                 request.remote_addr))
        
        # X-Forwarded-For can contain multiple IPs, take the first one
        if ip and ',' in ip:
            ip = ip.split(',')[0].strip()
        
        return ip or 'unknown'
    
    def get_user_fingerprint(self) -> str:
        """Generate user fingerprint based on browser and IP"""
        user_agent = request.headers.get('User-Agent', '')
        ip_address = self.get_client_ip()
        accept_language = request.headers.get('Accept-Language', '')
        
        fingerprint_data = f"{user_agent}|{ip_address}|{accept_language}"
        return hashlib.sha256(fingerprint_data.encode()).hexdigest()[:16]
    
    def check_rate_limit(self, identifier: str, limit: int = 60, window: int = 60) -> bool:
        """
        Check if request is within rate limits
        Returns True if within limits, False if exceeded
        """
        if not self.redis_client:
            return True  # No rate limiting if Redis not available
        
        try:
            current_time = int(time.time())
            window_start = current_time - window
            
            # Clean old entries
            self.redis_client.zremrangebyscore(identifier, 0, window_start)
            
            # Count current requests
            current_requests = self.redis_client.zcard(identifier)
            
            if current_requests >= limit:
                return False
            
            # Add current request
            self.redis_client.zadd(identifier, {str(current_time): current_time})
            self.redis_client.expire(identifier, window)
            
            return True
        except Exception:
            return True  # Allow request if Redis fails
    
    def track_login_attempt(self, identifier: str, success: bool) -> Dict:
        """Track login attempts and implement account lockout"""
        if not self.redis_client:
            return {'locked': False, 'attempts': 0}
        
        try:
            lockout_key = f"lockout:{identifier}"
            attempts_key = f"attempts:{identifier}"
            
            # Check if account is currently locked
            if self.redis_client.exists(lockout_key):
                ttl = self.redis_client.ttl(lockout_key)
                return {
                    'locked': True,
                    'lockout_expires': ttl,
                    'attempts': self.redis_client.get(attempts_key) or 0
                }
            
            if success:
                # Clear failed attempts on successful login
                self.redis_client.delete(attempts_key)
                return {'locked': False, 'attempts': 0}
            else:
                # Increment failed attempts
                attempts = self.redis_client.incr(attempts_key)
                self.redis_client.expire(attempts_key, 3600)  # Expire after 1 hour
                
                # Lock account if max attempts reached
                max_attempts = current_app.config.get('MAX_LOGIN_ATTEMPTS', 5)
                lockout_minutes = current_app.config.get('ACCOUNT_LOCKOUT_MINUTES', 15)
                
                if attempts >= max_attempts:
                    self.redis_client.setex(lockout_key, lockout_minutes * 60, 'locked')
                    return {
                        'locked': True,
                        'lockout_expires': lockout_minutes * 60,
                        'attempts': attempts
                    }
                
                return {'locked': False, 'attempts': attempts}
        except Exception:
            return {'locked': False, 'attempts': 0}
    
    def validate_session(self) -> bool:
        """Validate current session for security"""
        if not session.get('user_id'):
            return False
        
        # Check session timeout
        last_activity = session.get('last_activity')
        if last_activity:
            timeout_minutes = current_app.config.get('SESSION_TIMEOUT_MINUTES', 30)
            if datetime.now() - datetime.fromisoformat(last_activity) > timedelta(minutes=timeout_minutes):
                return False
        
        # Check session fingerprint (optional, for enhanced security)
        stored_fingerprint = session.get('fingerprint')
        current_fingerprint = self.get_user_fingerprint()
        
        if stored_fingerprint and stored_fingerprint != current_fingerprint:
            # Fingerprint mismatch - possible session hijacking
            self.log_security_event('session_fingerprint_mismatch', {
                'user_id': session.get('user_id'),
                'stored_fingerprint': stored_fingerprint,
                'current_fingerprint': current_fingerprint
            })
            return False
        
        return True
    
    def update_session_activity(self):
        """Update session with current activity timestamp"""
        session['last_activity'] = datetime.now().isoformat()
        
        # Set fingerprint on first activity
        if 'fingerprint' not in session:
            session['fingerprint'] = self.get_user_fingerprint()
    
    def secure_logout(self):
        """Perform secure logout with session cleanup"""
        # Log security event
        if current_user.is_authenticated:
            self.log_security_event('user_logout', {
                'user_id': current_user.id,
                'session_duration': self._calculate_session_duration()
            })
        
        # Clear all session data
        session.clear()
        
        # Logout user
        logout_user()
    
    def _calculate_session_duration(self) -> Optional[int]:
        """Calculate session duration in minutes"""
        if 'login_time' in session:
            try:
                login_time = datetime.fromisoformat(session['login_time'])
                duration = (datetime.now() - login_time).total_seconds() / 60
                return int(duration)
            except:
                pass
        return None
    
    def log_security_event(self, event_type: str, details: Dict):
        """Log security events for monitoring and audit"""
        event_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': event_type,
            'ip_address': self.get_client_ip(),
            'user_agent': request.headers.get('User-Agent', ''),
            'details': details
        }
        
        # In production, this should write to a secure log system
        print(f"SECURITY EVENT: {event_data}")
        
        # Store in Redis for immediate analysis (optional)
        if self.redis_client:
            try:
                key = f"security_events:{event_type}"
                self.redis_client.lpush(key, str(event_data))
                self.redis_client.ltrim(key, 0, 999)  # Keep last 1000 events
                self.redis_client.expire(key, 86400 * 7)  # Keep for 7 days
            except Exception:
                pass
    
    def check_suspicious_activity(self, user_id: str) -> Dict:
        """Check for suspicious activity patterns"""
        if not self.redis_client:
            return {'suspicious': False}
        
        try:
            # Check multiple IPs in short time
            ip_key = f"user_ips:{user_id}"
            recent_ips = self.redis_client.smembers(ip_key)
            
            if len(recent_ips) > 3:  # More than 3 IPs in tracking window
                return {
                    'suspicious': True,
                    'reason': 'multiple_ip_addresses',
                    'ip_count': len(recent_ips)
                }
            
            # Check rapid login attempts
            attempts_key = f"rapid_attempts:{user_id}"
            attempts = self.redis_client.get(attempts_key)
            
            if attempts and int(attempts) > 10:  # More than 10 attempts in window
                return {
                    'suspicious': True,
                    'reason': 'rapid_login_attempts',
                    'attempt_count': int(attempts)
                }
            
            return {'suspicious': False}
        except Exception:
            return {'suspicious': False}
    
    def add_security_headers(self, response):
        """Add security headers to response"""
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Content Security Policy
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "img-src 'self' data: https:; "
            "font-src 'self' https://cdn.jsdelivr.net; "
            "connect-src 'self';"
        )
        response.headers['Content-Security-Policy'] = csp
        
        return response

# Security decorators
def rate_limit(requests_per_minute: int = 60):
    """Decorator for rate limiting endpoints"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            security_service = SecurityService(current_app.config.get('RATE_LIMIT_STORAGE_URL'))
            
            identifier = f"rate_limit:{security_service.get_client_ip()}:{request.endpoint}"
            
            if not security_service.check_rate_limit(identifier, requests_per_minute):
                flash('Too many requests. Please try again later.', 'error')
                return redirect(url_for('index'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def session_required(f):
    """Decorator to ensure valid session"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        security_service = SecurityService()
        
        if not security_service.validate_session():
            security_service.secure_logout()
            flash('Your session has expired. Please log in again.', 'warning')
            return redirect(url_for('login'))
        
        security_service.update_session_activity()
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator to require admin privileges"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        
        # Check if user is admin (implement based on your user model)
        if not getattr(current_user, 'is_admin', False):
            flash('Administrative privileges required.', 'error')
            return redirect(url_for('index'))
        
        return f(*args, **kwargs)
    return decorated_function

# Initialize global security service instance
security_service = SecurityService()
