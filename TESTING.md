# Testing Guide

This document provides comprehensive testing guidelines and procedures for the Emergency Hospital Bed Booking System.

## Testing Overview

The testing strategy covers unit tests, integration tests, end-to-end tests, and security testing to ensure system reliability and functionality.

## Testing Environment Setup

### Prerequisites

```bash
# Install testing dependencies
pip install pytest pytest-flask pytest-cov selenium coverage bandit safety
```

### Test Configuration

Create `conftest.py` in the project root:

```python
import pytest
import tempfile
import os
from main import app, db, User, Hospitaluser, Hospitaldata, Bookingpatient

@pytest.fixture
def client():
    # Create temporary database
    db_fd, app.config['DATABASE'] = tempfile.mkstemp()
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
    
    os.close(db_fd)
    os.unlink(app.config['DATABASE'])

@pytest.fixture
def auth(client):
    return AuthActions(client)

class AuthActions:
    def __init__(self, client):
        self._client = client
    
    def login(self, email='test@example.com', password='testpass'):
        return self._client.post('/login', data={
            'email': email,
            'password': password
        })
    
    def logout(self):
        return self._client.get('/logout')
```

## Unit Testing

### Model Tests

Test database models and their methods:

```python
# tests/test_models.py
import pytest
from werkzeug.security import check_password_hash
from main import User, Hospitaluser, Hospitaldata, Bookingpatient

def test_user_password_hashing():
    """Test password hashing functionality"""
    user = User(
        fname='Test',
        lname='User',
        email='test@example.com',
        phone='1234567890'
    )
    user.set_password('testpass')
    
    assert user.password_hash is not None
    assert user.password_hash != 'testpass'
    assert check_password_hash(user.password_hash, 'testpass')
    assert not check_password_hash(user.password_hash, 'wrongpass')

def test_user_repr():
    """Test user string representation"""
    user = User(
        fname='Test',
        lname='User',
        email='test@example.com',
        phone='1234567890'
    )
    assert repr(user) == '<User test@example.com>'

def test_hospital_data_creation():
    """Test hospital data model creation"""
    hospital = Hospitaldata(
        hname='Test Hospital',
        hcode='TH001',
        hcity='Test City',
        hphone='9876543210',
        normalbed=100,
        hicubed=50,
        ventilatorbed=25,
        oxygenbed=75
    )
    
    assert hospital.hname == 'Test Hospital'
    assert hospital.normalbed == 100
    assert hospital.available_beds() == 250  # If this method exists

def test_booking_patient_creation():
    """Test patient booking model"""
    booking = Bookingpatient(
        srfid='SRF001',
        pname='John Doe',
        pphone='1111111111',
        paddress='123 Test St',
        hcode='TH001',
        bedtype='Normal',
        spo2='95',
        pulserate='80',
        respirationrate='18',
        bp='120/80',
        temp='98.6'
    )
    
    assert booking.pname == 'John Doe'
    assert booking.bedtype == 'Normal'
    assert booking.is_critical() == False  # If this method exists
```

### Route Tests

Test API endpoints and route handlers:

