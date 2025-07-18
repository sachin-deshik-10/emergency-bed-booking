"""
Advanced Authentication Service with Multi-Factor Authentication
Handles user authentication, MFA, password management, and access control
"""

import pyotp
import qrcode
import io
import base64
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
from flask import current_app, url_for
from flask_mail import Message
import secrets
import redis
import logging

class AuthenticationService:
    """Advanced authentication service with MFA support"""
    
    def __init__(self, redis_url: Optional[str] = None, mail_service=None):
        self.redis_client = None
        self.mail_service = mail_service
        
        if redis_url:
            try:
                self.redis_client = redis.from_url(redis_url)
            except Exception as e:
                logging.warning(f"Redis connection failed: {e}")
    
    def generate_mfa_secret(self, user_email: str) -> str:
        """Generate a new MFA secret for user"""
        secret = pyotp.random_base32()
        
        # Store secret temporarily until user confirms setup
        if self.redis_client:
            key = f"mfa_setup:{user_email}"
            self.redis_client.setex(key, 600, secret)  # 10 minutes expiry
        
        return secret
    
    def generate_mfa_qr_code(self, user_email: str, secret: str) -> str:
        """Generate QR code for MFA setup"""
        try:
            # Create TOTP URI
            totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
                name=user_email,
                issuer_name="Emergency Bed Booking System"
            )
            
            # Generate QR code
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(totp_uri)
            qr.make(fit=True)
            
            # Create QR code image
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Convert to base64 string
            img_buffer = io.BytesIO()
            img.save(img_buffer, format='PNG')
            img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
            
            return f"data:image/png;base64,{img_base64}"
        except Exception as e:
            logging.error(f"Error generating QR code: {e}")
            return ""
    
    def verify_mfa_token(self, secret: str, token: str, window: int = 1) -> bool:
        """Verify MFA token with tolerance window"""
        try:
            totp = pyotp.TOTP(secret)
            return totp.verify(token, valid_window=window)
        except Exception as e:
            logging.error(f"Error verifying MFA token: {e}")
            return False
    
    def enable_mfa_for_user(self, user_id: str, user_email: str, secret: str, verification_token: str) -> Dict:
        """Enable MFA for a user after verification"""
        try:
            # Verify the token first
            if not self.verify_mfa_token(secret, verification_token):
                return {
                    'success': False,
                    'error': 'Invalid verification token'
                }
            
            # Store MFA secret securely (in production, encrypt this)
            if self.redis_client:
                key = f"mfa_secret:{user_id}"
                self.redis_client.set(key, secret)
                
                # Remove temporary setup key
                setup_key = f"mfa_setup:{user_email}"
                self.redis_client.delete(setup_key)
            
            # Generate backup codes
            backup_codes = self.generate_backup_codes(user_id)
            
            return {
                'success': True,
                'backup_codes': backup_codes,
                'message': 'MFA enabled successfully'
            }
        except Exception as e:
            logging.error(f"Error enabling MFA: {e}")
            return {
                'success': False,
                'error': 'Failed to enable MFA'
            }
    
    def generate_backup_codes(self, user_id: str, count: int = 10) -> list:
        """Generate backup codes for MFA recovery"""
        backup_codes = []
        
        for _ in range(count):
            code = ''.join([str(secrets.randbelow(10)) for _ in range(8)])
            code = f"{code[:4]}-{code[4:]}"  # Format as XXXX-XXXX
            backup_codes.append(code)
        
        # Store backup codes in Redis (in production, encrypt these)
        if self.redis_client:
            key = f"backup_codes:{user_id}"
            self.redis_client.sadd(key, *backup_codes)
            self.redis_client.expire(key, 86400 * 365)  # 1 year expiry
        
        return backup_codes
    
    def verify_backup_code(self, user_id: str, backup_code: str) -> bool:
        """Verify and consume a backup code"""
        if not self.redis_client:
            return False
        
        try:
            key = f"backup_codes:{user_id}"
            
            # Check if code exists
            if self.redis_client.sismember(key, backup_code):
                # Remove the code (one-time use)
                self.redis_client.srem(key, backup_code)
                
                # Log backup code usage
                self.log_backup_code_usage(user_id, backup_code)
                
                return True
            
            return False
        except Exception as e:
            logging.error(f"Error verifying backup code: {e}")
            return False
    
    def is_mfa_enabled(self, user_id: str) -> bool:
        """Check if MFA is enabled for user"""
        if not self.redis_client:
            return False
        
        key = f"mfa_secret:{user_id}"
        return self.redis_client.exists(key)
    
    def get_mfa_secret(self, user_id: str) -> Optional[str]:
        """Get MFA secret for user (for internal use only)"""
        if not self.redis_client:
            return None
        
        key = f"mfa_secret:{user_id}"
        secret = self.redis_client.get(key)
        return secret.decode() if secret else None
    
    def disable_mfa_for_user(self, user_id: str) -> bool:
        """Disable MFA for a user"""
        if not self.redis_client:
            return False
        
        try:
            # Remove MFA secret
            secret_key = f"mfa_secret:{user_id}"
            self.redis_client.delete(secret_key)
            
            # Remove backup codes
            backup_key = f"backup_codes:{user_id}"
            self.redis_client.delete(backup_key)
            
            return True
        except Exception as e:
            logging.error(f"Error disabling MFA: {e}")
            return False
    
    def generate_password_reset_token(self, user_email: str) -> str:
        """Generate secure password reset token"""
        token = secrets.token_urlsafe(32)
        
        if self.redis_client:
            key = f"reset_token:{token}"
            self.redis_client.setex(key, 3600, user_email)  # 1 hour expiry
        
        return token
    
    def verify_password_reset_token(self, token: str) -> Optional[str]:
        """Verify password reset token and return email"""
        if not self.redis_client:
            return None
        
        key = f"reset_token:{token}"
        email = self.redis_client.get(key)
        
        if email:
            # Delete token after verification (one-time use)
            self.redis_client.delete(key)
            return email.decode()
        
        return None
    
    def send_password_reset_email(self, user_email: str) -> bool:
        """Send password reset email"""
        if not self.mail_service:
            return False
        
        try:
            token = self.generate_password_reset_token(user_email)
            reset_url = url_for('reset_password', token=token, _external=True)
            
            msg = Message(
                subject='Password Reset Request - Emergency Bed Booking System',
                recipients=[user_email],
                html=self._get_password_reset_email_template(reset_url)
            )
            
            self.mail_service.send(msg)
            return True
        except Exception as e:
            logging.error(f"Error sending password reset email: {e}")
            return False
    
    def _get_password_reset_email_template(self, reset_url: str) -> str:
        """Get HTML template for password reset email"""
        return f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background-color: #f8f9fa; padding: 20px; text-align: center;">
                <h2 style="color: #28a745;">Emergency Bed Booking System</h2>
            </div>
            
            <div style="padding: 30px;">
                <h3>Password Reset Request</h3>
                
                <p>You have requested to reset your password. Click the button below to proceed:</p>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{reset_url}" 
                       style="background-color: #007bff; color: white; padding: 12px 30px; 
                              text-decoration: none; border-radius: 5px; display: inline-block;">
                        Reset Password
                    </a>
                </div>
                
                <p><strong>Important:</strong></p>
                <ul>
                    <li>This link will expire in 1 hour</li>
                    <li>If you didn't request this reset, please ignore this email</li>
                    <li>For security, never share this link with anyone</li>
                </ul>
                
                <p>If the button doesn't work, copy and paste this link:</p>
                <p style="word-break: break-all; color: #6c757d; font-size: 12px;">{reset_url}</p>
            </div>
            
            <div style="background-color: #f8f9fa; padding: 15px; text-align: center; 
                        color: #6c757d; font-size: 12px;">
                Emergency Hospital Bed Booking System<br>
                This is an automated message, please do not reply.
            </div>
        </body>
        </html>
        """
    
    def send_mfa_setup_email(self, user_email: str, qr_code_data: str) -> bool:
        """Send MFA setup instructions via email"""
        if not self.mail_service:
            return False
        
        try:
            msg = Message(
                subject='Multi-Factor Authentication Setup - Emergency Bed Booking System',
                recipients=[user_email],
                html=self._get_mfa_setup_email_template(qr_code_data)
            )
            
            self.mail_service.send(msg)
            return True
        except Exception as e:
            logging.error(f"Error sending MFA setup email: {e}")
            return False
    
    def _get_mfa_setup_email_template(self, qr_code_data: str) -> str:
        """Get HTML template for MFA setup email"""
        return f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background-color: #f8f9fa; padding: 20px; text-align: center;">
                <h2 style="color: #28a745;">Emergency Bed Booking System</h2>
            </div>
            
            <div style="padding: 30px;">
                <h3>Multi-Factor Authentication Setup</h3>
                
                <p>To enhance your account security, please set up Multi-Factor Authentication (MFA):</p>
                
                <h4>Step 1: Install an Authenticator App</h4>
                <p>Download one of these apps on your mobile device:</p>
                <ul>
                    <li>Google Authenticator</li>
                    <li>Microsoft Authenticator</li>
                    <li>Authy</li>
                </ul>
                
                <h4>Step 2: Scan the QR Code</h4>
                <p>Use your authenticator app to scan this QR code:</p>
                
                <div style="text-align: center; margin: 20px 0;">
                    <img src="{qr_code_data}" alt="MFA QR Code" style="max-width: 200px;">
                </div>
                
                <h4>Step 3: Verify Setup</h4>
                <p>Return to the application and enter the 6-digit code from your authenticator app to complete setup.</p>
                
                <div style="background-color: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; margin: 20px 0; border-radius: 5px;">
                    <strong>Important:</strong> Save your backup codes in a secure location. 
                    They can be used to access your account if you lose your mobile device.
                </div>
            </div>
            
            <div style="background-color: #f8f9fa; padding: 15px; text-align: center; 
                        color: #6c757d; font-size: 12px;">
                Emergency Hospital Bed Booking System<br>
                This is an automated message, please do not reply.
            </div>
        </body>
        </html>
        """
    
    def log_authentication_event(self, user_id: str, event_type: str, details: Dict = None):
        """Log authentication events for security monitoring"""
        event_data = {
            'user_id': user_id,
            'event_type': event_type,
            'timestamp': datetime.utcnow().isoformat(),
            'details': details or {}
        }
        
        # Log to application logs
        logging.info(f"AUTH EVENT: {event_data}")
        
        # Store in Redis for monitoring
        if self.redis_client:
            try:
                key = f"auth_events:{user_id}"
                self.redis_client.lpush(key, str(event_data))
                self.redis_client.ltrim(key, 0, 99)  # Keep last 100 events
                self.redis_client.expire(key, 86400 * 30)  # Keep for 30 days
            except Exception:
                pass
    
    def log_backup_code_usage(self, user_id: str, backup_code: str):
        """Log backup code usage"""
        self.log_authentication_event(
            user_id,
            'backup_code_used',
            {
                'backup_code_partial': backup_code[:4] + 'XXXX',  # Don't log full code
                'remaining_codes': self.get_remaining_backup_codes_count(user_id)
            }
        )
    
    def get_remaining_backup_codes_count(self, user_id: str) -> int:
        """Get count of remaining backup codes"""
        if not self.redis_client:
            return 0
        
        key = f"backup_codes:{user_id}"
        return self.redis_client.scard(key)
    
    def get_user_auth_status(self, user_id: str) -> Dict:
        """Get comprehensive authentication status for user"""
        return {
            'mfa_enabled': self.is_mfa_enabled(user_id),
            'backup_codes_remaining': self.get_remaining_backup_codes_count(user_id),
            'last_login': self.get_last_login_time(user_id),
            'total_logins': self.get_total_login_count(user_id)
        }
    
    def get_last_login_time(self, user_id: str) -> Optional[str]:
        """Get last login time for user"""
        if not self.redis_client:
            return None
        
        key = f"last_login:{user_id}"
        timestamp = self.redis_client.get(key)
        return timestamp.decode() if timestamp else None
    
    def update_last_login_time(self, user_id: str):
        """Update last login time for user"""
        if self.redis_client:
            key = f"last_login:{user_id}"
            self.redis_client.set(key, datetime.utcnow().isoformat())
    
    def get_total_login_count(self, user_id: str) -> int:
        """Get total login count for user"""
        if not self.redis_client:
            return 0
        
        key = f"login_count:{user_id}"
        count = self.redis_client.get(key)
        return int(count) if count else 0
    
    def increment_login_count(self, user_id: str):
        """Increment login count for user"""
        if self.redis_client:
            key = f"login_count:{user_id}"
            self.redis_client.incr(key)

# Create global instance
auth_service = AuthenticationService()
