# Security Guide

This document outlines security best practices and measures implemented in the Emergency Hospital Bed Booking System.

## 🔐 Credential Management

### ⚠️ CRITICAL: Never Commit Secrets to Version Control

**Files that must NEVER be committed:**

- `*firebase*adminsdk*.json` - Firebase service account keys
- `project/templates/config.json` - Database credentials
- `.env` - Environment variables with sensitive data
- Any file containing private keys, passwords, or API keys

### Secure Credential Setup

1. **Environment Variables Setup**:

   ```bash
   # Copy the template
   cp .env.example .env
   
   # Edit with your values
   nano .env  # or your preferred editor
   
   # Set restrictive permissions
   chmod 600 .env
   ```

2. **Firebase Credentials**:

   ```bash
   # Place Firebase key in secure location
   mv your-firebase-key.json project/firebase-credentials.json
   chmod 600 project/firebase-credentials.json
   ```

3. **Database Configuration**:

   ```bash
   # Copy config template
   cp project/templates/config.json.example project/templates/config.json
   
   # Edit with your database credentials
   nano project/templates/config.json
   chmod 600 project/templates/config.json
   ```

### Production Security Checklist

- [ ] All sensitive files added to `.gitignore`
- [ ] Environment variables properly configured
- [ ] File permissions set to 600 for credential files
- [ ] No hardcoded secrets in source code
- [ ] Regular credential rotation scheduled
- [ ] Backup credentials stored securely

## Authentication & Authorization

### Password Security

- **Password Hashing**: Werkzeug's PBKDF2 SHA-256 hashing
- **Salt Generation**: Automatic salt generation for each password
- **Password Requirements**: Enforce strong password policies

```python
from werkzeug.security import generate_password_hash, check_password_hash

# Password hashing
hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

# Password verification
is_valid = check_password_hash(hashed_password, password)
```

### Session Management

- **Flask-Login**: Secure session handling
- **Session Timeout**: Configurable session expiration
- **Secure Cookies**: HTTPOnly and Secure flags enabled

```python
from flask_login import LoginManager, login_required

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.session_protection = 'strong'
```

### Role-Based Access Control

- **Patient Access**: Limited to booking and viewing own data
- **Hospital Staff**: Manage hospital data and view patient details
- **Administrator**: Full system access and user management

## Input Validation & Sanitization

### Form Validation

- **Server-side Validation**: All inputs validated on server
- **Data Type Checking**: Strict type enforcement
- **Length Limits**: Maximum input length restrictions

```python
def validate_hospital_code(hcode):
    if not hcode or len(hcode) > 20:
        return False
    return hcode.isalnum()

def validate_email(email):
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None
```

### SQL Injection Prevention

- **SQLAlchemy ORM**: Prevents SQL injection attacks
- **Parameterized Queries**: All database queries use parameters
- **Input Escaping**: Automatic input escaping

```python
# Safe query using SQLAlchemy
user = User.query.filter_by(email=email).first()

# Avoid raw SQL queries
# cursor.execute("SELECT * FROM users WHERE email = '%s'" % email)  # NEVER DO THIS
```

## Data Protection

### Database Security

- **Connection Encryption**: SSL/TLS for database connections
- **User Privileges**: Minimal required privileges for database users
- **Regular Backups**: Encrypted backup storage

```sql
-- Create limited privilege user
CREATE USER 'app_user'@'localhost' IDENTIFIED BY 'strong_password';
GRANT SELECT, INSERT, UPDATE, DELETE ON emergency_bed.* TO 'app_user'@'localhost';
FLUSH PRIVILEGES;
```

### File Upload Security

- **File Type Validation**: Allowed file types only
- **File Size Limits**: Maximum upload size restrictions
- **Virus Scanning**: Optional virus scanning integration

```python
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'doc', 'docx'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
```

### Data Encryption

- **Sensitive Data**: Encrypt sensitive information at rest
- **Environment Variables**: Store secrets in environment variables
- **API Keys**: Secure API key storage and rotation

