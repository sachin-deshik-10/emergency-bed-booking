# Enhanced Emergency Hospital Bed Booking System - User Guide

## 🚀 Overview

The Enhanced Emergency Hospital Bed Booking System is a comprehensive web application designed to manage hospital bed availability with advanced security features, real-time updates, and multi-factor authentication.

## ✨ New Enhanced Features

### 🔒 Advanced Security
- **Multi-Factor Authentication (MFA)** with TOTP (Time-based One-Time Passwords)
- **Role-Based Access Control (RBAC)** for different user types
- **Rate Limiting** to prevent abuse and brute force attacks
- **CSRF Protection** on all forms
- **Input Validation & Sanitization** to prevent XSS and injection attacks
- **Secure Session Management** with automatic expiration
- **Comprehensive Audit Logging** for security monitoring

### ⚡ Real-Time Features
- **Live Bed Availability Updates** using WebSocket technology
- **Real-Time Emergency Alerts** for critical situations
- **Instant Notifications** for booking confirmations
- **Live System Status** indicators
- **Auto-Refresh Dashboard** with live data

### 🛡️ Enhanced Data Protection
- **Environment-Based Configuration** for secure deployment
- **Encrypted Password Storage** using PBKDF2 with salt
- **Secure File Upload** handling with validation
- **SQL Injection Prevention** through parameterized queries
- **XSS Protection** with input sanitization

## 📋 Prerequisites

### System Requirements
- **Python 3.8 or higher**
- **MySQL 8.0 or higher**
- **Redis 6.0 or higher** (recommended for real-time features)
- **Modern web browser** with JavaScript enabled

### Required Packages
All packages are listed in `requirements.txt`:
```
Flask>=2.3.0
Flask-SQLAlchemy>=3.0.0
Flask-WTF>=1.1.0
Flask-Limiter>=3.0.0
Flask-SocketIO>=5.3.0
python-socketio>=5.8.0
bcrypt>=4.0.0
PyOTP>=2.8.0
qrcode[pil]>=7.4.0
redis>=4.6.0
bleach>=6.0.0
cryptography>=41.0.0
Pillow>=10.0.0
python-decouple>=3.8
email-validator>=2.0.0
WTForms>=3.0.0
```

## 🛠️ Installation

### Quick Setup (Windows)
1. **Run the PowerShell setup script:**
   ```powershell
   .\setup_enhanced.ps1
   ```

### Quick Setup (Linux/Mac)
1. **Run the bash setup script:**
   ```bash
   chmod +x setup_enhanced.sh
   ./setup_enhanced.sh
   ```

### Manual Setup
1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd emergency-bed-booking-clean
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Setup database:**
   ```bash
   python migrate_db.py
   ```

6. **Test installation:**
   ```bash
   python test_enhanced_system.py
   ```

## ⚙️ Configuration

### Environment Variables (.env)
```env
# Database Configuration
DATABASE_URL=mysql://username:password@localhost/emergency_bed
DB_HOST=localhost
DB_USER=your_username
DB_PASSWORD=your_password
DB_NAME=emergency_bed

# Security Configuration
SECRET_KEY=your-secret-key-here
CSRF_SECRET_KEY=your-csrf-secret-key
FLASK_ENV=development
FLASK_DEBUG=True

# Redis Configuration (for real-time features)
REDIS_URL=redis://localhost:6379/0
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Email Configuration (for MFA)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# Security Settings
SESSION_PERMANENT=False
SESSION_TIMEOUT=3600
MAX_LOGIN_ATTEMPTS=5
RATE_LIMIT_DEFAULT=100 per hour

# Firebase Configuration (for file uploads)
FIREBASE_CREDENTIALS_PATH=project/credentials/firebase-key.json
```

### Database Configuration (config.json)
```json
{
    "host": "localhost",
    "user": "your_username", 
    "password": "your_password",
    "database": "emergency_bed"
}
```

## 🚀 Running the Application

### Development Mode
```bash
# Using the startup script
./start_app.sh        # Linux/Mac
start_app.ps1          # Windows PowerShell
start_app.bat          # Windows Command Prompt

# Or manually
python project/enhanced_main.py
```

### Production Mode
```bash
# Set production environment
export FLASK_ENV=production
export FLASK_DEBUG=False

# Use a production WSGI server
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 --worker-class eventlet project.enhanced_main:app
```

## 👥 User Management

### Default Admin Account
- **Email:** admin@hospital.com
- **Password:** SecureAdmin123!
- **⚠️ Change this password immediately after first login**

### User Types

#### 1. Regular Users (Patients)
- Book hospital beds
- View bed availability
- Receive real-time updates
- Manage personal profile

#### 2. Hospital Users
- Manage hospital information
- Update bed availability
- View booking requests
- Access hospital dashboard

