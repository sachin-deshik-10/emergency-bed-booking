"""
Secure Form Models with CSRF Protection and Advanced Validation
Enhanced forms for all user interactions with comprehensive security
"""

from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, SelectField, IntegerField, 
    TextAreaField, HiddenField, BooleanField, DateField, EmailField
)
from wtforms.validators import (
    DataRequired, Email, Length, NumberRange, Optional, 
    ValidationError, Regexp, EqualTo
)
from wtforms.widgets import TextArea
from datetime import datetime, date
import re

class SecureBaseForm(FlaskForm):
    """Base form with enhanced security features"""
    
    # Hidden field for additional CSRF protection
    form_token = HiddenField()
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Generate form-specific token
        if not self.form_token.data:
            import secrets
            self.form_token.data = secrets.token_urlsafe(16)

class PasswordStrengthValidator:
    """Custom validator for password strength"""
    
    def __init__(self, min_length=8, require_uppercase=True, require_lowercase=True,
                 require_numbers=True, require_special=True):
        self.min_length = min_length
        self.require_uppercase = require_uppercase
        self.require_lowercase = require_lowercase
        self.require_numbers = require_numbers
        self.require_special = require_special
    
    def __call__(self, form, field):
        password = field.data
        errors = []
        
        if len(password) < self.min_length:
            errors.append(f'Password must be at least {self.min_length} characters long')
        
        if self.require_uppercase and not re.search(r'[A-Z]', password):
            errors.append('Password must contain uppercase letters')
        
        if self.require_lowercase and not re.search(r'[a-z]', password):
            errors.append('Password must contain lowercase letters')
        
        if self.require_numbers and not re.search(r'\d', password):
            errors.append('Password must contain numbers')
        
        if self.require_special and not re.search(r'[@$!%*?&]', password):
            errors.append('Password must contain special characters (@$!%*?&)')
        
        # Check for common weak patterns
        weak_patterns = ['password', '12345', 'qwerty', 'admin']
        if any(weak in password.lower() for weak in weak_patterns):
            errors.append('Password contains common weak patterns')
        
        if errors:
            raise ValidationError(' | '.join(errors))

class HospitalCodeValidator:
    """Custom validator for hospital codes"""
    
    def __call__(self, form, field):
        code = field.data.upper() if field.data else ''
        
        if not re.match(r'^[A-Z0-9]{3,10}$', code):
            raise ValidationError('Hospital code must be 3-10 alphanumeric characters')

class PhoneValidator:
    """Custom validator for phone numbers"""
    
    def __call__(self, form, field):
        phone = re.sub(r'[\s\-\(\)]', '', field.data) if field.data else ''
        
        if not re.match(r'^[\+]?[1-9][\d]{0,15}$', phone):
            raise ValidationError('Invalid phone number format')

class SpO2Validator:
    """Custom validator for SpO2 values"""
    
    def __call__(self, form, field):
        try:
            value = int(field.data)
            if not 70 <= value <= 100:
                raise ValidationError('SpO2 must be between 70-100%')
        except (ValueError, TypeError):
            raise ValidationError('SpO2 must be a valid number')

# User Authentication Forms

class UserRegistrationForm(SecureBaseForm):
    """Enhanced user registration form"""
    
    email = EmailField('Email Address', validators=[
        DataRequired(message='Email is required'),
        Email(message='Invalid email format'),
        Length(max=254, message='Email too long')
    ])
    
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required'),
        PasswordStrengthValidator()
    ])
    
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(message='Please confirm your password'),
        EqualTo('password', message='Passwords must match')
    ])
    
    dob = DateField('Date of Birth', validators=[
        DataRequired(message='Date of birth is required')
    ])
    
    terms_accepted = BooleanField('I accept the Terms of Service and Privacy Policy', validators=[
        DataRequired(message='You must accept the terms and conditions')
    ])
    
    def validate_dob(self, field):
        """Custom validation for date of birth"""
        if field.data > date.today():
            raise ValidationError('Date of birth cannot be in the future')
        
        # Check minimum age (optional)
        age = (date.today() - field.data).days / 365.25
        if age > 150:
            raise ValidationError('Invalid date of birth')