```python
import os
from cryptography.fernet import Fernet

# Generate encryption key
key = Fernet.generate_key()
cipher_suite = Fernet(key)

# Encrypt sensitive data
encrypted_data = cipher_suite.encrypt(b"sensitive_information")
```

## Network Security

### HTTPS Implementation

- **SSL/TLS**: Force HTTPS in production
- **HSTS Headers**: HTTP Strict Transport Security
- **Certificate Management**: Regular certificate renewal

```nginx
server {
    listen 443 ssl http2;
    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options DENY;
    add_header X-XSS-Protection "1; mode=block";
}
```

### Firewall Configuration

- **Port Restrictions**: Only necessary ports open
- **IP Whitelisting**: Restrict admin access by IP
- **Rate Limiting**: Prevent brute force attacks

```bash
# UFW firewall rules
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow http
sudo ufw allow https
sudo ufw enable
```

## Application Security

### CSRF Protection

- **CSRF Tokens**: Protect against cross-site request forgery
- **Same-Origin Policy**: Verify request origins
- **Secure Headers**: Implement security headers

```python
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect(app)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
```

### XSS Prevention

- **Output Encoding**: Encode all user output
- **Content Security Policy**: Implement CSP headers
- **Input Sanitization**: Sanitize all user inputs

```python
from markupsafe import escape

# Template escaping (automatic in Jinja2)
{{ user_input|e }}

# Manual escaping
safe_output = escape(user_input)
```

### Security Headers

```python
@app.after_request
def set_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    return response
```

## Error Handling & Logging

### Secure Error Handling

- **Error Sanitization**: Never expose sensitive information in errors
- **Custom Error Pages**: User-friendly error messages
- **Logging**: Comprehensive security logging

```python
@app.errorhandler(500)
def internal_error(error):
    app.logger.error(f'Server Error: {error}')
    return render_template('500.html'), 500

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404
```

### Security Logging

```python
import logging
from logging.handlers import RotatingFileHandler

# Security event logging
security_logger = logging.getLogger('security')
handler = RotatingFileHandler('logs/security.log', maxBytes=10000, backupCount=3)
handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
))
security_logger.addHandler(handler)
security_logger.setLevel(logging.INFO)

# Log security events
def log_security_event(event_type, user_id, details):
    security_logger.info(f'SECURITY_EVENT: {event_type} | User: {user_id} | Details: {details}')
```

## Infrastructure Security

### Server Hardening

- **Regular Updates**: Keep system packages updated
- **Minimal Services**: Disable unnecessary services
- **User Privileges**: Run application with minimal privileges

```bash
# Disable unnecessary services
sudo systemctl disable telnet
sudo systemctl disable ftp

# Update system packages
sudo apt update && sudo apt upgrade -y

# Configure automatic security updates
sudo apt install unattended-upgrades -y
```

### Database Hardening

- **Root Access**: Disable remote root access
- **Anonymous Users**: Remove anonymous user accounts
- **Test Databases**: Remove test databases

```sql
-- MySQL security hardening
DELETE FROM mysql.user WHERE User='';
DELETE FROM mysql.user WHERE User='root' AND Host NOT IN ('localhost', '127.0.0.1', '::1');
DROP DATABASE IF EXISTS test;
DELETE FROM mysql.db WHERE Db='test' OR Db='test\\_%';
FLUSH PRIVILEGES;
```

## Monitoring & Incident Response

### Security Monitoring

- **Failed Login Attempts**: Monitor and alert on multiple failures
- **Unusual Activity**: Detect abnormal usage patterns
- **File Changes**: Monitor critical file modifications

```python
# Failed login monitoring
@app.route('/login', methods=['POST'])
def login():
    attempts = get_failed_attempts(request.remote_addr)
    if attempts > MAX_ATTEMPTS:
        log_security_event('BRUTE_FORCE_DETECTED', None, request.remote_addr)
        return 'Too many failed attempts', 429
    
    # Login logic here
```

### Intrusion Detection

```bash
# Install and configure fail2ban
sudo apt install fail2ban -y

# Create jail configuration
sudo nano /etc/fail2ban/jail.local
```

```ini
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 3

[sshd]
enabled = true

[nginx-http-auth]
enabled = true
```

