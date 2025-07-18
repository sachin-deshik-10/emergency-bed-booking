# Deployment Guide

This guide provides step-by-step instructions for deploying the Emergency Hospital Bed Booking System in different environments.

## Prerequisites

- Python 3.8 or higher
- MySQL 8.0 or higher
- Firebase account with Storage enabled
- Web server (Apache/Nginx) for production
- SSL certificate for production deployment

## Local Development Deployment

### 1. Clone Repository

```bash
git clone https://github.com/sachin-deshik-10/emergency-bed-booking.git
cd emergency-bed-booking
```

### 2. Set Up Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Database Setup

```bash
mysql -u root -p
CREATE DATABASE emergency_bed;
```

### 5. Secure Credential Setup

⚠️ **CRITICAL**: Never commit credentials to version control. Follow these steps:

```bash
# 1. Copy environment template
cp .env.example .env

# 2. Copy config template  
cp project/templates/config.json.example project/templates/config.json

# 3. Set up Firebase credentials
# Download your Firebase service account key from Firebase Console
# Place it as: project/firebase-credentials.json
```

**Edit `.env` with your values**:

```env
SECRET_KEY=generate-a-strong-secret-key
DATABASE_URL=mysql+mysqldb://root:your_password@localhost/emergency_bed
FIREBASE_CREDENTIALS_PATH=project/firebase-credentials.json
FIREBASE_STORAGE_BUCKET=your-project.appspot.com
```

**Edit `project/templates/config.json` with your database credentials**:

```json
{
    "params": {
        "user": "your_mysql_username",
        "password": "your_mysql_password",
        "gmail-user": "your_gmail@example.com",
        "gmail-password": "your_app_password"
    }
}
```

**Set secure file permissions**:

```bash
chmod 600 .env
chmod 600 project/firebase-credentials.json
chmod 600 project/templates/config.json
```

### 6. Initialize Database

```python
python -c "from project.main import app, dbsql; app.app_context().push(); dbsql.create_all()"
```

### 7. Run Application

```bash
cd project
python main.py
```

The application will be available at `http://localhost:5000`

## Production Deployment

### Option 1: Manual Server Deployment

#### 1. Server Preparation

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install python3 python3-pip python3-venv mysql-server nginx supervisor -y

# Install MySQL development headers
sudo apt install libmysqlclient-dev -y
```

#### 2. MySQL Configuration

```bash
sudo mysql_secure_installation

# Create database and user
sudo mysql -u root -p
```

```sql
CREATE DATABASE emergency_bed CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'emergency_user'@'localhost' IDENTIFIED BY 'secure_password_here';
GRANT ALL PRIVILEGES ON emergency_bed.* TO 'emergency_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

#### 3. Application Setup

```bash
# Create application directory
sudo mkdir -p /var/www/emergency-bed-booking
cd /var/www/emergency-bed-booking

# Clone repository
sudo git clone https://github.com/yourusername/emergency-bed-booking.git .

# Set up virtual environment
sudo python3 -m venv venv
sudo ./venv/bin/pip install -r requirements.txt

# Set permissions
sudo chown -R www-data:www-data /var/www/emergency-bed-booking
sudo chmod -R 755 /var/www/emergency-bed-booking
```

#### 4. Environment Configuration

```bash
sudo cp .env.example .env
sudo nano .env
```

Update with production values:

```env
SECRET_KEY=your-super-secure-secret-key-here
FLASK_ENV=production
FLASK_DEBUG=False
DATABASE_URL=mysql+mysqldb://emergency_user:secure_password_here@localhost/emergency_bed
```

#### 5. Initialize Database

```bash
sudo -u www-data ./venv/bin/python -c "from project.main import app, dbsql; app.app_context().push(); dbsql.create_all()"
```

#### 6. Gunicorn Setup

```bash
sudo ./venv/bin/pip install gunicorn

# Create Gunicorn configuration
sudo nano /var/www/emergency-bed-booking/gunicorn.conf.py
```

