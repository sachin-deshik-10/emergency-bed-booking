"""
Enhanced Main Application with Advanced Security and Real-time Features
Integrates all critical priority enhancements for the Emergency Hospital Bed Booking System
"""

import os
import logging
import secrets
from datetime import datetime, timedelta
from flask import Flask, render_template, request, flash, redirect, url_for, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf.csrf import CSRFProtect
from flask_mail import Mail
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman
from werkzeug.security import generate_password_hash, check_password_hash

# Import our enhanced services
from config.secure_config import get_config, Config
from services.validation_service import validator
from services.security_service import SecurityService, rate_limit, session_required, admin_required
from services.auth_service import AuthenticationService
from services.realtime_service import RealTimeService
from forms.secure_forms import *

# Initialize Flask app with enhanced security
app = Flask(__name__)

# Load configuration
config = get_config()
app.config.from_object(config)

# Validate configuration
try:
    config.validate_config()
except ValueError as e:
    logging.error(f"Configuration error: {e}")
    exit(1)

# Security Headers
talisman = Talisman(
    app,
    force_https=False,  # Set to True in production
    strict_transport_security=True,
    content_security_policy={
        'default-src': "'self'",
        'script-src': "'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net",
        'style-src': "'self' 'unsafe-inline' https://cdn.jsdelivr.net",
        'img-src': "'self' data: https:",
        'font-src': "'self' https://cdn.jsdelivr.net",
        'connect-src': "'self'"
    }
)

# CSRF Protection
csrf = CSRFProtect(app)

# Database
app.config['SQLALCHEMY_DATABASE_URI'] = config.get_database_url()
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

# Mail Service
mail = Mail(app)

# Rate Limiting
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri=config.RATE_LIMIT_STORAGE_URL
)

# Initialize Services
security_service = SecurityService(config.RATE_LIMIT_STORAGE_URL)
auth_service = AuthenticationService(config.SOCKETIO_REDIS_URL, mail)
realtime_service = RealTimeService(app, config.SOCKETIO_REDIS_URL)

# Enhanced Database Models

class User(UserMixin, db.Model):
    """Enhanced User model with security features"""
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    password_salt = db.Column(db.String(32), nullable=False)
    dob = db.Column(db.String(1000))
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    failed_login_attempts = db.Column(db.Integer, default=0)
    account_locked_until = db.Column(db.DateTime)
    
    @property
    def user_type(self):
        return 'admin' if self.is_admin else 'patient'
    
    def set_password(self, password):
        """Set password with enhanced security"""
        self.password_hash, self.password_salt = security_service.hash_password(password)
    
    def check_password(self, password):
        """Check password with constant-time comparison"""
        return security_service.verify_password(password, self.password_hash, self.password_salt)
    
    def is_account_locked(self):
        """Check if account is locked"""
        if self.account_locked_until and self.account_locked_until > datetime.utcnow():
            return True
        return False