```python
# tests/test_routes.py
import pytest
from flask import url_for

def test_index_page(client):
    """Test home page loads correctly"""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Emergency' in response.data

def test_user_signup(client):
    """Test user registration"""
    response = client.post('/usersignup', data={
        'fname': 'Test',
        'lname': 'User',
        'email': 'test@example.com',
        'phone': '1234567890',
        'password': 'testpass',
        'confirm_password': 'testpass'
    })
    
    # Should redirect to login page
    assert response.status_code == 302
    
    # Verify user was created
    with client.application.app_context():
        from main import User
        user = User.query.filter_by(email='test@example.com').first()
        assert user is not None
        assert user.fname == 'Test'

def test_user_login_valid(client):
    """Test valid user login"""
    # First create a user
    client.post('/usersignup', data={
        'fname': 'Test',
        'lname': 'User',
        'email': 'test@example.com',
        'phone': '1234567890',
        'password': 'testpass',
        'confirm_password': 'testpass'
    })
    
    # Then try to login
    response = client.post('/userlogin', data={
        'email': 'test@example.com',
        'password': 'testpass'
    })
    
    assert response.status_code == 302  # Redirect after login

def test_user_login_invalid(client):
    """Test invalid user login"""
    response = client.post('/userlogin', data={
        'email': 'nonexistent@example.com',
        'password': 'wrongpass'
    })
    
    assert response.status_code == 200  # Stay on login page
    assert b'Invalid' in response.data

def test_hospital_login(client):
    """Test hospital staff login"""
    # Create hospital user first
    response = client.post('/hospitallogin', data={
        'email': 'hospital@example.com',
        'password': 'hospitalpass'
    })
    
    # Should handle appropriately
    assert response.status_code in [200, 302]

def test_booking_creation(client, auth):
    """Test bed booking creation"""
    # Login first
    auth.login()
    
    response = client.post('/booking', data={
        'srfid': 'SRF001',
        'pname': 'John Doe',
        'pphone': '1111111111',
        'paddress': '123 Test St',
        'hcode': 'TH001',
        'bedtype': 'Normal',
        'spo2': '95',
        'pulserate': '80',
        'respirationrate': '18',
        'bp': '120/80',
        'temp': '98.6'
    })
    
    assert response.status_code in [200, 302]

def test_unauthorized_access(client):
    """Test that protected routes require authentication"""
    response = client.get('/admin')
    assert response.status_code == 302  # Redirect to login

def test_hospital_data_view(client):
    """Test hospital data viewing"""
    response = client.get('/hospitaldata')
    assert response.status_code == 200
    assert b'Hospital' in response.data
```

### Utility Function Tests

```python
# tests/test_utils.py
import pytest
from main import allowed_file, validate_email  # If these functions exist

def test_allowed_file_valid():
    """Test file extension validation"""
    assert allowed_file('document.pdf') == True
    assert allowed_file('image.jpg') == True
    assert allowed_file('image.jpeg') == True
    assert allowed_file('image.png') == True

def test_allowed_file_invalid():
    """Test invalid file extensions"""
    assert allowed_file('script.exe') == False
    assert allowed_file('document.txt') == False
    assert allowed_file('file_without_extension') == False

def test_email_validation():
    """Test email validation function"""
    assert validate_email('valid@example.com') == True
    assert validate_email('user.name@domain.co.uk') == True
    assert validate_email('invalid.email') == False
    assert validate_email('@domain.com') == False
    assert validate_email('user@') == False
```

## Integration Testing

### Database Integration Tests

```python
# tests/test_integration.py
import pytest
from main import app, db, User, Hospitaldata, Bookingpatient

def test_user_hospital_booking_flow(client):
    """Test complete user registration to booking flow"""
    
    # 1. Create hospital
    with client.application.app_context():
        hospital = Hospitaldata(
            hname='Test Hospital',
            hcode='TH001',
            hcity='Test City',
            hphone='9876543210',
            normalbed=100,
            hicubed=50,
            ventilatorbed=25,
            oxygenbed=75
        )
        db.session.add(hospital)
        db.session.commit()
    
    # 2. Register user
    response = client.post('/usersignup', data={
        'fname': 'Test',
        'lname': 'User',
        'email': 'test@example.com',
        'phone': '1234567890',
        'password': 'testpass',
        'confirm_password': 'testpass'
    })
    assert response.status_code == 302
    
    # 3. Login user
    response = client.post('/userlogin', data={
        'email': 'test@example.com',
        'password': 'testpass'
    })
    assert response.status_code == 302
    
    # 4. Make booking
    response = client.post('/booking', data={
        'srfid': 'SRF001',
        'pname': 'John Doe',
        'pphone': '1111111111',
        'paddress': '123 Test St',
        'hcode': 'TH001',
        'bedtype': 'Normal',
        'spo2': '95',
        'pulserate': '80',
        'respirationrate': '18',
        'bp': '120/80',
        'temp': '98.6'
    })
    
    # 5. Verify booking was created
    with client.application.app_context():
        booking = Bookingpatient.query.filter_by(srfid='SRF001').first()
        assert booking is not None
        assert booking.pname == 'John Doe'
        assert booking.hcode == 'TH001'

def test_hospital_bed_management(client):
    """Test hospital bed management functionality"""
    
    # Create hospital with beds
    with client.application.app_context():
        hospital = Hospitaldata(
            hname='Test Hospital',
            hcode='TH001',
            hcity='Test City',
            hphone='9876543210',
            normalbed=10,
            hicubed=5,
            ventilatorbed=2,
            oxygenbed=8
        )
        db.session.add(hospital)
        db.session.commit()
        
        initial_normal_beds = hospital.normalbed
    
    # Make a booking
    with client.application.app_context():
        booking = Bookingpatient(
            srfid='SRF002',
            pname='Jane Doe',
            pphone='2222222222',
            paddress='456 Test Ave',
            hcode='TH001',
            bedtype='Normal',
            spo2='96',
            pulserate='75',
            respirationrate='16',
            bp='110/70',
            temp='98.4'
        )
        db.session.add(booking)
        db.session.commit()
    
    # Verify bed count updated (if implemented)
    with client.application.app_context():
        hospital = Hospitaldata.query.filter_by(hcode='TH001').first()
        # Assuming bed count decreases after booking
        # assert hospital.normalbed == initial_normal_beds - 1
```

