# Troubleshooting Guide

This guide helps resolve common issues encountered while setting up and running the Emergency Hospital Bed Booking System.

## 🚫 Git Push Issues

### Secret Scanning Violations

**Problem**: GitHub blocks push with message about secret scanning violations.

**Solution**:

```bash
# 1. Remove sensitive files from tracking
git rm --cached project/emergencybooking-31043-firebase-adminsdk-l69k0-98c85bc3f2.json
git rm --cached nosql/emergencybooking-31043-firebase-adminsdk-l69k0-98c85bc3f2.json
git rm --cached project/templates/config.json

# 2. Ensure .gitignore is updated
# Check that these patterns are in .gitignore:
# *firebase*adminsdk*.json
# config.json
# .env

# 3. Commit the removal
git add .gitignore
git commit -m "Remove sensitive credentials and update .gitignore"

# 4. Push to repository
git push origin main
```

### Large File Issues

**Problem**: Files too large for GitHub.

**Solution**:

```bash
# Remove large files from tracking
git rm --cached path/to/large/file
git commit -m "Remove large files"
git push origin main
```

## 🔐 Credential Issues

### Firebase Authentication Errors

**Problem**: `FileNotFoundError` for Firebase credentials.

**Solution**:

1. Download Firebase service account key from console
2. Place as `project/firebase-credentials.json`
3. Update `.env` file with correct path:

   ```env
   FIREBASE_CREDENTIALS_PATH=project/firebase-credentials.json
   ```

### Database Connection Errors

**Problem**: `Access denied for user` or connection refused.

**Solution**:

1. Check MySQL service is running:

   ```bash
   # Windows
   net start mysql
   
   # Linux/Mac
   sudo systemctl start mysql
   ```

2. Verify credentials in `project/templates/config.json`:

   ```json
   {
       "params": {
           "user": "correct_username",
           "password": "correct_password"
       }
   }
   ```

3. Test database connection:

   ```bash
   mysql -u username -p database_name
   ```

## 🐍 Python Environment Issues

### Module Not Found Errors

**Problem**: `ModuleNotFoundError` for required packages.

**Solution**:

```bash
# Activate virtual environment
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# If specific module missing
pip install module_name
```

### Permission Denied Errors

**Problem**: Cannot write to directories or files.

**Solution**:

```bash
# Linux/Mac - Fix permissions
chmod 755 project/
chmod 644 project/*.py
chmod 600 .env
chmod 600 project/firebase-credentials.json

# Windows - Run as administrator if needed
```

## 🌐 Web Application Issues

### Port Already in Use

**Problem**: `Address already in use` error.

**Solution**:

```bash
# Find process using port 5000
netstat -tulpn | grep 5000  # Linux/Mac
netstat -ano | findstr 5000 # Windows

# Kill the process or use different port
python project/main.py --port 5001
```

### Template Not Found

**Problem**: `TemplateNotFound` error.

**Solution**:

1. Check template files exist in `project/templates/`
2. Verify template names in route handlers
3. Ensure Flask app knows template directory:

   ```python
   app = Flask(__name__, template_folder='templates')
   ```

### Static Files Not Loading

**Problem**: CSS/JS files not loading (404 errors).

**Solution**:

1. Check files exist in `project/static/`
2. Verify static URL configuration:

   ```python
   app = Flask(__name__, static_folder='static')
   ```

3. Clear browser cache
4. Check file permissions

## 🗄️ Database Issues

### Table Doesn't Exist

**Problem**: `Table 'database.table' doesn't exist`.

**Solution**:

```python
# Run in Python shell
from project.main import app, db
with app.app_context():
    db.create_all()
```

### Migration Issues

**Problem**: Database schema out of sync.

**Solution**:

1. Backup existing data
2. Drop and recreate database:

   ```sql
   DROP DATABASE emergency_bed;
   CREATE DATABASE emergency_bed;
   ```

3. Recreate tables with updated schema

## 🔧 Development Environment

### IDE Configuration Issues

**Problem**: VS Code not recognizing Python environment.

**Solution**:

1. Open VS Code in project directory
2. Select Python interpreter: `Ctrl+Shift+P` → "Python: Select Interpreter"
3. Choose the virtual environment interpreter

### Git Configuration

**Problem**: Git username/email not set.

**Solution**:

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

## 🚀 Production Deployment Issues

### Environment Variables

**Problem**: App works locally but not in production.

**Solution**:

1. Check all environment variables are set in production
2. Use production-ready database settings
3. Set `FLASK_ENV=production`
4. Disable debug mode: `FLASK_DEBUG=False`

### SSL Certificate Issues

**Problem**: HTTPS not working in production.

**Solution**:

1. Verify SSL certificate is valid
2. Check certificate chain is complete
3. Ensure proper nginx/Apache configuration
4. Test with SSL checker tools

## 📱 Browser Compatibility

### JavaScript Errors

**Problem**: Features not working in certain browsers.

**Solution**:

1. Check browser console for errors
2. Verify JavaScript ES6+ features support
3. Add polyfills if needed
4. Test in multiple browsers

### CSS Layout Issues

**Problem**: Layout broken in some browsers.

**Solution**:

1. Use CSS vendor prefixes
2. Test responsive design on different screen sizes
3. Validate CSS with W3C validator
4. Check Bootstrap compatibility

## 🔍 Debugging Tips

### Enable Debug Mode

```python
# In main.py
app.debug = True
app.run(debug=True)
```

### Check Logs

```bash
# Application logs
tail -f logs/app.log

# System logs
tail -f /var/log/apache2/error.log  # Apache
tail -f /var/log/nginx/error.log    # Nginx
```

### Database Query Debugging

```python
# Enable SQLAlchemy logging
import logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
```

## 📞 Getting Help

If you continue to experience issues:

1. **Check the [GitHub Issues](https://github.com/sachin-deshik-10/emergency-bed-booking/issues)**
2. **Review the [Documentation](README.md)**
3. **Create a new issue** with:
   - Error messages
   - Steps to reproduce
   - System information
   - Screenshots if applicable

## 🛠️ Common Commands Reference

```bash
# Virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Dependencies
pip install -r requirements.txt
pip freeze > requirements.txt

# Database
mysql -u root -p
CREATE DATABASE emergency_bed;

# Git
git status
git add .
git commit -m "message"
git push origin main

# Run application
python project/main.py
```

---

*Remember: Always backup your data before making significant changes!*