class UserLoginForm(SecureBaseForm):
    """Enhanced user login form"""
    
    email = EmailField('Email Address', validators=[
        DataRequired(message='Email is required'),
        Email(message='Invalid email format')
    ])
    
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required')
    ])
    
    remember_me = BooleanField('Remember Me')
    
    # MFA token field (optional)
    mfa_token = StringField('Authentication Code', validators=[
        Optional(),
        Length(min=6, max=6, message='Authentication code must be 6 digits'),
        Regexp(r'^\d{6}$', message='Authentication code must contain only digits')
    ])

class HospitalRegistrationForm(SecureBaseForm):
    """Enhanced hospital registration form"""
    
    hcode = StringField('Hospital Code', validators=[
        DataRequired(message='Hospital code is required'),
        Length(min=3, max=10, message='Hospital code must be 3-10 characters'),
        HospitalCodeValidator()
    ])
    
    hname = StringField('Hospital Name', validators=[
        DataRequired(message='Hospital name is required'),
        Length(min=3, max=100, message='Hospital name must be 3-100 characters'),
        Regexp(r'^[a-zA-Z0-9\s\-\.&]+$', message='Invalid characters in hospital name')
    ])
    
    email = EmailField('Email Address', validators=[
        DataRequired(message='Email is required'),
        Email(message='Invalid email format'),
        Length(max=254, message='Email too long')
    ])
    
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required'),
        PasswordStrengthValidator()
    ])
    
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(message='Please confirm your password'),
        EqualTo('password', message='Passwords must match')
    ])
    
    phone = StringField('Contact Phone', validators=[
        DataRequired(message='Phone number is required'),
        PhoneValidator()
    ])
    
    address = TextAreaField('Hospital Address', validators=[
        DataRequired(message='Address is required'),
        Length(min=10, max=500, message='Address must be 10-500 characters')
    ])
    
    license_number = StringField('Medical License Number', validators=[
        DataRequired(message='License number is required'),
        Length(min=5, max=50, message='License number must be 5-50 characters')
    ])

class HospitalLoginForm(SecureBaseForm):
    """Enhanced hospital login form"""
    
    hcode = StringField('Hospital Code', validators=[
        DataRequired(message='Hospital code is required'),
        HospitalCodeValidator()
    ])
    
    email = EmailField('Email Address', validators=[
        DataRequired(message='Email is required'),
        Email(message='Invalid email format')
    ])
    
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required')
    ])
    
    mfa_token = StringField('Authentication Code', validators=[
        Optional(),
        Length(min=6, max=6, message='Authentication code must be 6 digits'),
        Regexp(r'^\d{6}$', message='Authentication code must contain only digits')
    ])

# Bed Booking Forms

class BedBookingForm(SecureBaseForm):
    """Enhanced bed booking form"""
    
    bedtype = SelectField('Bed Type', choices=[
        ('Normal', 'Normal Bed'),
        ('HICU', 'High Dependency Unit (HICU)'),
        ('ICU', 'Intensive Care Unit (ICU)'),
        ('Ventilator', 'Ventilator Bed')
    ], validators=[
        DataRequired(message='Please select a bed type')
    ])
    
    hcode = SelectField('Hospital', validators=[
        DataRequired(message='Please select a hospital')
    ])
    
    pname = StringField('Patient Name', validators=[
        DataRequired(message='Patient name is required'),
        Length(min=2, max=100, message='Name must be 2-100 characters'),
        Regexp(r'^[a-zA-Z\s\-\.]+$', message='Name can only contain letters, spaces, hyphens, and dots')
    ])
    
    pphone = StringField('Patient Phone', validators=[
        DataRequired(message='Phone number is required'),
        PhoneValidator()
    ])
    
    paddress = TextAreaField('Patient Address', validators=[
        DataRequired(message='Address is required'),
        Length(min=10, max=500, message='Address must be 10-500 characters')
    ])
    
    email = EmailField('Contact Email', validators=[
        DataRequired(message='Email is required'),
        Email(message='Invalid email format')
    ])
    
    spo2 = IntegerField('SpO2 Level (%)', validators=[
        DataRequired(message='SpO2 level is required'),
        SpO2Validator()
    ])
    
    emergency_contact = StringField('Emergency Contact', validators=[
        Optional(),
        PhoneValidator()
    ])
    
    medical_conditions = TextAreaField('Medical Conditions/Symptoms', validators=[
        Optional(),
        Length(max=1000, message='Medical conditions description too long')
    ])
    
    insurance_number = StringField('Insurance Number', validators=[
        Optional(),
        Length(max=50, message='Insurance number too long')
    ])