## End-to-End Testing

### Selenium Web Driver Tests

```python
# tests/test_e2e.py
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

@pytest.fixture
def driver():
    """Setup Chrome WebDriver"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in background
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(options=chrome_options)
    yield driver
    driver.quit()

def test_user_registration_flow(driver):
    """Test complete user registration flow"""
    driver.get("http://localhost:5000")
    
    # Navigate to signup
    signup_link = driver.find_element(By.LINK_TEXT, "Sign Up")
    signup_link.click()
    
    # Fill registration form
    driver.find_element(By.NAME, "fname").send_keys("Test")
    driver.find_element(By.NAME, "lname").send_keys("User")
    driver.find_element(By.NAME, "email").send_keys("test@example.com")
    driver.find_element(By.NAME, "phone").send_keys("1234567890")
    driver.find_element(By.NAME, "password").send_keys("testpass")
    driver.find_element(By.NAME, "confirm_password").send_keys("testpass")
    
    # Submit form
    submit_button = driver.find_element(By.XPATH, "//input[@type='submit']")
    submit_button.click()
    
    # Wait for redirect
    WebDriverWait(driver, 10).until(
        EC.url_contains("/userlogin")
    )
    
    assert "login" in driver.current_url

def test_hospital_data_viewing(driver):
    """Test viewing hospital data"""
    driver.get("http://localhost:5000/hospitaldata")
    
    # Wait for page to load
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "table"))
    )
    
    # Check if table is present
    table = driver.find_element(By.TAG_NAME, "table")
    assert table is not None

def test_booking_form_validation(driver):
    """Test booking form validation"""
    driver.get("http://localhost:5000/booking")
    
    # Try to submit empty form
    submit_button = driver.find_element(By.XPATH, "//input[@type='submit']")
    submit_button.click()
    
    # Check for validation messages
    # This depends on your validation implementation
    assert "required" in driver.page_source.lower() or "error" in driver.page_source.lower()

def test_responsive_design(driver):
    """Test responsive design on different screen sizes"""
    
    # Test mobile view
    driver.set_window_size(375, 667)  # iPhone 6/7/8 size
    driver.get("http://localhost:5000")
    
    # Check if mobile navigation is working
    # This test depends on your responsive implementation
    
    # Test tablet view
    driver.set_window_size(768, 1024)  # iPad size
    driver.get("http://localhost:5000")
    
    # Test desktop view
    driver.set_window_size(1920, 1080)  # Desktop size
    driver.get("http://localhost:5000")
```

## Performance Testing

### Load Testing with Locust

```python
# tests/test_performance.py
from locust import HttpUser, task, between

class WebsiteUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        """Login user at start"""
        self.client.post("/userlogin", data={
            "email": "test@example.com",
            "password": "testpass"
        })
    
    @task(3)
    def view_homepage(self):
        """Most common task - view homepage"""
        self.client.get("/")
    
    @task(2)
    def view_hospital_data(self):
        """View hospital data"""
        self.client.get("/hospitaldata")
    
    @task(1)
    def make_booking(self):
        """Make a booking - less frequent but important"""
        self.client.post("/booking", data={
            "srfid": f"SRF{self.environment.runner.user_count}",
            "pname": "Test Patient",
            "pphone": "1234567890",
            "paddress": "Test Address",
            "hcode": "TH001",
            "bedtype": "Normal",
            "spo2": "95",
            "pulserate": "80",
            "respirationrate": "18",
            "bp": "120/80",
            "temp": "98.6"
        })

# Run with: locust -f tests/test_performance.py --host=http://localhost:5000
```

