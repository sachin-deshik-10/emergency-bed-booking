"""
Enhanced Main Application for Emergency Hospital Bed Booking System

Advanced version integrating:
- Analytics and reporting
- Advanced API endpoints
- Background task management
- Data export and backup
- Enhanced dashboard
- Real-time notifications
- Security enhancements
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from flask_wtf.csrf import CSRFProtect
from flask_talisman import Talisman
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_jwt_extended import JWTManager
import redis
import json
import logging
from datetime import datetime, timedelta
import os
from typing import Dict, List, Optional
import secrets

# Import all services
from services.validation_service import validation_service
from services.security_service import security_service, MFAService
from services.auth_service import auth_service, RoleBasedAuth
from services.realtime_service import realtime_service
from services.analytics_service import analytics_service
from services.api_service import api_v1
from services.task_service import celery_app, task_service
from services.export_service import export_service, ExportRequest, ExportFormat

# Import enhanced forms
from forms.secure_forms import (
    SecureLoginForm, SecureRegistrationForm, SecureBookingForm, 
    SecureHospitalForm, SecureUserManagementForm
)

class EnhancedEmergencyBookingApp:
    """Enhanced Emergency Hospital Bed Booking Application"""
    
    def __init__(self):
        self.app = Flask(__name__)
        self.setup_configuration()
        self.setup_security()
        self.setup_extensions()
        self.setup_logging()
        self.setup_routes()
        self.setup_error_handlers()
        self.setup_background_tasks()
        
    def setup_configuration(self):
        """Configure application settings"""
        self.app.config.update({
            'SECRET_KEY': os.environ.get('SECRET_KEY', secrets.token_hex(32)),
            'WTF_CSRF_TIME_LIMIT': 3600,  # 1 hour CSRF token expiry
            'SESSION_COOKIE_SECURE': True,
            'SESSION_COOKIE_HTTPONLY': True,
            'SESSION_COOKIE_SAMESITE': 'Lax',
            'PERMANENT_SESSION_LIFETIME': timedelta(hours=24),
            
            # JWT Configuration
            'JWT_SECRET_KEY': os.environ.get('JWT_SECRET_KEY', secrets.token_hex(32)),
            'JWT_ACCESS_TOKEN_EXPIRES': timedelta(hours=24),
            'JWT_REFRESH_TOKEN_EXPIRES': timedelta(days=30),
            
            # Redis Configuration
            'REDIS_URL': os.environ.get('REDIS_URL', 'redis://localhost:6379/0'),
            
            # Celery Configuration
            'CELERY_BROKER_URL': os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
            'CELERY_RESULT_BACKEND': os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0'),
            
            # Security Settings
            'MAX_LOGIN_ATTEMPTS': 5,
            'LOGIN_LOCKOUT_DURATION': 300,  # 5 minutes
            'PASSWORD_MIN_LENGTH': 8,
            'REQUIRE_MFA': False,  # Can be enabled per user
            
            # Analytics Settings
            'ANALYTICS_RETENTION_DAYS': 90,
            'EXPORT_MAX_RECORDS': 100000,
            'BACKUP_RETENTION_DAYS': 30,
        })
        
    def setup_security(self):
        """Setup security extensions and policies"""
        # CSRF Protection
        self.csrf = CSRFProtect(self.app)
        
        # Security Headers with Talisman
        self.talisman = Talisman(
            self.app,
            force_https=False,  # Set to True in production
            strict_transport_security=True,
            strict_transport_security_max_age=31536000,
            content_security_policy={
                'default-src': "'self'",
                'script-src': [
                    "'self'",
                    "'unsafe-inline'",  # Required for inline scripts (use nonce in production)
                    "https://cdn.jsdelivr.net",
                    "https://cdnjs.cloudflare.com",
                    "https://cdn.plot.ly",
                    "https://cdn.socket.io"
                ],
                'style-src': [
                    "'self'",
                    "'unsafe-inline'",  # Required for inline styles
                    "https://cdn.jsdelivr.net",
                    "https://cdnjs.cloudflare.com"
                ],
                'font-src': [
                    "'self'",
                    "https://cdnjs.cloudflare.com"
                ],
                'img-src': [
                    "'self'",
                    "data:",
                    "https:"
                ],
                'connect-src': [
                    "'self'",
                    "wss:",
                    "ws:"
                ]
            },
            frame_options='DENY',
            content_type_options=True,
            referrer_policy='strict-origin-when-cross-origin'
        )
        
        # JWT Manager
        self.jwt = JWTManager(self.app)
        
    def setup_extensions(self):
        """Setup Flask extensions"""
        # Redis for caching and session storage
        try:
            self.redis_client = redis.from_url(self.app.config['REDIS_URL'])
            self.redis_client.ping()  # Test connection
        except Exception as e:
            logging.warning(f"Redis connection failed: {e}. Using in-memory storage.")
            self.redis_client = None
        
        # SocketIO for real-time communication
        self.socketio = SocketIO(
            self.app,
            cors_allowed_origins="*",  # Configure appropriately for production
            async_mode='threading',
            logger=True,
            engineio_logger=True,
            ping_timeout=60,
            ping_interval=25
        )
        
        # Initialize Celery with Flask app context
        self.celery = celery_app
        self.celery.conf.update(
            broker_url=self.app.config['CELERY_BROKER_URL'],
            result_backend=self.app.config['CELERY_RESULT_BACKEND']
        )
        
        class ContextTask(self.celery.Task):
            def __call__(self, *args, **kwargs):
                with self.app.app_context():
                    return self.run(*args, **kwargs)
        
        self.celery.Task = ContextTask
        
    def setup_logging(self):
        """Setup application logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s %(levelname)s %(name)s %(message)s',
            handlers=[
                logging.FileHandler('emergency_booking.log'),
                logging.StreamHandler()
            ]
        )
        
        # Security event logging
        security_logger = logging.getLogger('security')
        security_handler = logging.FileHandler('security.log')
        security_handler.setFormatter(
            logging.Formatter('%(asctime)s SECURITY %(levelname)s %(message)s')
        )
        security_logger.addHandler(security_handler)
        security_logger.setLevel(logging.INFO)
        
        self.logger = logging.getLogger(__name__)
        
    def setup_routes(self):
        """Setup application routes"""
        
        # Register API Blueprint
        self.app.register_blueprint(api_v1)
        
        # Main Dashboard Route
        @self.app.route('/')
        def index():
            """Enhanced dashboard with real-time analytics"""
            if 'user_id' not in session:
                return redirect(url_for('login'))
            
            # Get real-time dashboard data
            dashboard_data = analytics_service.get_real_time_dashboard_data()
            
            return render_template(
                'enhanced_dashboard.html',
                dashboard_data=dashboard_data,
                user=session.get('user', {}),
                csrf_token=self.csrf.generate_csrf()
            )
        
        # Authentication Routes
        @self.app.route('/login', methods=['GET', 'POST'])
        def login():
            """Enhanced login with MFA support"""
            if 'user_id' in session:
                return redirect(url_for('index'))
            
            form = SecureLoginForm()
            
            if form.validate_on_submit():
                username = form.username.data
                password = form.password.data
                
                # Check rate limiting
                if not security_service.check_rate_limit(request.remote_addr, 'login'):
                    flash('Too many login attempts. Please try again later.', 'error')
                    return render_template('login.html', form=form)
                
                # Validate credentials
                user = auth_service.authenticate_user(username, password)
                if user:
                    # Check if MFA is required
                    if user.get('mfa_enabled'):
                        session['temp_user_id'] = user['id']
                        session['temp_username'] = username
                        return redirect(url_for('mfa_verify'))
                    
                    # Login successful
                    self.complete_login(user)
                    self.logger.info(f"User login successful: {username}")
                    
                    return redirect(url_for('index'))
                else:
                    flash('Invalid username or password', 'error')
                    self.logger.warning(f"Failed login attempt: {username}")
            
            return render_template('enhanced_login.html', form=form)
        
        @self.app.route('/mfa-verify', methods=['GET', 'POST'])
        def mfa_verify():
            """Multi-Factor Authentication verification"""
            if 'temp_user_id' not in session:
                return redirect(url_for('login'))
            
            if request.method == 'POST':
                token = request.form.get('mfa_token')
                user_id = session['temp_user_id']
                
                mfa_service = MFAService()
                if mfa_service.verify_totp_token(user_id, token):
                    # Complete login
                    user = auth_service.get_user_by_id(user_id)
                    self.complete_login(user)
                    
                    # Clear temporary session data
                    session.pop('temp_user_id', None)
                    session.pop('temp_username', None)
                    
                    return redirect(url_for('index'))
                else:
                    flash('Invalid MFA token', 'error')
            
            return render_template('mfa_verify.html')
        
        @self.app.route('/register', methods=['GET', 'POST'])
        def register():
            """Enhanced user registration"""
            form = SecureRegistrationForm()
            
            if form.validate_on_submit():
                try:
                    # Create new user
                    user_data = {
                        'username': form.username.data,
                        'email': form.email.data,
                        'password': form.password.data,
                        'role': 'user',
                        'hospital_id': form.hospital_id.data
                    }
                    
                    user = auth_service.create_user(user_data)
                    if user:
                        flash('Registration successful! Please login.', 'success')
                        
                        # Send welcome email (background task)
                        task_service.submit_task(
                            'services.task_service.send_email_notification',
                            args=(
                                form.email.data,
                                'Welcome to Emergency Booking System',
                                f'Welcome {form.username.data}! Your account has been created successfully.'
                            )
                        )
                        
                        return redirect(url_for('login'))
                    else:
                        flash('Registration failed. Please try again.', 'error')
                        
                except Exception as e:
                    self.logger.error(f"Registration error: {str(e)}")
                    flash('Registration failed due to server error.', 'error')
            
            return render_template('enhanced_register.html', form=form)
        
        @self.app.route('/logout')
        def logout():
            """Enhanced logout with session cleanup"""
            user_id = session.get('user_id')
            username = session.get('username')
            
            # Clear session
            session.clear()
            
            # Log security event
            if user_id:
                self.logger.info(f"User logout: {username} (ID: {user_id})")
            
            flash('You have been logged out successfully.', 'info')
            return redirect(url_for('login'))
        
        # Booking Routes
        @self.app.route('/booking', methods=['GET', 'POST'])
        def booking():
            """Enhanced booking with real-time validation"""
            if 'user_id' not in session:
                return redirect(url_for('login'))
            
            form = SecureBookingForm()
            
            if form.validate_on_submit():
                try:
                    # Create booking
                    booking_data = {
                        'hospital_id': form.hospital_id.data,
                        'patient_name': form.patient_name.data,
                        'patient_phone': form.patient_phone.data,
                        'emergency_level': form.emergency_level.data,
                        'symptoms': form.symptoms.data,
                        'estimated_arrival': form.estimated_arrival.data,
                        'special_requirements': form.special_requirements.data,
                        'created_by': session['user_id']
                    }
                    
                    # Validate booking
                    validation_result = validation_service.validate_booking_request(booking_data)
                    if not validation_result['valid']:
                        flash(f'Booking validation failed: {validation_result["message"]}', 'error')
                        return render_template('enhanced_booking.html', form=form)
                    
                    # Create booking (integrate with database)
                    booking_id = f"BK{datetime.now().strftime('%Y%m%d%H%M%S')}"
                    
                    # Emit real-time notification
                    realtime_service.emit_booking_update({
                        'booking_id': booking_id,
                        'hospital_id': booking_data['hospital_id'],
                        'status': 'created',
                        'timestamp': datetime.now().isoformat()
                    })
                    
                    # Send confirmation email (background task)
                    if form.patient_email.data:
                        task_service.submit_task(
                            'services.task_service.send_email_notification',
                            args=(
                                form.patient_email.data,
                                'Booking Confirmation',
                                f'Your emergency bed booking {booking_id} has been confirmed.'
                            )
                        )
                    
                    flash(f'Booking created successfully! Booking ID: {booking_id}', 'success')
                    return redirect(url_for('booking_status', booking_id=booking_id))
                    
                except Exception as e:
                    self.logger.error(f"Booking creation error: {str(e)}")
                    flash('Booking failed due to server error.', 'error')
            
            return render_template('enhanced_booking.html', form=form)
        
        @self.app.route('/booking-status/<booking_id>')
        def booking_status(booking_id: str):
            """Real-time booking status tracking"""
            if 'user_id' not in session:
                return redirect(url_for('login'))
            
            # Get booking details (integrate with database)
            booking_data = {
                'booking_id': booking_id,
                'status': 'confirmed',
                'hospital_name': 'City General Hospital',
                'patient_name': 'John Doe',
                'created_at': datetime.now().isoformat()
            }
            
            return render_template('booking_status.html', booking=booking_data)
        
        # Analytics Routes
        @self.app.route('/analytics')
        def analytics():
            """Advanced analytics dashboard"""
            if 'user_id' not in session:
                return redirect(url_for('login'))
            
            # Check permissions
            user_role = session.get('role', 'user')
            if not RoleBasedAuth.check_permission(user_role, 'analytics', 'read'):
                flash('Access denied. Insufficient permissions.', 'error')
                return redirect(url_for('index'))
            
            return render_template('analytics_dashboard.html')
        
        @self.app.route('/reports')
        def reports():
            """Report generation and export"""
            if 'user_id' not in session:
                return redirect(url_for('login'))
            
            # Check permissions
            user_role = session.get('role', 'user')
            if not RoleBasedAuth.check_permission(user_role, 'reports', 'read'):
                flash('Access denied. Insufficient permissions.', 'error')
                return redirect(url_for('index'))
            
            # Get recent exports and backups
            recent_exports = export_service.list_exports(days=30)
            recent_backups = export_service.list_backups(days=30)
            
            return render_template(
                'reports.html',
                exports=recent_exports,
                backups=recent_backups
            )
        
        @self.app.route('/export-data', methods=['POST'])
        def export_data():
            """Handle data export requests"""
            if 'user_id' not in session:
                return redirect(url_for('login'))
            
            # Check permissions
            user_role = session.get('role', 'user')
            if not RoleBasedAuth.check_permission(user_role, 'export', 'create'):
                return jsonify({'error': 'Access denied'}), 403
            
            try:
                data = request.get_json()
                
                # Create export request
                export_request = ExportRequest(
                    format=ExportFormat(data['format']),
                    tables=data['tables'],
                    filters=data.get('filters'),
                    date_range=data.get('date_range'),
                    compression=data.get('compression', 'none')
                )
                
                # Submit export task
                task_id = task_service.submit_task(
                    'services.task_service.generate_analytics_report',
                    kwargs={
                        'report_type': 'custom_export',
                        'parameters': {
                            'export_request': export_request.__dict__,
                            'user_id': session['user_id']
                        }
                    }
                )
                
                return jsonify({
                    'success': True,
                    'task_id': task_id,
                    'message': 'Export task submitted successfully'
                })
                
            except Exception as e:
                self.logger.error(f"Export error: {str(e)}")
                return jsonify({'error': 'Export failed'}), 500
        
        # Task Management Routes
        @self.app.route('/tasks/<task_id>/status')
        def task_status(task_id: str):
            """Get background task status"""
            if 'user_id' not in session:
                return jsonify({'error': 'Authentication required'}), 401
            
            try:
                task_result = task_service.get_task_status(task_id)
                return jsonify({
                    'success': True,
                    'task': {
                        'id': task_result.task_id,
                        'status': task_result.status.value,
                        'progress': task_result.progress,
                        'result': task_result.result,
                        'error': task_result.error
                    }
                })
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        # Admin Routes
        @self.app.route('/admin')
        def admin():
            """Administrative dashboard"""
            if 'user_id' not in session:
                return redirect(url_for('login'))
            
            # Check admin permissions
            user_role = session.get('role', 'user')
            if not RoleBasedAuth.check_permission(user_role, 'admin', 'read'):
                flash('Access denied. Administrator privileges required.', 'error')
                return redirect(url_for('index'))
            
            # Get system metrics
            system_metrics = {
                'active_users': 25,
                'total_bookings': 150,
                'system_uptime': '99.9%',
                'active_tasks': len(task_service.get_active_tasks())
            }
            
            return render_template('admin_dashboard.html', metrics=system_metrics)
        
        # WebSocket Events
        @self.socketio.on('connect')
        def handle_connect(auth=None):
            """Handle WebSocket connection"""
            if 'user_id' not in session:
                return False  # Reject connection
            
            user_id = session['user_id']
            join_room(f'user_{user_id}')
            
            # Send initial data
            emit('connected', {
                'message': 'Connected to real-time updates',
                'timestamp': datetime.now().isoformat()
            })
            
            self.logger.info(f"WebSocket connected: user {user_id}")
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """Handle WebSocket disconnection"""
            if 'user_id' in session:
                user_id = session['user_id']
                leave_room(f'user_{user_id}')
                self.logger.info(f"WebSocket disconnected: user {user_id}")
        
        @self.socketio.on('subscribe_updates')
        def handle_subscribe_updates(data):
            """Subscribe to specific update channels"""
            if 'user_id' not in session:
                return
            
            channel = data.get('channel')
            if channel in ['utilization', 'bookings', 'alerts']:
                join_room(f'updates_{channel}')
                emit('subscribed', {'channel': channel})
    
    def setup_error_handlers(self):
        """Setup custom error handlers"""
        
        @self.app.errorhandler(404)
        def not_found(error):
            return render_template('errors/404.html'), 404
        
        @self.app.errorhandler(500)
        def internal_error(error):
            self.logger.error(f"Internal server error: {str(error)}")
            return render_template('errors/500.html'), 500
        
        @self.app.errorhandler(403)
        def forbidden(error):
            return render_template('errors/403.html'), 403
        
        @self.app.errorhandler(429)
        def rate_limit_exceeded(error):
            return render_template('errors/429.html'), 429
    
    def setup_background_tasks(self):
        """Setup recurring background tasks"""
        
        # Schedule periodic tasks
        @self.celery.on_after_configure.connect
        def setup_periodic_tasks(sender, **kwargs):
            # Process utilization every 5 minutes
            sender.add_periodic_task(
                300.0,  # 5 minutes
                task_service.process_bed_utilization.s(),
                name='process_bed_utilization'
            )
            
            # Generate daily reports
            sender.add_periodic_task(
                86400.0,  # 24 hours
                task_service.generate_daily_reports.s(),
                name='generate_daily_reports'
            )
            
            # Cleanup old data weekly
            sender.add_periodic_task(
                604800.0,  # 7 days
                task_service.cleanup_old_data.s(),
                name='cleanup_old_data'
            )
    
    def complete_login(self, user: Dict):
        """Complete user login process"""
        session.permanent = True
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['role'] = user.get('role', 'user')
        session['hospital_id'] = user.get('hospital_id')
        session['last_activity'] = datetime.now().isoformat()
        
        # Update last login timestamp (integrate with database)
        auth_service.update_last_login(user['id'])
        
        # Log security event
        security_logger = logging.getLogger('security')
        security_logger.info(f"Successful login: {user['username']} from {request.remote_addr}")
    
    def run(self, debug=False, host='0.0.0.0', port=5000):
        """Run the enhanced application"""
        self.logger.info("Starting Enhanced Emergency Booking System")
        self.logger.info("Features: Analytics, API, Background Tasks, Real-time Updates")
        
        try:
            self.socketio.run(
                self.app,
                debug=debug,
                host=host,
                port=port,
                use_reloader=debug,
                log_output=True
            )
        except Exception as e:
            self.logger.error(f"Failed to start application: {str(e)}")
            raise

# Create and configure the enhanced application
def create_app():
    """Application factory function"""
    return EnhancedEmergencyBookingApp()

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Enhanced Emergency Hospital Bed Booking System')
    parser.add_argument('--debug', action='store_true', help='Run in debug mode')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=5000, help='Port to bind to')
    
    args = parser.parse_args()
    
    # Create and run the application
    app = create_app()
    app.run(debug=args.debug, host=args.host, port=args.port)
