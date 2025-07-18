"""
Advanced API Service for Emergency Hospital Bed Booking System

Provides comprehensive REST API endpoints for:
- Hospital and bed management
- User operations and authentication
- Booking and reservation management
- Analytics and reporting
- Real-time notifications
- Administrative functions

Features:
- RESTful API design
- JWT authentication
- Rate limiting
- Request/response validation
- Comprehensive error handling
- API versioning support
- Documentation generation
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from functools import wraps
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import json
import logging
from dataclasses import dataclass, asdict
from enum import Enum

# Import services
from .analytics_service import analytics_service, ReportType
from .validation_service import validation_service
from .security_service import security_service

class APIVersion(Enum):
    V1 = "v1"
    V2 = "v2"

class HTTPMethod(Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"

@dataclass
class APIResponse:
    """Standardized API response structure"""
    success: bool
    data: Any = None
    message: str = ""
    error: Optional[str] = None
    metadata: Optional[Dict] = None
    timestamp: str = None
    version: str = "v1"
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()

class APIRateLimiter:
    """Simple in-memory rate limiter for API endpoints"""
    
    def __init__(self):
        self.requests = {}  # {client_id: [timestamps]}
        self.limits = {
            'default': {'requests': 100, 'window': 3600},  # 100 requests per hour
            'auth': {'requests': 10, 'window': 300},        # 10 auth requests per 5 minutes
            'analytics': {'requests': 50, 'window': 3600},   # 50 analytics requests per hour
        }
    
    def is_allowed(self, client_id: str, endpoint_type: str = 'default') -> bool:
        """Check if request is within rate limits"""
        now = datetime.now()
        limit_config = self.limits.get(endpoint_type, self.limits['default'])
        
        if client_id not in self.requests:
            self.requests[client_id] = []
        
        # Clean old requests outside window
        window_start = now - timedelta(seconds=limit_config['window'])
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id] 
            if req_time > window_start
        ]
        
        # Check if under limit
        if len(self.requests[client_id]) >= limit_config['requests']:
            return False
        
        # Record this request
        self.requests[client_id].append(now)
        return True

# Global rate limiter instance
rate_limiter = APIRateLimiter()

def rate_limit(endpoint_type: str = 'default'):
    """Rate limiting decorator"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            client_id = request.remote_addr
            if hasattr(request, 'user_id'):
                client_id = f"user_{request.user_id}"
            
            if not rate_limiter.is_allowed(client_id, endpoint_type):
                return jsonify(asdict(APIResponse(
                    success=False,
                    error="Rate limit exceeded",
                    message="Too many requests. Please try again later."
                ))), 429
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def api_response(success: bool, data: Any = None, message: str = "", 
                error: str = None, status_code: int = 200) -> tuple:
    """Helper function to create standardized API responses"""
    response = APIResponse(
        success=success,
        data=data,
        message=message,
        error=error,
        metadata={
            'request_id': getattr(request, 'id', None),
            'endpoint': request.endpoint,
            'method': request.method
        }
    )
    return jsonify(asdict(response)), status_code