## Security Testing

### Vulnerability Scanning

```python
# tests/test_security.py
import pytest
import requests
from main import app

def test_sql_injection_protection():
    """Test SQL injection protection"""
    with app.test_client() as client:
        # Try SQL injection in login form
        response = client.post('/userlogin', data={
            'email': "admin'; DROP TABLE users; --",
            'password': "password"
        })
        
        # Should not cause error or succeed
        assert response.status_code in [200, 302]
        
        # Database should still be intact
        with app.app_context():
            from main import User
            users = User.query.all()
            # Should not crash

def test_xss_protection():
    """Test XSS protection"""
    with app.test_client() as client:
        # Try XSS in form fields
        response = client.post('/usersignup', data={
            'fname': '<script>alert("xss")</script>',
            'lname': 'User',
            'email': 'test@example.com',
            'phone': '1234567890',
            'password': 'testpass',
            'confirm_password': 'testpass'
        })
        
        # Check that script is not executed in response
        assert b'<script>' not in response.data

def test_password_hashing():
    """Test that passwords are properly hashed"""
    with app.app_context():
        from main import User, db
        
        user = User(
            fname='Test',
            lname='User',
            email='test@example.com',
            phone='1234567890'
        )
        user.set_password('plaintext_password')
        db.session.add(user)
        db.session.commit()
        
        # Password should not be stored in plain text
        assert user.password_hash != 'plaintext_password'
        assert len(user.password_hash) > 20  # Hashed passwords are longer

def test_unauthorized_access():
    """Test unauthorized access to protected routes"""
    with app.test_client() as client:
        # Try to access admin without login
        response = client.get('/admin')
        assert response.status_code == 302  # Redirect to login
        
        # Try to access booking without login
        response = client.get('/booking')
        assert response.status_code == 302  # Redirect to login

# Security scanning with bandit
def test_bandit_security_scan():
    """Run bandit security scan"""
    import subprocess
    result = subprocess.run(['bandit', '-r', 'main.py'], 
                          capture_output=True, text=True)
    
    # Check for high severity issues
    assert 'SEVERITY: HIGH' not in result.stdout

# Dependency vulnerability check with safety
def test_safety_check():
    """Check for vulnerable dependencies"""
    import subprocess
    result = subprocess.run(['safety', 'check'], 
                          capture_output=True, text=True)
    
    # Should not find vulnerabilities
    assert result.returncode == 0
```

## API Testing

### REST API Tests

```python
# tests/test_api.py
import pytest
import json

def test_hospital_data_api(client):
    """Test hospital data API endpoint"""
    response = client.get('/api/hospitals')  # If this endpoint exists
    
    if response.status_code == 200:
        data = json.loads(response.data)
        assert isinstance(data, list)
        
        if data:  # If hospitals exist
            hospital = data[0]
            assert 'hname' in hospital
            assert 'hcode' in hospital

def test_bed_availability_api(client):
    """Test bed availability API"""
    response = client.get('/api/beds/TH001')  # If this endpoint exists
    
    if response.status_code == 200:
        data = json.loads(response.data)
        assert 'normalbed' in data
        assert 'hicubed' in data
        assert 'ventilatorbed' in data
        assert 'oxygenbed' in data

def test_booking_api(client, auth):
    """Test booking API endpoint"""
    auth.login()
    
    booking_data = {
        'srfid': 'SRF001',
        'pname': 'John Doe',
        'pphone': '1111111111',
        'paddress': '123 Test St',
        'hcode': 'TH001',
        'bedtype': 'Normal',
        'spo2': '95',
        'pulserate': '80',
        'respirationrate': '18',
        'bp': '120/80',
        'temp': '98.6'
    }
    
    response = client.post('/api/booking', 
                          data=json.dumps(booking_data),
                          content_type='application/json')
    
    # Check response based on implementation
    assert response.status_code in [200, 201, 302]
```

## Test Data Management

### Test Fixtures