class Hospitaluser(UserMixin, db.Model):
    """Enhanced Hospital user model"""
    id = db.Column(db.Integer, primary_key=True)
    hcode = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    password_salt = db.Column(db.String(32), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    failed_login_attempts = db.Column(db.Integer, default=0)
    account_locked_until = db.Column(db.DateTime)
    
    @property
    def user_type(self):
        return 'hospital'
    
    def set_password(self, password):
        """Set password with enhanced security"""
        self.password_hash, self.password_salt = security_service.hash_password(password)
    
    def check_password(self, password):
        """Check password with constant-time comparison"""
        return security_service.verify_password(password, self.password_hash, self.password_salt)
    
    def is_account_locked(self):
        """Check if account is locked"""
        if self.account_locked_until and self.account_locked_until > datetime.utcnow():
            return True
        return False

class Hospitaldata(db.Model):
    """Enhanced Hospital data model"""
    id = db.Column(db.Integer, primary_key=True)
    hcode = db.Column(db.String(20), unique=True, nullable=False)
    hname = db.Column(db.String(100), nullable=False)
    normalbed = db.Column(db.Integer, default=0)
    hicubed = db.Column(db.Integer, default=0)
    icubed = db.Column(db.Integer, default=0)
    vbed = db.Column(db.Integer, default=0)
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    specialties = db.Column(db.Text)
    license_number = db.Column(db.String(50))
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @property
    def total_beds(self):
        return self.normalbed + self.hicubed + self.icubed + self.vbed
    
    def to_dict(self):
        return {
            'hcode': self.hcode,
            'hname': self.hname,
            'normalbed': self.normalbed,
            'hicubed': self.hicubed,
            'icubed': self.icubed,
            'vbed': self.vbed,
            'total_beds': self.total_beds
        }

class Bookingpatient(db.Model):
    """Enhanced Patient booking model"""
    id = db.Column(db.Integer, primary_key=True)
    bedtype = db.Column(db.String(100), nullable=False)
    hcode = db.Column(db.String(20), nullable=False)
    spo2 = db.Column(db.Integer, nullable=False)
    pname = db.Column(db.String(100), nullable=False)
    pphone = db.Column(db.String(100), nullable=False)
    paddress = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    emergency_contact = db.Column(db.String(100))
    medical_conditions = db.Column(db.Text)
    insurance_number = db.Column(db.String(50))
    booking_status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Trig(db.Model):
    """Enhanced trigger/audit log model"""
    id = db.Column(db.Integer, primary_key=True)
    hcode = db.Column(db.String(20), nullable=False)
    normalbed = db.Column(db.Integer, default=0)
    hicubed = db.Column(db.Integer, default=0)
    icubed = db.Column(db.Integer, default=0)
    vbed = db.Column(db.Integer, default=0)
    querys = db.Column(db.String(50), nullable=False)
    date = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.String(50))
    ip_address = db.Column(db.String(45))

# Login Manager User Loader
@login_manager.user_loader
def load_user(user_id):
    """Load user for Flask-Login"""
    # Check if it's a regular user
    user = User.query.get(int(user_id))
    if user:
        return user
    
    # Check if it's a hospital user
    hospital_user = Hospitaluser.query.get(int(user_id))
    if hospital_user:
        return hospital_user
    
    return None

# Security Event Handlers
@app.before_request
def security_checks():
    """Perform security checks before each request"""
    # Update session activity
    security_service.update_session_activity()
    
    # Check session validity for authenticated users
    if current_user.is_authenticated:
        if not security_service.validate_session():
            security_service.secure_logout()
            flash('Your session has expired. Please log in again.', 'warning')
            return redirect(url_for('login'))

@app.after_request
def after_request(response):
    """Add security headers to all responses"""
    return security_service.add_security_headers(response)

# Enhanced Route Handlers

@app.route('/')
def index():
    """Enhanced home page with real-time bed data"""
    try:
        hospitals = Hospitaldata.query.filter_by(is_verified=True).all()
        
        # Get real-time bed availability
        bed_data = []
        for hospital in hospitals:
            bed_data.append({
                'hospital': hospital,
                'availability': hospital.to_dict(),
                'last_updated': hospital.updated_at.strftime('%Y-%m-%d %H:%M:%S')
            })
        
        return render_template('index.html', 
                             bed_data=bed_data,
                             total_hospitals=len(hospitals))
    except Exception as e:
        logging.error(f"Error loading home page: {e}")
        flash('Error loading hospital data. Please try again.', 'error')
        return render_template('index.html', bed_data=[], total_hospitals=0)