# Hospital Management Forms

class HospitalDataForm(SecureBaseForm):
    """Enhanced hospital data management form"""
    
    hcode = StringField('Hospital Code', validators=[
        DataRequired(message='Hospital code is required'),
        HospitalCodeValidator()
    ])
    
    hname = StringField('Hospital Name', validators=[
        DataRequired(message='Hospital name is required'),
        Length(min=3, max=100, message='Hospital name must be 3-100 characters')
    ])
    
    normalbed = IntegerField('Normal Beds', validators=[
        DataRequired(message='Normal bed count is required'),
        NumberRange(min=0, max=10000, message='Bed count must be 0-10000')
    ])
    
    hicubed = IntegerField('HICU Beds', validators=[
        DataRequired(message='HICU bed count is required'),
        NumberRange(min=0, max=10000, message='Bed count must be 0-10000')
    ])
    
    icubed = IntegerField('ICU Beds', validators=[
        DataRequired(message='ICU bed count is required'),
        NumberRange(min=0, max=10000, message='Bed count must be 0-10000')
    ])
    
    vbed = IntegerField('Ventilator Beds', validators=[
        DataRequired(message='Ventilator bed count is required'),
        NumberRange(min=0, max=10000, message='Bed count must be 0-10000')
    ])
    
    phone = StringField('Hospital Phone', validators=[
        Optional(),
        PhoneValidator()
    ])
    
    address = TextAreaField('Hospital Address', validators=[
        Optional(),
        Length(max=500, message='Address too long')
    ])
    
    specialties = TextAreaField('Medical Specialties', validators=[
        Optional(),
        Length(max=1000, message='Specialties description too long')
    ])

class QuickBedUpdateForm(SecureBaseForm):
    """Quick bed count update form for real-time updates"""
    
    bed_type = SelectField('Bed Type', choices=[
        ('normal', 'Normal'),
        ('hicu', 'HICU'),
        ('icu', 'ICU'),
        ('ventilator', 'Ventilator')
    ], validators=[
        DataRequired(message='Please select bed type')
    ])
    
    action = SelectField('Action', choices=[
        ('increase', 'Increase'),
        ('decrease', 'Decrease'),
        ('set', 'Set to')
    ], validators=[
        DataRequired(message='Please select action')
    ])
    
    count = IntegerField('Count', validators=[
        DataRequired(message='Count is required'),
        NumberRange(min=0, max=100, message='Count must be 0-100')
    ])
    
    reason = StringField('Reason (Optional)', validators=[
        Optional(),
        Length(max=200, message='Reason too long')
    ])

# Security Forms

class PasswordResetRequestForm(SecureBaseForm):
    """Password reset request form"""
    
    email = EmailField('Email Address', validators=[
        DataRequired(message='Email is required'),
        Email(message='Invalid email format')
    ])

class PasswordResetForm(SecureBaseForm):
    """Password reset form"""
    
    token = HiddenField('Reset Token', validators=[
        DataRequired()
    ])
    
    password = PasswordField('New Password', validators=[
        DataRequired(message='Password is required'),
        PasswordStrengthValidator()
    ])
    
    confirm_password = PasswordField('Confirm New Password', validators=[
        DataRequired(message='Please confirm your password'),
        EqualTo('password', message='Passwords must match')
    ])

class MFASetupForm(SecureBaseForm):
    """Multi-Factor Authentication setup form"""
    
    verification_token = StringField('Verification Code', validators=[
        DataRequired(message='Verification code is required'),
        Length(min=6, max=6, message='Verification code must be 6 digits'),
        Regexp(r'^\d{6}$', message='Verification code must contain only digits')
    ])