```python
# tests/fixtures.py
import pytest
from main import db, User, Hospitaluser, Hospitaldata, Bookingpatient

@pytest.fixture
def sample_user():
    """Create a sample user for testing"""
    user = User(
        fname='Test',
        lname='User',
        email='test@example.com',
        phone='1234567890'
    )
    user.set_password('testpass')
    return user

@pytest.fixture
def sample_hospital():
    """Create a sample hospital for testing"""
    return Hospitaldata(
        hname='Test Hospital',
        hcode='TH001',
        hcity='Test City',
        hphone='9876543210',
        normalbed=100,
        hicubed=50,
        ventilatorbed=25,
        oxygenbed=75
    )

@pytest.fixture
def sample_booking():
    """Create a sample booking for testing"""
    return Bookingpatient(
        srfid='SRF001',
        pname='John Doe',
        pphone='1111111111',
        paddress='123 Test St',
        hcode='TH001',
        bedtype='Normal',
        spo2='95',
        pulserate='80',
        respirationrate='18',
        bp='120/80',
        temp='98.6'
    )

@pytest.fixture
def db_with_data(client):
    """Create database with sample data"""
    with client.application.app_context():
        # Add sample hospital
        hospital = Hospitaldata(
            hname='Test Hospital',
            hcode='TH001',
            hcity='Test City',
            hphone='9876543210',
            normalbed=100,
            hicubed=50,
            ventilatorbed=25,
            oxygenbed=75
        )
        db.session.add(hospital)
        
        # Add sample user
        user = User(
            fname='Test',
            lname='User',
            email='test@example.com',
            phone='1234567890'
        )
        user.set_password('testpass')
        db.session.add(user)
        
        db.session.commit()
```

## Running Tests

### Test Execution Commands

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=main --cov-report=html

# Run specific test file
pytest tests/test_models.py

# Run specific test function
pytest tests/test_models.py::test_user_password_hashing

# Run tests with verbose output
pytest -v

# Run tests and stop on first failure
pytest -x

# Run tests in parallel (requires pytest-xdist)
pytest -n auto

# Run only failed tests from last run
pytest --lf

# Run security tests
bandit -r main.py
safety check
```

### Continuous Integration

Create `.github/workflows/tests.yml`:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      mysql:
        image: mysql:8.0
        env:
          MYSQL_ROOT_PASSWORD: rootpass
          MYSQL_DATABASE: test_emergency_bed
        options: >-
          --health-cmd="mysqladmin ping"
          --health-interval=10s
          --health-timeout=5s
          --health-retries=3
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.8
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov selenium bandit safety
    
    - name: Run security checks
      run: |
        bandit -r main.py
        safety check
    
    - name: Run tests
      run: |
        pytest --cov=main --cov-report=xml
      env:
        DATABASE_URL: mysql://root:rootpass@localhost/test_emergency_bed
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v1
```

## Test Reports and Metrics

### Coverage Reports

```bash
# Generate HTML coverage report
pytest --cov=main --cov-report=html

# Generate XML coverage report (for CI)
pytest --cov=main --cov-report=xml

# Show coverage in terminal
pytest --cov=main --cov-report=term-missing
```

### Performance Metrics

Monitor and track:

- Response times for critical endpoints
- Database query performance
- Memory usage during tests
- Test execution time

### Quality Gates

Set minimum thresholds:

- Code coverage: 80%
- Security scan: No high severity issues
- Performance: Response time < 200ms for critical paths
- All tests must pass

## Troubleshooting Test Issues

### Common Issues

1. **Database Connection Errors**
   - Ensure test database is running
   - Check connection string
   - Verify database permissions

2. **Authentication Test Failures**
   - Check session configuration
   - Verify CSRF token handling
   - Ensure proper test isolation

3. **Selenium Test Issues**
   - Update ChromeDriver version
   - Check element selectors
   - Add proper waits

4. **Performance Test Variations**
   - Run tests multiple times
   - Account for system load
   - Use consistent test environment

### Debugging Tips

```python
# Add debug output in tests
import logging
logging.basicConfig(level=logging.DEBUG)

# Use pytest fixtures for debugging
@pytest.fixture
def debug_client(client):
    client.testing = True
    return client

# Capture and inspect database state
def test_with_db_inspection(client):
    with client.application.app_context():
        # Inspect database state
        from main import User
        users = User.query.all()
        print(f"Users in database: {len(users)}")
        for user in users:
            print(f"User: {user.email}")
```

Remember: Good tests are the foundation of reliable software. Write tests early, run them often, and maintain them as your codebase evolves.