```python
bind = "127.0.0.1:5000"
workers = 4
worker_class = "sync"
worker_connections = 1000
timeout = 30
max_requests = 1000
max_requests_jitter = 100
preload_app = True
```

#### 7. Supervisor Configuration

```bash
sudo nano /etc/supervisor/conf.d/emergency-bed-booking.conf
```

```ini
[program:emergency-bed-booking]
command=/var/www/emergency-bed-booking/venv/bin/gunicorn -c gunicorn.conf.py project.main:app
directory=/var/www/emergency-bed-booking
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/emergency-bed-booking.log
```

```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start emergency-bed-booking
```

#### 8. Nginx Configuration

```bash
sudo nano /etc/nginx/sites-available/emergency-bed-booking
```

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /static {
        alias /var/www/emergency-bed-booking/project/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    client_max_body_size 5M;
}
```

```bash
sudo ln -s /etc/nginx/sites-available/emergency-bed-booking /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 9. SSL Certificate (Let's Encrypt)

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

### Option 2: Docker Deployment

#### 1. Create Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app && chown -R app:app /app
USER app

# Expose port
EXPOSE 5000

# Run application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "project.main:app"]
```

#### 2. Create Docker Compose

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - DATABASE_URL=mysql+mysqldb://emergency_user:password@db:3306/emergency_bed
    depends_on:
      - db
    volumes:
      - ./uploads:/app/uploads
    restart: unless-stopped

  db:
    image: mysql:8.0
    environment:
      - MYSQL_ROOT_PASSWORD=rootpassword
      - MYSQL_DATABASE=emergency_bed
      - MYSQL_USER=emergency_user
      - MYSQL_PASSWORD=password
    volumes:
      - mysql_data:/var/lib/mysql
      - ./db-init:/docker-entrypoint-initdb.d
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - web
    restart: unless-stopped

volumes:
  mysql_data:
```

#### 3. Deploy with Docker

```bash
docker-compose up -d
```

### Option 3: Cloud Platform Deployment

#### Heroku Deployment

1. **Prepare Application**

```bash
# Create Procfile
echo "web: gunicorn project.main:app" > Procfile

# Create runtime.txt
echo "python-3.9.20" > runtime.txt
```

2. **Heroku Setup**

```bash
heroku create emergency-bed-booking
heroku addons:create cleardb:ignite
heroku config:set SECRET_KEY=your-secret-key
heroku config:set FLASK_ENV=production
```

3. **Deploy**

```bash
git add .
git commit -m "Prepare for Heroku deployment"
git push heroku main
```

#### AWS EC2 Deployment

1. **Launch EC2 Instance**
   - Use Ubuntu 20.04 LTS
   - Configure security groups (HTTP, HTTPS, SSH)
   - Create or select key pair

2. **Connect and Setup**

```bash
ssh -i your-key.pem ubuntu@your-ec2-ip
sudo apt update && sudo apt upgrade -y
```

3. **Follow Manual Server Deployment steps** above

#### DigitalOcean Droplet

1. **Create Droplet**
   - Ubuntu 20.04 LTS
   - Configure firewall
   - Add SSH keys

2. **Setup Application**
   - Follow Manual Server Deployment guide
   - Configure domain and SSL

## Environment-Specific Configurations

### Development Environment

```env
FLASK_ENV=development
FLASK_DEBUG=True
DATABASE_URL=mysql+mysqldb://root:password@localhost/emergency_bed_dev
```

### Staging Environment

```env
FLASK_ENV=staging
FLASK_DEBUG=False
DATABASE_URL=mysql+mysqldb://staging_user:password@staging-db/emergency_bed_staging
```

### Production Environment

```env
FLASK_ENV=production
FLASK_DEBUG=False
DATABASE_URL=mysql+mysqldb://prod_user:secure_password@prod-db/emergency_bed
```

## Security Hardening

### 1. Firewall Configuration

```bash
sudo ufw allow ssh
sudo ufw allow http
sudo ufw allow https
sudo ufw enable
```

### 2. Fail2Ban Setup

```bash
sudo apt install fail2ban -y
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

### 3. Regular Updates

```bash
# Create update script
sudo nano /usr/local/bin/security-updates.sh
```

```bash
#!/bin/bash
apt update
apt upgrade -y
apt autoremove -y
```

```bash
sudo chmod +x /usr/local/bin/security-updates.sh
sudo crontab -e
```

Add line:

```
0 2 * * * /usr/local/bin/security-updates.sh
```

## Monitoring and Logging

### 1. Application Logging

```python
import logging
from logging.handlers import RotatingFileHandler

if not app.debug:
    file_handler = RotatingFileHandler('logs/emergency_bed.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
```

### 2. System Monitoring

```bash
# Install monitoring tools
sudo apt install htop iotop nethogs -y

# Monitor application
sudo supervisorctl status
sudo tail -f /var/log/emergency-bed-booking.log
```

## Backup Strategy

### 1. Database Backup

```bash
# Create backup script
sudo nano /usr/local/bin/db-backup.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/backups/mysql"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

mysqldump -u emergency_user -p emergency_bed > $BACKUP_DIR/emergency_bed_$DATE.sql
gzip $BACKUP_DIR/emergency_bed_$DATE.sql

# Keep only last 7 days
find $BACKUP_DIR -name "*.sql.gz" -mtime +7 -delete
```

### 2. Application Backup

```bash
# Backup uploaded files
tar -czf /backups/uploads_$(date +%Y%m%d).tar.gz /var/www/emergency-bed-booking/uploads/
```

## Performance Optimization

### 1. Database Optimization

```sql
-- Add indexes for better performance
CREATE INDEX idx_booking_date ON bookingpatient(created_at);
CREATE INDEX idx_hospital_beds ON hospitaldata(normalbed, hicubed, icubed, vbed);
```

### 2. Caching

```python
from flask_caching import Cache

cache = Cache(app, config={'CACHE_TYPE': 'simple'})

@cache.cached(timeout=300)
def get_available_beds():
    return Hospitaldata.query.all()
```

### 3. Static File Optimization

```nginx
location /static {
    alias /var/www/emergency-bed-booking/project/static;
    expires 1y;
    add_header Cache-Control "public, immutable";
    gzip on;
    gzip_types text/css application/javascript;
}
```

## Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Check MySQL service status
   - Verify credentials in .env
   - Check firewall rules

2. **Permission Denied Errors**
   - Verify file ownership: `sudo chown -R www-data:www-data /var/www/emergency-bed-booking`
   - Check file permissions: `sudo chmod -R 755 /var/www/emergency-bed-booking`

3. **Application Not Loading**
   - Check supervisor status: `sudo supervisorctl status`
   - Review logs: `sudo tail -f /var/log/emergency-bed-booking.log`
   - Check nginx status: `sudo systemctl status nginx`

### Logs Location

- Application logs: `/var/log/emergency-bed-booking.log`
- Nginx logs: `/var/log/nginx/access.log`, `/var/log/nginx/error.log`
- MySQL logs: `/var/log/mysql/error.log`
- Supervisor logs: `/var/log/supervisor/supervisord.log`

## Post-Deployment Checklist

- [ ] Application is accessible via domain
- [ ] SSL certificate is working
- [ ] Database connections are successful
- [ ] File uploads are working
- [ ] All pages load without errors
- [ ] Authentication system is functional
- [ ] Email notifications are working (if configured)
- [ ] Monitoring and logging are active
- [ ] Backup system is configured
- [ ] Security measures are in place
- [ ] Performance is optimized

## Support and Maintenance

### Regular Maintenance Tasks

1. **Weekly**
   - Review application logs
   - Check disk space usage
   - Verify backup integrity

2. **Monthly**
   - Update system packages
   - Review security logs
   - Database optimization

3. **Quarterly**
   - Security audit
   - Performance review
   - Backup strategy evaluation

For technical support, please refer to the project's GitHub repository or contact the development team.