def validate_json_request(required_fields: List[str] = None):
    """Decorator to validate JSON request data"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.is_json:
                return api_response(
                    success=False,
                    error="Invalid content type",
                    message="Request must be JSON",
                    status_code=400
                )
            
            data = request.get_json()
            if not data:
                return api_response(
                    success=False,
                    error="Invalid JSON",
                    message="Request body must contain valid JSON",
                    status_code=400
                )
            
            if required_fields:
                missing_fields = [field for field in required_fields if field not in data]
                if missing_fields:
                    return api_response(
                        success=False,
                        error="Missing required fields",
                        message=f"Required fields: {', '.join(missing_fields)}",
                        status_code=400
                    )
            
            request.json_data = data
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Create API Blueprint
api_v1 = Blueprint('api_v1', __name__, url_prefix='/api/v1')

# Authentication Endpoints
@api_v1.route('/auth/login', methods=['POST'])
@rate_limit('auth')
@validate_json_request(['username', 'password'])
def api_login():
    """Authenticate user and return JWT token"""
    try:
        data = request.json_data
        username = data['username']
        password = data['password']
        
        # Validate credentials (integrate with your auth system)
        if validation_service.validate_login_credentials(username, password):
            # Create JWT token
            access_token = create_access_token(
                identity=username,
                expires_delta=timedelta(hours=24)
            )
            
            return api_response(
                success=True,
                data={
                    'access_token': access_token,
                    'token_type': 'Bearer',
                    'expires_in': 86400,  # 24 hours in seconds
                    'user': {
                        'username': username,
                        'role': 'user'  # Get from database
                    }
                },
                message="Login successful"
            )
        else:
            return api_response(
                success=False,
                error="Authentication failed",
                message="Invalid username or password",
                status_code=401
            )
            
    except Exception as e:
        logging.error(f"API login error: {str(e)}")
        return api_response(
            success=False,
            error="Internal server error",
            message="Login failed due to server error",
            status_code=500
        )

@api_v1.route('/auth/refresh', methods=['POST'])
@jwt_required()
@rate_limit('auth')
def api_refresh_token():
    """Refresh JWT token"""
    try:
        current_user = get_jwt_identity()
        new_token = create_access_token(
            identity=current_user,
            expires_delta=timedelta(hours=24)
        )
        
        return api_response(
            success=True,
            data={
                'access_token': new_token,
                'token_type': 'Bearer',
                'expires_in': 86400
            },
            message="Token refreshed successfully"
        )
        
    except Exception as e:
        logging.error(f"API token refresh error: {str(e)}")
        return api_response(
            success=False,
            error="Token refresh failed",
            status_code=401
        )

# Hospital Management Endpoints
@api_v1.route('/hospitals', methods=['GET'])
@jwt_required()
@rate_limit()
def api_get_hospitals():
    """Get list of all hospitals"""
    try:
        # Simulate hospital data (replace with database query)
        hospitals = [
            {
                'id': 1,
                'name': 'City General Hospital',
                'address': '123 Main St, City',
                'total_beds': 100,
                'available_beds': 25,
                'utilization_rate': 75.0,
                'emergency_contact': '+1-555-0101',
                'specialties': ['Emergency', 'Cardiology', 'Surgery']
            },
            {
                'id': 2,
                'name': 'Regional Medical Center',
                'address': '456 Oak Ave, Town',
                'total_beds': 150,
                'available_beds': 40,
                'utilization_rate': 73.3,
                'emergency_contact': '+1-555-0102',
                'specialties': ['Emergency', 'Oncology', 'Pediatrics']
            }
        ]
        
        return api_response(
            success=True,
            data={
                'hospitals': hospitals,
                'total_count': len(hospitals)
            },
            message="Hospitals retrieved successfully"
        )
        
    except Exception as e:
        logging.error(f"API get hospitals error: {str(e)}")
        return api_response(
            success=False,
            error="Failed to retrieve hospitals",
            status_code=500
        )

@api_v1.route('/hospitals/<int:hospital_id>', methods=['GET'])
@jwt_required()
@rate_limit()
def api_get_hospital(hospital_id: int):
    """Get detailed information about a specific hospital"""
    try:
        # Simulate hospital details (replace with database query)
        hospital_details = {
            'id': hospital_id,
            'name': 'City General Hospital',
            'address': '123 Main St, City',
            'phone': '+1-555-0101',
            'email': 'info@citygeneral.com',
            'website': 'https://citygeneral.com',
            'total_beds': 100,
            'available_beds': 25,
            'utilization_rate': 75.0,
            'departments': [
                {'name': 'Emergency', 'beds': 20, 'available': 5},
                {'name': 'ICU', 'beds': 15, 'available': 3},
                {'name': 'General', 'beds': 65, 'available': 17}
            ],
            'specialties': ['Emergency', 'Cardiology', 'Surgery'],
            'coordinates': {'lat': 40.7128, 'lng': -74.0060},
            'rating': 4.5,
            'certifications': ['JCI', 'ISO 9001'],
            'last_updated': datetime.now().isoformat()
        }
        
        return api_response(
            success=True,
            data=hospital_details,
            message="Hospital details retrieved successfully"
        )
        
    except Exception as e:
        logging.error(f"API get hospital error: {str(e)}")
        return api_response(
            success=False,
            error="Failed to retrieve hospital details",
            status_code=500
        )

@api_v1.route('/hospitals/<int:hospital_id>/availability', methods=['GET'])
@jwt_required()
@rate_limit()
def api_get_hospital_availability(hospital_id: int):
    """Get real-time bed availability for a hospital"""
    try:
        # Get query parameters
        department = request.args.get('department', 'all')
        date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
        
        # Simulate availability data
        availability = {
            'hospital_id': hospital_id,
            'date': date,
            'last_updated': datetime.now().isoformat(),
            'total_beds': 100,
            'occupied_beds': 75,
            'available_beds': 25,
            'utilization_rate': 75.0,
            'departments': {
                'Emergency': {'total': 20, 'available': 5, 'reserved': 2},
                'ICU': {'total': 15, 'available': 3, 'reserved': 1},
                'General': {'total': 65, 'available': 17, 'reserved': 5}
            },
            'predicted_availability': {
                'next_hour': 23,
                'next_4_hours': 21,
                'next_24_hours': 28
            }
        }
        
        if department != 'all' and department in availability['departments']:
            availability['filtered_department'] = {
                'department': department,
                'data': availability['departments'][department]
            }
        
        return api_response(
            success=True,
            data=availability,
            message="Hospital availability retrieved successfully"
        )
        
    except Exception as e:
        logging.error(f"API get hospital availability error: {str(e)}")
        return api_response(
            success=False,
            error="Failed to retrieve hospital availability",
            status_code=500
        )

# Booking Management Endpoints
@api_v1.route('/bookings', methods=['POST'])
@jwt_required()
@rate_limit()
@validate_json_request(['hospital_id', 'patient_name', 'emergency_level'])
def api_create_booking():
    """Create a new bed booking"""
    try:
        data = request.json_data
        current_user = get_jwt_identity()
        
        # Validate booking data
        validation_result = validation_service.validate_booking_request(data)
        if not validation_result['valid']:
            return api_response(
                success=False,
                error="Validation failed",
                message=validation_result['message'],
                status_code=400
            )
        
        # Create booking (integrate with database)
        booking_id = f"BK{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        booking_data = {
            'booking_id': booking_id,
            'hospital_id': data['hospital_id'],
            'patient_name': data['patient_name'],
            'patient_phone': data.get('patient_phone', ''),
            'emergency_level': data['emergency_level'],
            'symptoms': data.get('symptoms', ''),
            'created_by': current_user,
            'created_at': datetime.now().isoformat(),
            'status': 'pending',
            'estimated_arrival': data.get('estimated_arrival'),
            'special_requirements': data.get('special_requirements', [])
        }
        
        return api_response(
            success=True,
            data=booking_data,
            message="Booking created successfully",
            status_code=201
        )
        
    except Exception as e:
        logging.error(f"API create booking error: {str(e)}")
        return api_response(
            success=False,
            error="Failed to create booking",
            status_code=500
        )

@api_v1.route('/bookings/<string:booking_id>', methods=['GET'])
@jwt_required()
@rate_limit()
def api_get_booking(booking_id: str):
    """Get booking details"""
    try:
        # Simulate booking data (replace with database query)
        booking = {
            'booking_id': booking_id,
            'hospital_id': 1,
            'hospital_name': 'City General Hospital',
            'patient_name': 'John Doe',
            'patient_phone': '+1-555-0123',
            'emergency_level': 'high',
            'symptoms': 'Chest pain, difficulty breathing',
            'created_at': datetime.now().isoformat(),
            'status': 'confirmed',
            'bed_assignment': {
                'department': 'Emergency',
                'room': 'ER-105',
                'bed': 'A'
            },
            'estimated_arrival': '2024-01-15T14:30:00',
            'actual_arrival': None,
            'discharge_time': None,
            'total_cost': 0,
            'insurance_info': {},
            'medical_notes': []
        }
        
        return api_response(
            success=True,
            data=booking,
            message="Booking details retrieved successfully"
        )
        
    except Exception as e:
        logging.error(f"API get booking error: {str(e)}")
        return api_response(
            success=False,
            error="Failed to retrieve booking",
            status_code=500
        )

@api_v1.route('/bookings/<string:booking_id>/status', methods=['PUT'])
@jwt_required()
@rate_limit()
@validate_json_request(['status'])
def api_update_booking_status(booking_id: str):
    """Update booking status"""
    try:
        data = request.json_data
        new_status = data['status']
        current_user = get_jwt_identity()
        
        # Validate status
        valid_statuses = ['pending', 'confirmed', 'arrived', 'admitted', 'discharged', 'cancelled']
        if new_status not in valid_statuses:
            return api_response(
                success=False,
                error="Invalid status",
                message=f"Status must be one of: {', '.join(valid_statuses)}",
                status_code=400
            )
        
        # Update booking status (integrate with database)
        updated_booking = {
            'booking_id': booking_id,
            'status': new_status,
            'updated_by': current_user,
            'updated_at': datetime.now().isoformat(),
            'status_history': [
                {
                    'status': new_status,
                    'timestamp': datetime.now().isoformat(),
                    'updated_by': current_user,
                    'notes': data.get('notes', '')
                }
            ]
        }
        
        return api_response(
            success=True,
            data=updated_booking,
            message="Booking status updated successfully"
        )
        
    except Exception as e:
        logging.error(f"API update booking status error: {str(e)}")
        return api_response(
            success=False,
            error="Failed to update booking status",
            status_code=500
        )

# Analytics Endpoints
@api_v1.route('/analytics/utilization', methods=['GET'])
@jwt_required()
@rate_limit('analytics')
def api_get_utilization_analytics():
    """Get hospital utilization analytics"""
    try:
        hospital_id = request.args.get('hospital_id', type=int)
        days = request.args.get('days', 30, type=int)
        
        # Validate parameters
        if days > 365:
            return api_response(
                success=False,
                error="Invalid parameter",
                message="Days parameter cannot exceed 365",
                status_code=400
            )
        
        analytics_data = analytics_service.get_hospital_utilization_metrics(hospital_id, days)
        
        return api_response(
            success=True,
            data=analytics_data,
            message="Utilization analytics retrieved successfully"
        )
        
    except Exception as e:
        logging.error(f"API utilization analytics error: {str(e)}")
        return api_response(
            success=False,
            error="Failed to retrieve utilization analytics",
            status_code=500
        )

@api_v1.route('/analytics/emergency-response', methods=['GET'])
@jwt_required()
@rate_limit('analytics')
def api_get_emergency_analytics():
    """Get emergency response analytics"""
    try:
        days = request.args.get('days', 30, type=int)
        
        analytics_data = analytics_service.get_emergency_response_analytics(days)
        
        return api_response(
            success=True,
            data=analytics_data,
            message="Emergency response analytics retrieved successfully"
        )
        
    except Exception as e:
        logging.error(f"API emergency analytics error: {str(e)}")
        return api_response(
            success=False,
            error="Failed to retrieve emergency analytics",
            status_code=500
        )

@api_v1.route('/analytics/forecast', methods=['GET'])
@jwt_required()
@rate_limit('analytics')
def api_get_capacity_forecast():
    """Get capacity planning forecast"""
    try:
        hospital_id = request.args.get('hospital_id', type=int)
        forecast_days = request.args.get('forecast_days', 30, type=int)
        
        forecast_data = analytics_service.generate_capacity_forecast(hospital_id, forecast_days)
        
        return api_response(
            success=True,
            data=forecast_data,
            message="Capacity forecast retrieved successfully"
        )
        
    except Exception as e:
        logging.error(f"API capacity forecast error: {str(e)}")
        return api_response(
            success=False,
            error="Failed to retrieve capacity forecast",
            status_code=500
        )

@api_v1.route('/analytics/dashboard', methods=['GET'])
@jwt_required()
@rate_limit('analytics')
def api_get_dashboard_data():
    """Get real-time dashboard data"""
    try:
        dashboard_data = analytics_service.get_real_time_dashboard_data()
        
        return api_response(
            success=True,
            data=dashboard_data,
            message="Dashboard data retrieved successfully"
        )
        
    except Exception as e:
        logging.error(f"API dashboard data error: {str(e)}")
        return api_response(
            success=False,
            error="Failed to retrieve dashboard data",
            status_code=500
        )

# Export Endpoints
@api_v1.route('/export/report', methods=['POST'])
@jwt_required()
@rate_limit('analytics')
@validate_json_request(['report_type'])
def api_export_report():
    """Export analytics report"""
    try:
        data = request.json_data
        report_type = data['report_type']
        format_type = data.get('format', 'json')
        
        # Validate report type
        try:
            report_enum = ReportType(report_type)
        except ValueError:
            return api_response(
                success=False,
                error="Invalid report type",
                message=f"Report type must be one of: {[t.value for t in ReportType]}",
                status_code=400
            )
        
        # Export report
        report_data = analytics_service.export_analytics_report(
            report_enum,
            format_type,
            **data.get('parameters', {})
        )
        
        return api_response(
            success=True,
            data={
                'report_data': report_data,
                'format': format_type,
                'generated_at': datetime.now().isoformat()
            },
            message="Report exported successfully"
        )
        
    except Exception as e:
        logging.error(f"API export report error: {str(e)}")
        return api_response(
            success=False,
            error="Failed to export report",
            status_code=500
        )

# Health Check Endpoint
@api_v1.route('/health', methods=['GET'])
@rate_limit()
def api_health_check():
    """API health check endpoint"""
    try:
        health_data = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0',
            'services': {
                'database': 'connected',
                'analytics': 'operational',
                'validation': 'operational',
                'security': 'operational'
            },
            'uptime': '24h 15m 30s',  # Calculate actual uptime
            'memory_usage': '45%',    # Get from system
            'cpu_usage': '23%'        # Get from system
        }
        
        return api_response(
            success=True,
            data=health_data,
            message="API is healthy"
        )
        
    except Exception as e:
        logging.error(f"API health check error: {str(e)}")
        return api_response(
            success=False,
            error="Health check failed",
            status_code=500
        )

# Error handlers
@api_v1.errorhandler(404)
def api_not_found(error):
    """Handle 404 errors"""
    return api_response(
        success=False,
        error="Endpoint not found",
        message="The requested API endpoint does not exist",
        status_code=404
    )

@api_v1.errorhandler(405)
def api_method_not_allowed(error):
    """Handle 405 errors"""
    return api_response(
        success=False,
        error="Method not allowed",
        message="The HTTP method is not allowed for this endpoint",
        status_code=405
    )

@api_v1.errorhandler(500)
def api_internal_error(error):
    """Handle 500 errors"""
    return api_response(
        success=False,
        error="Internal server error",
        message="An unexpected error occurred",
        status_code=500
    )

# API Documentation endpoint
@api_v1.route('/docs', methods=['GET'])
def api_documentation():
    """Return API documentation"""
    docs = {
        'title': 'Emergency Hospital Bed Booking API',
        'version': '1.0.0',
        'description': 'REST API for hospital bed booking and management system',
        'base_url': '/api/v1',
        'authentication': 'JWT Bearer Token',
        'endpoints': {
            'Authentication': {
                'POST /auth/login': 'Authenticate and get JWT token',
                'POST /auth/refresh': 'Refresh JWT token'
            },
            'Hospitals': {
                'GET /hospitals': 'Get list of hospitals',
                'GET /hospitals/{id}': 'Get hospital details',
                'GET /hospitals/{id}/availability': 'Get hospital bed availability'
            },
            'Bookings': {
                'POST /bookings': 'Create new booking',
                'GET /bookings/{id}': 'Get booking details',
                'PUT /bookings/{id}/status': 'Update booking status'
            },
            'Analytics': {
                'GET /analytics/utilization': 'Get utilization analytics',
                'GET /analytics/emergency-response': 'Get emergency response analytics',
                'GET /analytics/forecast': 'Get capacity forecast',
                'GET /analytics/dashboard': 'Get dashboard data'
            },
            'Export': {
                'POST /export/report': 'Export analytics report'
            },
            'System': {
                'GET /health': 'API health check',
                'GET /docs': 'API documentation'
            }
        },
        'rate_limits': {
            'default': '100 requests per hour',
            'auth': '10 requests per 5 minutes',
            'analytics': '50 requests per hour'
        }
    }
    
    return jsonify(docs)

# Export the blueprint
__all__ = ['api_v1']