### Incident Response Plan

1. **Detection**: Automated monitoring and alerts
2. **Assessment**: Evaluate severity and impact
3. **Containment**: Isolate affected systems
4. **Eradication**: Remove threats and vulnerabilities
5. **Recovery**: Restore normal operations
6. **Documentation**: Record incident details and lessons learned

## Compliance & Privacy

### Data Privacy

- **Data Minimization**: Collect only necessary information
- **Data Retention**: Implement data retention policies
- **User Consent**: Obtain explicit consent for data processing

```python
# Data anonymization
def anonymize_patient_data(patient_id):
    patient = Bookingpatient.query.get(patient_id)
    patient.pname = f"Patient_{patient.id}"
    patient.pphone = "***-***-****"
    patient.paddress = "Anonymized"
    db.session.commit()
```

### Audit Trail

- **User Actions**: Log all user activities
- **Data Changes**: Track all data modifications
- **System Events**: Monitor system-level events

```python
def create_audit_log(user_id, action, resource, old_value=None, new_value=None):
    audit_entry = {
        'user_id': user_id,
        'action': action,
        'resource': resource,
        'old_value': old_value,
        'new_value': new_value,
        'timestamp': datetime.utcnow(),
        'ip_address': request.remote_addr
    }
    # Store in audit log table
```

## Security Testing

### Vulnerability Scanning

```bash
# Install security scanning tools
pip install bandit safety

# Scan for security vulnerabilities
bandit -r project/
safety check

# SQL injection testing
sqlmap -u "http://localhost:5000/login" --forms
```

### Penetration Testing

- **Regular Testing**: Schedule regular security assessments
- **Third-party Audits**: External security reviews
- **Bug Bounty Programs**: Community-driven security testing

## Security Configuration Checklist

### Application Level

- [ ] Strong password hashing implemented
- [ ] Session management configured securely
- [ ] Input validation on all forms
- [ ] SQL injection prevention measures
- [ ] XSS protection enabled
- [ ] CSRF protection implemented
- [ ] Secure error handling
- [ ] Security logging configured

### Infrastructure Level

- [ ] HTTPS enforced in production
- [ ] Security headers implemented
- [ ] Firewall configured properly
- [ ] Database access restricted
- [ ] File upload security measures
- [ ] Regular security updates
- [ ] Monitoring and alerting setup
- [ ] Backup encryption enabled

### Operational Level

- [ ] Security policies documented
- [ ] Incident response plan ready
- [ ] Staff security training completed
- [ ] Regular security audits scheduled
- [ ] Vulnerability management process
- [ ] Access control procedures
- [ ] Data retention policies
- [ ] Compliance requirements met

## Emergency Procedures

### Security Incident Response

1. **Immediate Actions**
   - Isolate affected systems
   - Preserve evidence
   - Notify stakeholders

2. **Investigation**
   - Analyze logs and system state
   - Determine scope and impact
   - Identify root cause

3. **Recovery**
   - Patch vulnerabilities
   - Restore from clean backups
   - Implement additional safeguards

4. **Post-Incident**
   - Document lessons learned
   - Update security procedures
   - Conduct security review

### Contact Information

- **Security Team**: <security@hospital-booking.com>
- **Emergency Hotline**: +1-XXX-XXX-XXXX
- **Legal Department**: <legal@hospital-booking.com>
- **Third-party Security**: <vendor-security@security-firm.com>

## Security Resources

### Documentation

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Flask Security Guidelines](https://flask.palletsprojects.com/en/2.0.x/security/)
- [MySQL Security Best Practices](https://dev.mysql.com/doc/refman/8.0/en/security-guidelines.html)

### Tools

- [Bandit](https://bandit.readthedocs.io/) - Python security linter
- [Safety](https://pyup.io/safety/) - Python dependency checker
- [OWASP ZAP](https://www.zaproxy.org/) - Web application security scanner
- [Nmap](https://nmap.org/) - Network security scanner

Remember: Security is an ongoing process, not a one-time setup. Regular reviews and updates are essential for maintaining a secure system.