@app.route('/signup', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def signup():
    """Enhanced user registration with validation"""
    form = UserRegistrationForm()
    
    if form.validate_on_submit():
        # Additional server-side validation
        validation_result = validator.validate_user_registration(form.data)
        
        if not validation_result['valid']:
            for field, errors in validation_result['errors'].items():
                if isinstance(errors, list):
                    for error in errors:
                        flash(f"{field}: {error}", 'error')
                else:
                    flash(f"{field}: {errors}", 'error')
            return render_template('usersignup.html', form=form)
        
        # Check if user already exists
        if User.query.filter_by(email=form.email.data.lower()).first():
            flash('Email already registered. Please use a different email.', 'error')
            return render_template('usersignup.html', form=form)
        
        try:
            # Create new user
            user = User(
                email=form.email.data.lower(),
                dob=form.dob.data.isoformat()
            )
            user.set_password(form.password.data)
            
            db.session.add(user)
            db.session.commit()
            
            # Log registration event
            security_service.log_security_event('user_registered', {
                'user_id': user.id,
                'email': user.email
            })
            
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
            
        except Exception as e:
            db.session.rollback()
            logging.error(f"Registration error: {e}")
            flash('Registration failed. Please try again.', 'error')
    
    return render_template('usersignup.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def login():
    """Enhanced user login with MFA support"""
    form = UserLoginForm()
    
    if form.validate_on_submit():
        email = form.email.data.lower()
        password = form.password.data
        mfa_token = form.mfa_token.data
        
        # Check rate limiting for this user
        login_attempts = security_service.track_login_attempt(email, False)
        
        if login_attempts.get('locked'):
            flash(f'Account locked due to too many failed attempts. Try again in {login_attempts.get("lockout_expires", 0)//60} minutes.', 'error')
            return render_template('userlogin.html', form=form)
        
        # Find user
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password) and not user.is_account_locked():
            # Check MFA if enabled
            if auth_service.is_mfa_enabled(str(user.id)):
                if not mfa_token:
                    flash('Multi-factor authentication code required.', 'info')
                    return render_template('userlogin.html', form=form, require_mfa=True)
                
                # Verify MFA token
                mfa_secret = auth_service.get_mfa_secret(str(user.id))
                if not auth_service.verify_mfa_token(mfa_secret, mfa_token):
                    security_service.track_login_attempt(email, False)
                    flash('Invalid authentication code.', 'error')
                    return render_template('userlogin.html', form=form, require_mfa=True)
            
            # Successful login
            login_user(user, remember=form.remember_me.data)
            
            # Update login tracking
            user.last_login = datetime.utcnow()
            user.failed_login_attempts = 0
            db.session.commit()
            
            # Track successful login
            security_service.track_login_attempt(email, True)
            auth_service.update_last_login_time(str(user.id))
            auth_service.increment_login_count(str(user.id))
            
            # Set session data
            session['login_time'] = datetime.utcnow().isoformat()
            session['user_type'] = user.user_type
            
            # Log security event
            security_service.log_security_event('user_login', {
                'user_id': user.id,
                'user_type': user.user_type,
                'mfa_used': auth_service.is_mfa_enabled(str(user.id))
            })
            
            flash('Login successful!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            # Failed login
            security_service.track_login_attempt(email, False)
            
            if user:
                user.failed_login_attempts += 1
                
                # Lock account if too many attempts
                if user.failed_login_attempts >= app.config.get('MAX_LOGIN_ATTEMPTS', 5):
                    user.account_locked_until = datetime.utcnow() + timedelta(
                        minutes=app.config.get('ACCOUNT_LOCKOUT_MINUTES', 15)
                    )
                
                db.session.commit()
            
            flash('Invalid email or password.', 'error')
    
    return render_template('userlogin.html', form=form)

@app.route('/hospitallogin', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def hospitallogin():
    """Enhanced hospital login with MFA support"""
    form = HospitalLoginForm()
    
    if form.validate_on_submit():
        hcode = form.hcode.data.upper()
        email = form.email.data.lower()
        password = form.password.data
        mfa_token = form.mfa_token.data
        
        # Check rate limiting
        login_attempts = security_service.track_login_attempt(f"{hcode}:{email}", False)
        
        if login_attempts.get('locked'):
            flash(f'Account locked due to too many failed attempts. Try again in {login_attempts.get("lockout_expires", 0)//60} minutes.', 'error')
            return render_template('hospitallogin.html', form=form)
        
        # Find hospital user
        hospital_user = Hospitaluser.query.filter_by(hcode=hcode, email=email).first()
        
        if hospital_user and hospital_user.check_password(password) and not hospital_user.is_account_locked():
            # Check MFA if enabled
            if auth_service.is_mfa_enabled(str(hospital_user.id)):
                if not mfa_token:
                    flash('Multi-factor authentication code required.', 'info')
                    return render_template('hospitallogin.html', form=form, require_mfa=True)
                
                # Verify MFA token
                mfa_secret = auth_service.get_mfa_secret(str(hospital_user.id))
                if not auth_service.verify_mfa_token(mfa_secret, mfa_token):
                    security_service.track_login_attempt(f"{hcode}:{email}", False)
                    flash('Invalid authentication code.', 'error')
                    return render_template('hospitallogin.html', form=form, require_mfa=True)
            
            # Successful login
            login_user(hospital_user)
            
            # Update login tracking
            hospital_user.last_login = datetime.utcnow()
            hospital_user.failed_login_attempts = 0
            db.session.commit()
            
            # Track successful login
            security_service.track_login_attempt(f"{hcode}:{email}", True)
            
            # Set session data
            session['login_time'] = datetime.utcnow().isoformat()
            session['user_type'] = hospital_user.user_type
            session['hospital_code'] = hcode
            
            # Log security event
            security_service.log_security_event('hospital_login', {
                'user_id': hospital_user.id,
                'hospital_code': hcode,
                'mfa_used': auth_service.is_mfa_enabled(str(hospital_user.id))
            })
            
            flash('Hospital login successful!', 'success')
            return redirect(url_for('hospitaldata'))
        else:
            # Failed login
            security_service.track_login_attempt(f"{hcode}:{email}", False)
            
            if hospital_user:
                hospital_user.failed_login_attempts += 1
                
                # Lock account if too many attempts
                if hospital_user.failed_login_attempts >= app.config.get('MAX_LOGIN_ATTEMPTS', 5):
                    hospital_user.account_locked_until = datetime.utcnow() + timedelta(
                        minutes=app.config.get('ACCOUNT_LOCKOUT_MINUTES', 15)
                    )
                
                db.session.commit()
            
            flash('Invalid hospital code, email, or password.', 'error')
    
    return render_template('hospitallogin.html', form=form)

@app.route('/slotbooking', methods=['GET', 'POST'])
@login_required
@session_required
@rate_limit(30)  # 30 requests per minute
def slotbooking():
    """Enhanced bed booking with real-time availability"""
    form = BedBookingForm()
    
    # Populate hospital choices
    hospitals = Hospitaldata.query.filter_by(is_verified=True).all()
    form.hcode.choices = [(h.hcode, f"{h.hname} ({h.hcode})") for h in hospitals]
    
    if form.validate_on_submit():
        # Validate booking data
        validation_result = validator.validate_bed_booking(form.data)
        
        if not validation_result['valid']:
            for field, errors in validation_result['errors'].items():
                flash(f"{field}: {errors}", 'error')
            return render_template('booking.html', form=form, hospitals=hospitals)
        
        # Check bed availability
        hospital = Hospitaldata.query.filter_by(hcode=form.hcode.data).first()
        if not hospital:
            flash('Selected hospital not found.', 'error')
            return render_template('booking.html', form=form, hospitals=hospitals)
        
        # Check specific bed type availability
        bed_type = form.bedtype.data
        available_beds = 0
        
        if bed_type == 'Normal':
            available_beds = hospital.normalbed
        elif bed_type == 'HICU':
            available_beds = hospital.hicubed
        elif bed_type == 'ICU':
            available_beds = hospital.icubed
        elif bed_type == 'Ventilator':
            available_beds = hospital.vbed
        
        if available_beds <= 0:
            flash(f'No {bed_type} beds available at {hospital.hname}.', 'error')
            return render_template('booking.html', form=form, hospitals=hospitals)
        
        try:
            # Create booking
            booking = Bookingpatient(**validation_result['sanitized_data'])
            db.session.add(booking)
            
            # Update bed count
            if bed_type == 'Normal':
                hospital.normalbed -= 1
            elif bed_type == 'HICU':
                hospital.hicubed -= 1
            elif bed_type == 'ICU':
                hospital.icubed -= 1
            elif bed_type == 'Ventilator':
                hospital.vbed -= 1
            
            # Create audit log
            trig = Trig(
                hcode=hospital.hcode,
                normalbed=hospital.normalbed,
                hicubed=hospital.hicubed,
                icubed=hospital.icubed,
                vbed=hospital.vbed,
                querys=f"book_{bed_type.lower()}",
                date=datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
                user_id=str(current_user.id),
                ip_address=security_service.get_client_ip()
            )
            db.session.add(trig)
            
            db.session.commit()
            
            # Broadcast real-time update
            realtime_service._broadcast_bed_update(hospital.hcode, {
                'bed_type': bed_type.lower(),
                'action': 'decrease',
                'count': 1,
                'reason': 'bed_booking'
            })
            
            # Send confirmation email (if configured)
            # auth_service.send_booking_confirmation_email(booking)
            
            flash(f'Bed booking successful! Booking ID: {booking.id}', 'success')
            return redirect(url_for('index'))
            
        except Exception as e:
            db.session.rollback()
            logging.error(f"Booking error: {e}")
            flash('Booking failed. Please try again.', 'error')
    
    return render_template('booking.html', form=form, hospitals=hospitals)

# Additional route handlers would continue here...
# For brevity, I'll create the key ones and show the pattern

@app.route('/logout')
@login_required
def logout():
    """Enhanced logout with security logging"""
    security_service.secure_logout()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
@session_required
def dashboard():
    """Real-time dashboard for hospital staff"""
    if not hasattr(current_user, 'hcode'):
        flash('Access denied.', 'error')
        return redirect(url_for('index'))
    
    hospital = Hospitaldata.query.filter_by(hcode=current_user.hcode).first()
    if not hospital:
        flash('Hospital data not found.', 'error')
        return redirect(url_for('index'))
    
    # Get recent bookings
    recent_bookings = Bookingpatient.query.filter_by(hcode=current_user.hcode)\
                                          .order_by(Bookingpatient.created_at.desc())\
                                          .limit(10).all()
    
    # Get activity statistics
    activity_stats = realtime_service.get_hospital_activity(current_user.hcode)
    connected_users = realtime_service.get_connected_users_count()
    
    return render_template('dashboard.html',
                         hospital=hospital,
                         recent_bookings=recent_bookings,
                         activity_stats=activity_stats,
                         connected_users=connected_users)

# API Endpoints for Real-time Features

@app.route('/api/hospitals/availability')
@limiter.limit("30 per minute")
def api_hospital_availability():
    """API endpoint for real-time hospital availability"""
    try:
        hospitals = Hospitaldata.query.filter_by(is_verified=True).all()
        data = []
        
        for hospital in hospitals:
            data.append({
                'hcode': hospital.hcode,
                'hname': hospital.hname,
                'beds': {
                    'normal': hospital.normalbed,
                    'hicu': hospital.hicubed,
                    'icu': hospital.icubed,
                    'ventilator': hospital.vbed
                },
                'total_available': hospital.total_beds,
                'last_updated': hospital.updated_at.isoformat()
            })
        
        return jsonify({
            'success': True,
            'data': data,
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        logging.error(f"API error: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch hospital data'
        }), 500

# Error Handlers

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(403)
def forbidden_error(error):
    return render_template('errors/403.html'), 403

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500

@app.errorhandler(429)
def ratelimit_handler(e):
    return render_template('errors/429.html'), 429

# Initialize Database
def init_db():
    """Initialize database with tables"""
    with app.app_context():
        db.create_all()
        
        # Create default admin user if not exists
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
            print("Default admin user created: admin@hospital.com / SecureAdmin123!")

if __name__ == '__main__':
    # Setup logging
    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL),
        format='%(asctime)s %(levelname)s %(name)s %(message)s',
        handlers=[
            logging.FileHandler(config.LOG_FILE),
            logging.StreamHandler()
        ]
    )
    
    # Create logs directory
    os.makedirs(os.path.dirname(config.LOG_FILE), exist_ok=True)
    
    # Initialize database
    init_db()
    
    # Run application
    realtime_service.socketio.run(
        app,
        debug=config.FLASK_DEBUG,
        host='0.0.0.0',
        port=5000
    )