class MFAVerificationForm(SecureBaseForm):
    """MFA verification form for login"""
    
    mfa_token = StringField('Authentication Code', validators=[
        DataRequired(message='Authentication code is required'),
        Length(min=6, max=6, message='Authentication code must be 6 digits'),
        Regexp(r'^\d{6}$', message='Authentication code must contain only digits')
    ])
    
    backup_code = StringField('Or use backup code', validators=[
        Optional(),
        Length(min=9, max=9, message='Backup code format: XXXX-XXXX'),
        Regexp(r'^\d{4}-\d{4}$', message='Backup code format: XXXX-XXXX')
    ])
    
    def validate(self):
        """Custom validation to ensure either MFA token or backup code is provided"""
        if not super().validate():
            return False
        
        if not self.mfa_token.data and not self.backup_code.data:
            self.mfa_token.errors.append('Either authentication code or backup code is required')
            return False
        
        return True

class ChangePasswordForm(SecureBaseForm):
    """Change password form for authenticated users"""
    
    current_password = PasswordField('Current Password', validators=[
        DataRequired(message='Current password is required')
    ])
    
    new_password = PasswordField('New Password', validators=[
        DataRequired(message='New password is required'),
        PasswordStrengthValidator()
    ])
    
    confirm_password = PasswordField('Confirm New Password', validators=[
        DataRequired(message='Please confirm your new password'),
        EqualTo('new_password', message='Passwords must match')
    ])

# Admin Forms

class AdminLoginForm(SecureBaseForm):
    """Enhanced admin login form"""
    
    username = StringField('Username', validators=[
        DataRequired(message='Username is required'),
        Length(min=3, max=50, message='Username must be 3-50 characters')
    ])
    
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required')
    ])
    
    mfa_token = StringField('Authentication Code', validators=[
        Optional(),
        Length(min=6, max=6, message='Authentication code must be 6 digits'),
        Regexp(r'^\d{6}$', message='Authentication code must contain only digits')
    ])

# Search and Filter Forms

class HospitalSearchForm(FlaskForm):
    """Hospital search and filter form"""
    
    search_term = StringField('Search', validators=[
        Optional(),
        Length(max=100, message='Search term too long')
    ])
    
    bed_type = SelectField('Bed Type', choices=[
        ('', 'All Bed Types'),
        ('normal', 'Normal'),
        ('hicu', 'HICU'),
        ('icu', 'ICU'),
        ('ventilator', 'Ventilator')
    ], validators=[Optional()])
    
    min_beds = IntegerField('Minimum Available Beds', validators=[
        Optional(),
        NumberRange(min=0, max=1000, message='Invalid bed count')
    ])
    
    location = StringField('Location/Area', validators=[
        Optional(),
        Length(max=100, message='Location too long')
    ])

# File Upload Forms

class SecureFileUploadForm(SecureBaseForm):
    """Secure file upload form with validation"""
    
    description = StringField('File Description', validators=[
        Optional(),
        Length(max=200, message='Description too long')
    ])
    
    file_type = SelectField('File Type', choices=[
        ('medical_report', 'Medical Report'),
        ('prescription', 'Prescription'),
        ('insurance_document', 'Insurance Document'),
        ('id_proof', 'ID Proof'),
        ('other', 'Other')
    ], validators=[
        DataRequired(message='Please select file type')
    ])

# Emergency Alert Forms

class EmergencyAlertForm(SecureBaseForm):
    """Emergency alert form for hospital staff"""
    
    alert_type = SelectField('Alert Type', choices=[
        ('capacity_full', 'Hospital at Full Capacity'),
        ('emergency_situation', 'Emergency Situation'),
        ('system_maintenance', 'System Maintenance'),
        ('bed_shortage', 'Critical Bed Shortage'),
        ('other', 'Other')
    ], validators=[
        DataRequired(message='Please select alert type')
    ])
    
    message = TextAreaField('Alert Message', validators=[
        DataRequired(message='Alert message is required'),
        Length(min=10, max=500, message='Message must be 10-500 characters')
    ])
    
    priority = SelectField('Priority', choices=[
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical')
    ], validators=[
        DataRequired(message='Please select priority')
    ])
    
    duration_hours = IntegerField('Alert Duration (Hours)', validators=[
        Optional(),
        NumberRange(min=1, max=24, message='Duration must be 1-24 hours')
    ])