#### 3. Admin Users
- Manage all users and hospitals
- Access system logs
- Configure system settings
- Monitor real-time statistics

## 🔐 Security Features

### Multi-Factor Authentication (MFA)
1. **Enable MFA:**
   - Go to Profile Settings
   - Click "Enable MFA"
   - Scan QR code with authenticator app (Google Authenticator, Authy, etc.)
   - Enter verification code
   - Save backup codes

2. **Login with MFA:**
   - Enter email and password
   - Enter 6-digit code from authenticator app
   - Or use backup code if needed

### Password Requirements
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number
- At least one special character

### Account Security
- **Account Lockout:** After 5 failed login attempts
- **Session Timeout:** Automatic logout after inactivity
- **Secure Cookies:** HTTPOnly and Secure flags
- **CSRF Protection:** All forms protected

## ⚡ Real-Time Features

### Live Bed Availability
- Automatic updates every 30 seconds
- Instant updates when beds are booked/released
- Color-coded status indicators:
  - 🟢 Green: Available beds
  - 🟡 Yellow: Limited availability
  - 🔴 Red: No beds available

### Emergency Alerts
- Critical bed shortages
- System maintenance notifications
- Emergency announcements

### Connection Status
- Real-time connection indicator
- Automatic reconnection
- Offline mode support

## 📊 Dashboard Features

### Hospital Dashboard
- Real-time bed count
- Recent bookings
- Occupancy statistics
- Emergency alerts

### Admin Dashboard
- System overview
- User management
- Hospital management
- Security logs
- Performance metrics

## 🔧 API Endpoints

### Authentication
- `POST /api/login` - User login
- `POST /api/logout` - User logout
- `POST /api/mfa/enable` - Enable MFA
- `POST /api/mfa/verify` - Verify MFA code

### Bed Management
- `GET /api/beds/availability` - Get bed availability
- `POST /api/beds/book` - Book a bed
- `PUT /api/beds/update` - Update bed status
- `DELETE /api/beds/cancel` - Cancel booking

### Real-Time Events
- `bed_update` - Bed availability changed
- `emergency_alert` - Emergency notification
- `user_notification` - User-specific message

## 🐛 Troubleshooting

### Common Issues

#### 1. Application Won't Start
```bash
# Check Python version
python --version

# Check dependencies
pip list

# Run diagnostics
python test_enhanced_system.py
```

#### 2. Database Connection Failed
- Verify MySQL is running
- Check database credentials in .env
- Ensure database exists: `CREATE DATABASE emergency_bed;`

#### 3. Redis Connection Failed
- Start Redis: `redis-server`
- Check Redis status: `redis-cli ping`
- Real-time features will be limited without Redis

#### 4. MFA Not Working
- Check system time (TOTP is time-sensitive)
- Verify QR code scanning
- Use backup codes if needed

#### 5. File Upload Issues
- Check Firebase credentials
- Verify file permissions
- Ensure uploads directory exists

### Log Files
- Application logs: `logs/app.log`
- Security logs: `logs/security.log`
- Error logs: `logs/error.log`

## 📈 Performance Optimization

### Database
- Regular backups
- Index optimization
- Connection pooling

### Redis
- Memory optimization
- Persistence configuration
- Clustering for high availability

### Application
- Enable caching
- Optimize database queries
- Use CDN for static files

## 🔒 Security Best Practices

### Production Deployment
1. **Use HTTPS:** Enable SSL/TLS certificates
2. **Secure Headers:** Implement security headers
3. **Environment Variables:** Never commit secrets
4. **Regular Updates:** Keep dependencies updated
5. **Monitoring:** Set up security monitoring
6. **Backups:** Regular database backups

### User Training
- Strong password policies
- MFA adoption
- Security awareness
- Incident reporting

## 📞 Support

### Getting Help
1. **Documentation:** Check this user guide
2. **Logs:** Review application logs
3. **Testing:** Run test suite
4. **Community:** Check project issues

### Reporting Issues
- Include error messages
- Provide steps to reproduce
- Include system information
- Check logs for details

## 🔄 Updates and Maintenance

### Regular Maintenance
- Update dependencies: `pip install -r requirements.txt --upgrade`
- Database maintenance: Regular backups and optimization
- Log rotation: Prevent log files from growing too large
- Security updates: Keep all components updated

### Version Management
- Follow semantic versioning
- Test updates in staging environment
- Backup before major updates
- Document configuration changes

---

## 📚 Additional Resources

- **API Documentation:** See `API_DOCUMENTATION.md`
- **Database Schema:** See `DATABASE_SETUP.md`
- **Deployment Guide:** See `DEPLOYMENT.md`
- **Security Guidelines:** See `SECURITY.md`
- **Testing Guide:** See `TESTING.md`

---

**© 2024 Enhanced Emergency Hospital Bed Booking System - Built with security and real-time features**
