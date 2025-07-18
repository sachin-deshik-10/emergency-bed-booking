"""
Comprehensive Input Validation Service
Provides secure validation for all user inputs with sanitization
"""

import re
import html
import bleach
from typing import Optional, Dict, List, Any
from datetime import datetime
from email_validator import validate_email, EmailNotValidError

class ValidationError(Exception):
    """Custom validation error"""
    pass

class InputValidator:
    """Comprehensive input validation and sanitization service"""
    
    # Regex patterns for common validations
    PATTERNS = {
        'phone': re.compile(r'^[\+]?[1-9][\d]{0,15}$'),
        'hospital_code': re.compile(r'^[A-Z0-9]{3,10}$'),
        'name': re.compile(r'^[a-zA-Z\s\-\.]{2,50}$'),
        'password': re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'),
        'alpha_numeric': re.compile(r'^[a-zA-Z0-9]+$'),
        'safe_string': re.compile(r'^[a-zA-Z0-9\s\-_\.@]{1,100}$')
    }
    
    # Allowed HTML tags for rich text (if needed)
    ALLOWED_TAGS = ['b', 'i', 'u', 'em', 'strong', 'p', 'br']
    
    @classmethod
    def sanitize_html(cls, text: str) -> str:
        """Sanitize HTML content to prevent XSS"""
        if not text:
            return ""
        
        # Remove harmful HTML tags and attributes
        cleaned = bleach.clean(text, tags=cls.ALLOWED_TAGS, strip=True)
        return html.escape(cleaned)
    
    @classmethod
    def sanitize_input(cls, text: str) -> str:
        """Basic input sanitization"""
        if not text:
            return ""
        
        # Strip whitespace and escape HTML
        cleaned = text.strip()
        cleaned = html.escape(cleaned)
        return cleaned
    
    @classmethod
    def validate_email(cls, email: str) -> bool:
        """Validate email address format"""
        try:
            if not email or len(email) > 254:
                return False
            
            # Use email-validator library for comprehensive validation
            validate_email(email)
            return True
        except EmailNotValidError:
            return False
    
    @classmethod
    def validate_password(cls, password: str) -> Dict[str, Any]:
        """
        Validate password strength
        Returns dict with validation results and suggestions
        """
        if not password:
            return {
                'valid': False,
                'errors': ['Password is required'],
                'score': 0
            }
        
        errors = []
        score = 0
        
        # Length check
        if len(password) < 8:
            errors.append('Password must be at least 8 characters long')
        else:
            score += 1
        
        # Complexity checks
        if not re.search(r'[a-z]', password):
            errors.append('Password must contain lowercase letters')
        else:
            score += 1
            
        if not re.search(r'[A-Z]', password):
            errors.append('Password must contain uppercase letters')
        else:
            score += 1
            
        if not re.search(r'\d', password):
            errors.append('Password must contain numbers')
        else:
            score += 1
            
        if not re.search(r'[@$!%*?&]', password):
            errors.append('Password must contain special characters (@$!%*?&)')
        else:
            score += 1
        
        # Check for common weak passwords
        weak_patterns = ['password', '12345', 'qwerty', 'admin']
        if any(weak in password.lower() for weak in weak_patterns):
            errors.append('Password contains common weak patterns')
            score = max(0, score - 2)
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'score': score,
            'strength': cls._get_password_strength(score)
        }
    
    @classmethod
    def _get_password_strength(cls, score: int) -> str:
        """Get password strength description"""
        if score <= 2:
            return 'Weak'
        elif score <= 3:
            return 'Medium'
        elif score <= 4:
            return 'Strong'
        else:
            return 'Very Strong'
    
    @classmethod
    def validate_phone(cls, phone: str) -> bool:
        """Validate phone number format"""
        if not phone:
            return False
        
        # Remove spaces, dashes, and parentheses
        cleaned_phone = re.sub(r'[\s\-\(\)]', '', phone)
        
        return bool(cls.PATTERNS['phone'].match(cleaned_phone))
    
    @classmethod
    def validate_hospital_code(cls, code: str) -> bool:
        """Validate hospital code format"""
        if not code:
            return False
        
        return bool(cls.PATTERNS['hospital_code'].match(code.upper()))
    
    @classmethod
    def validate_name(cls, name: str) -> bool:
        """Validate name format"""
        if not name or len(name) < 2 or len(name) > 50:
            return False
        
        return bool(cls.PATTERNS['name'].match(name))
    
    @classmethod
    def validate_spo2(cls, spo2: Any) -> bool:
        """Validate SpO2 (oxygen saturation) value"""
        try:
            value = int(spo2)
            return 70 <= value <= 100  # Valid SpO2 range
        except (ValueError, TypeError):
            return False
    
    @classmethod
    def validate_bed_count(cls, count: Any) -> bool:
        """Validate bed count value"""
        try:
            value = int(count)
            return 0 <= value <= 10000  # Reasonable bed count range
        except (ValueError, TypeError):
            return False
    
    @classmethod
    def validate_required_fields(cls, data: Dict[str, Any], required_fields: List[str]) -> List[str]:
        """Validate that all required fields are present and not empty"""
        missing_fields = []
        
        for field in required_fields:
            value = data.get(field)
            if not value or (isinstance(value, str) and not value.strip()):
                missing_fields.append(field)
        
        return missing_fields
    
    @classmethod
    def validate_user_registration(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive validation for user registration"""
        errors = {}
        
        # Email validation
        email = data.get('email', '').strip()
        if not email:
            errors['email'] = 'Email is required'
        elif not cls.validate_email(email):
            errors['email'] = 'Invalid email format'
        
        # Password validation
        password = data.get('password', '')
        password_result = cls.validate_password(password)
        if not password_result['valid']:
            errors['password'] = password_result['errors']
        
        # Date of birth validation
        dob = data.get('dob', '').strip()
        if not dob:
            errors['dob'] = 'Date of birth is required'
        else:
            try:
                dob_date = datetime.strptime(dob, '%Y-%m-%d')
                if dob_date > datetime.now():
                    errors['dob'] = 'Date of birth cannot be in the future'
                elif datetime.now().year - dob_date.year > 150:
                    errors['dob'] = 'Invalid date of birth'
            except ValueError:
                errors['dob'] = 'Invalid date format. Use YYYY-MM-DD'
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'sanitized_data': {
                'email': cls.sanitize_input(email),
                'dob': cls.sanitize_input(dob)
            }
        }
    
    @classmethod
    def validate_hospital_registration(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive validation for hospital registration"""
        errors = {}
        
        # Hospital code validation
        hcode = data.get('hcode', '').strip().upper()
        if not hcode:
            errors['hcode'] = 'Hospital code is required'
        elif not cls.validate_hospital_code(hcode):
            errors['hcode'] = 'Invalid hospital code format (3-10 alphanumeric characters)'
        
        # Email validation
        email = data.get('email', '').strip()
        if not email:
            errors['email'] = 'Email is required'
        elif not cls.validate_email(email):
            errors['email'] = 'Invalid email format'
        
        # Password validation
        password = data.get('password', '')
        password_result = cls.validate_password(password)
        if not password_result['valid']:
            errors['password'] = password_result['errors']
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'sanitized_data': {
                'hcode': hcode,
                'email': cls.sanitize_input(email)
            }
        }
    
    @classmethod
    def validate_bed_booking(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive validation for bed booking"""
        errors = {}
        
        # Required fields
        required_fields = ['bedtype', 'hcode', 'pname', 'pphone', 'paddress', 'email']
        missing_fields = cls.validate_required_fields(data, required_fields)
        
        if missing_fields:
            errors['required'] = f"Missing required fields: {', '.join(missing_fields)}"
        
        # Specific field validations
        if data.get('pname') and not cls.validate_name(data['pname']):
            errors['pname'] = 'Invalid name format'
        
        if data.get('pphone') and not cls.validate_phone(data['pphone']):
            errors['pphone'] = 'Invalid phone number format'
        
        if data.get('email') and not cls.validate_email(data['email']):
            errors['email'] = 'Invalid email format'
        
        if data.get('hcode') and not cls.validate_hospital_code(data['hcode']):
            errors['hcode'] = 'Invalid hospital code'
        
        if data.get('spo2') and not cls.validate_spo2(data['spo2']):
            errors['spo2'] = 'Invalid SpO2 value (must be between 70-100)'
        
        # Bed type validation
        valid_bed_types = ['Normal', 'HICU', 'ICU', 'Ventilator']
        if data.get('bedtype') and data['bedtype'] not in valid_bed_types:
            errors['bedtype'] = f'Invalid bed type. Must be one of: {", ".join(valid_bed_types)}'
        
        # Sanitize data
        sanitized_data = {}
        for key, value in data.items():
            if isinstance(value, str):
                sanitized_data[key] = cls.sanitize_input(value)
            else:
                sanitized_data[key] = value
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'sanitized_data': sanitized_data
        }
    
    @classmethod
    def validate_hospital_data(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive validation for hospital data updates"""
        errors = {}
        
        # Hospital code validation
        if data.get('hcode') and not cls.validate_hospital_code(data['hcode']):
            errors['hcode'] = 'Invalid hospital code format'
        
        # Hospital name validation
        if data.get('hname'):
            hname = data['hname'].strip()
            if len(hname) < 3 or len(hname) > 100:
                errors['hname'] = 'Hospital name must be between 3-100 characters'
        
        # Bed count validations
        bed_fields = ['normalbed', 'hicubed', 'icubed', 'vbed']
        for field in bed_fields:
            if field in data and not cls.validate_bed_count(data[field]):
                errors[field] = f'Invalid {field} count (must be 0-10000)'
        
        # Sanitize data
        sanitized_data = {}
        for key, value in data.items():
            if isinstance(value, str):
                sanitized_data[key] = cls.sanitize_input(value)
            else:
                sanitized_data[key] = value
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'sanitized_data': sanitized_data
        }

# Create singleton instance
validator = InputValidator()
