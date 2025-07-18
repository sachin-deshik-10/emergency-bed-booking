"""
Comprehensive Test Suite for Advanced Features
Emergency Hospital Bed Booking System

Tests for:
- Analytics Service
- API Service
- Task Service
- Export Service
- Enhanced Dashboard
- Background Tasks
- Real-time Features
"""

import pytest
import json
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
import tempfile
import os
from pathlib import Path

# Import services to test
from services.analytics_service import AnalyticsService, ReportType, AnalyticsMetric
from services.api_service import api_v1, APIRateLimiter, APIResponse
from services.task_service import TaskService, TaskStatus, TaskPriority, celery_app
from services.export_service import DataExportService, ExportRequest, ExportFormat, BackupConfig, BackupType

class TestAnalyticsService:
    """Test analytics and reporting functionality"""
    
    def setup_method(self):
        """Setup test environment"""
        self.analytics = AnalyticsService()
    
    def test_hospital_utilization_metrics(self):
        """Test hospital utilization calculation"""
        # Test basic utilization metrics
        metrics = self.analytics.get_hospital_utilization_metrics(hospital_id=1, days=30)
        
        assert 'current_utilization' in metrics
        assert 'average_utilization' in metrics
        assert 'peak_utilization' in metrics
        assert 'trend_direction' in metrics
        assert 'metrics' in metrics
        
        # Validate metric ranges
        assert 0 <= metrics['current_utilization'] <= 100
        assert 0 <= metrics['average_utilization'] <= 100
        assert 0 <= metrics['peak_utilization'] <= 100
        
        # Test metrics structure
        assert isinstance(metrics['metrics'], list)
        if metrics['metrics']:
            metric = metrics['metrics'][0]
            assert hasattr(metric, 'name')
            assert hasattr(metric, 'value')
            assert hasattr(metric, 'unit')
    
    def test_utilization_chart_generation(self):
        """Test chart generation for utilization data"""
        chart_json = self.analytics.generate_utilization_chart(hospital_id=1, days=7)
        
        # Should return valid JSON
        chart_data = json.loads(chart_json)
        assert 'data' in chart_data or 'error' in chart_data
        
        if 'data' in chart_data:
            # Validate Plotly chart structure
            assert isinstance(chart_data['data'], list)
    
    def test_emergency_response_analytics(self):
        """Test emergency response metrics"""
        analytics = self.analytics.get_emergency_response_analytics(days=30)
        
        assert 'total_emergencies' in analytics
        assert 'average_response_time' in analytics
        assert 'response_rate_sla' in analytics
        
        # Validate data types
        assert isinstance(analytics['total_emergencies'], int)
        assert isinstance(analytics['average_response_time'], (int, float))
        assert 0 <= analytics['response_rate_sla'] <= 100
    
    def test_capacity_forecast(self):
        """Test capacity planning forecast"""
        forecast = self.analytics.generate_capacity_forecast(hospital_id=1, forecast_days=30)
        
        assert 'forecast_period_days' in forecast
        assert 'forecast_values' in forecast
        assert 'recommendations' in forecast
        
        # Validate forecast structure
        assert len(forecast['forecast_values']) == 30
        assert all(0 <= value <= 100 for value in forecast['forecast_values'])
    
    def test_real_time_dashboard_data(self):
        """Test real-time dashboard data generation"""
        dashboard_data = self.analytics.get_real_time_dashboard_data()
        
        assert 'timestamp' in dashboard_data
        assert 'utilization_summary' in dashboard_data
        assert 'emergency_summary' in dashboard_data
        assert 'system_health' in dashboard_data
        assert 'status' in dashboard_data
        
        # Validate status
        assert dashboard_data['status'] in ['operational', 'degraded', 'critical', 'error']
    
    def test_export_analytics_report(self):
        """Test analytics report export"""
        report = self.analytics.export_analytics_report(
            ReportType.UTILIZATION,
            format='json',
            days=7
        )
        
        # Should return valid JSON string
        report_data = json.loads(report)
        assert 'report_metadata' in report_data

class TestAPIService:
    """Test REST API endpoints and functionality"""
    
    def setup_method(self):
        """Setup test environment"""
        from flask import Flask
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.app.config['JWT_SECRET_KEY'] = 'test-secret'
        
        # Register API blueprint
        self.app.register_blueprint(api_v1)
        self.client = self.app.test_client()
        
        # Setup JWT
        from flask_jwt_extended import JWTManager
        self.jwt = JWTManager(self.app)
    
    def test_api_health_check(self):
        """Test API health check endpoint"""
        response = self.client.get('/api/v1/health')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'status' in data['data']
    
    def test_api_documentation(self):
        """Test API documentation endpoint"""
        response = self.client.get('/api/v1/docs')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'title' in data
        assert 'endpoints' in data
    
    def test_rate_limiting(self):
        """Test API rate limiting functionality"""
        rate_limiter = APIRateLimiter()
        
        # Test normal operation
        assert rate_limiter.is_allowed('test_client', 'default') is True
        
        # Test rate limit exceeded
        for _ in range(101):  # Exceed default limit of 100
            rate_limiter.is_allowed('test_client', 'default')
        
        assert rate_limiter.is_allowed('test_client', 'default') is False
    
    def test_api_response_format(self):
        """Test standardized API response format"""
        from services.api_service import APIResponse
        
        response = APIResponse(
            success=True,
            data={'test': 'data'},
            message='Test message'
        )
        
        assert response.success is True
        assert response.data == {'test': 'data'}
        assert response.message == 'Test message'
        assert response.timestamp is not None
    
    @patch('services.validation_service.validation_service.validate_login_credentials')
    def test_api_login(self, mock_validate):
        """Test API login endpoint"""
        mock_validate.return_value = True
        
        response = self.client.post('/api/v1/auth/login', 
                                  json={'username': 'test', 'password': 'test123'})
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'access_token' in data['data']

class TestTaskService:
    """Test background task management"""
    
    def setup_method(self):
        """Setup test environment"""
        self.task_service = TaskService()
    
    def test_task_submission(self):
        """Test submitting background tasks"""
        # Mock celery task submission
        with patch.object(self.task_service.celery, 'send_task') as mock_send:
            mock_task = Mock()
            mock_task.id = 'test-task-123'
            mock_send.return_value = mock_task
            
            task_id = self.task_service.submit_task(
                'test.task',
                args=('arg1', 'arg2'),
                kwargs={'key': 'value'}
            )
            
            assert task_id == 'test-task-123'
            mock_send.assert_called_once()
    
    def test_task_status_retrieval(self):
        """Test getting task status"""
        # Mock AsyncResult
        with patch('services.task_service.AsyncResult') as mock_result:
            mock_result.return_value.status = 'SUCCESS'
            mock_result.return_value.result = {'status': 'completed'}
            mock_result.return_value.successful.return_value = True
            mock_result.return_value.ready.return_value = True
            
            result = self.task_service.get_task_status('test-task-123')
            
            assert result.task_id == 'test-task-123'
            assert result.status == TaskStatus.SUCCESS
    
    def test_task_cancellation(self):
        """Test cancelling tasks"""
        with patch.object(self.task_service.celery.control, 'revoke') as mock_revoke:
            success = self.task_service.cancel_task('test-task-123')
            
            assert success is True
            mock_revoke.assert_called_once_with('test-task-123', terminate=True)
    
    def test_active_tasks_retrieval(self):
        """Test getting active tasks"""
        with patch.object(self.task_service.celery.control, 'inspect') as mock_inspect:
            mock_inspect.return_value.active.return_value = {
                'worker1': [
                    {
                        'id': 'task1',
                        'name': 'test.task',
                        'args': [],
                        'kwargs': {}
                    }
                ]
            }
            
            active_tasks = self.task_service.get_active_tasks()
            
            assert len(active_tasks) == 1
            assert active_tasks[0]['task_id'] == 'task1'

class TestExportService:
    """Test data export and backup functionality"""
    
    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.export_service = DataExportService(storage_path=self.temp_dir)
    
    def teardown_method(self):
        """Cleanup test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_json_export(self):
        """Test JSON data export"""
        request = ExportRequest(
            format=ExportFormat.JSON,
            tables=['hospitals', 'users'],
            filename='test_export.json'
        )
        
        result = self.export_service.export_data(request)
        
        assert result.success is True
        assert result.file_path is not None
        assert os.path.exists(result.file_path)
        assert result.format == ExportFormat.JSON
        
        # Validate JSON content
        with open(result.file_path, 'r') as f:
            data = json.load(f)
            assert 'data' in data
            assert 'hospitals' in data['data']
            assert 'users' in data['data']
    
    def test_csv_export(self):
        """Test CSV data export"""
        request = ExportRequest(
            format=ExportFormat.CSV,
            tables=['hospitals'],
            filename='test_export.csv'
        )
        
        result = self.export_service.export_data(request)
        
        assert result.success is True
        assert result.file_path is not None
        assert os.path.exists(result.file_path)
    
    def test_excel_export(self):
        """Test Excel data export"""
        request = ExportRequest(
            format=ExportFormat.EXCEL,
            tables=['hospitals', 'bookings'],
            filename='test_export.xlsx'
        )
        
        result = self.export_service.export_data(request)
        
        assert result.success is True
        assert result.file_path is not None
        assert os.path.exists(result.file_path)
        assert result.file_path.endswith('.xlsx')
    
    def test_backup_creation(self):
        """Test database backup creation"""
        config = BackupConfig(
            backup_type=BackupType.FULL,
            destination_path=self.temp_dir,
            retention_days=30
        )
        
        result = self.export_service.create_backup(config)
        
        assert result['success'] is True
        assert 'backup_path' in result
        assert os.path.exists(result['backup_path'])
    
    def test_export_list(self):
        """Test listing export files"""
        # Create a test export file
        test_file = Path(self.temp_dir) / "exports" / "test.json"
        test_file.parent.mkdir(exist_ok=True)
        test_file.write_text('{"test": "data"}')
        
        exports = self.export_service.list_exports(days=30)
        
        assert len(exports) >= 1
        assert exports[0]['filename'] == 'test.json'
        assert 'size' in exports[0]
        assert 'created' in exports[0]

class TestEnhancedDashboard:
    """Test enhanced dashboard functionality"""
    
    def setup_method(self):
        """Setup test environment"""
        from flask import Flask
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.app.config['SECRET_KEY'] = 'test-secret'
        
        # Mock session
        with self.app.test_request_context():
            from flask import session
            session['user_id'] = 1
            session['username'] = 'test_user'
            session['role'] = 'admin'
            
            self.client = self.app.test_client()
    
    def test_dashboard_data_structure(self):
        """Test dashboard data structure"""
        from services.analytics_service import analytics_service
        
        dashboard_data = analytics_service.get_real_time_dashboard_data()
        
        # Validate required fields
        required_fields = [
            'timestamp', 'utilization_summary', 
            'emergency_summary', 'system_health', 'status'
        ]
        
        for field in required_fields:
            assert field in dashboard_data
        
        # Validate utilization summary
        util_summary = dashboard_data['utilization_summary']
        assert 'current' in util_summary
        assert 'trend' in util_summary
        
        # Validate system health
        health = dashboard_data['system_health']
        assert 'api_response_time' in health
        assert 'active_users' in health

class TestIntegrationScenarios:
    """Test integration between different components"""
    
    def test_booking_to_analytics_flow(self):
        """Test complete booking to analytics flow"""
        # This would test the full flow from booking creation
        # to analytics processing in a real environment
        pass
    
    def test_real_time_updates_flow(self):
        """Test real-time update propagation"""
        # This would test WebSocket updates from booking
        # changes to dashboard updates
        pass
    
    def test_export_and_backup_integration(self):
        """Test export and backup working together"""
        # This would test exporting data and creating backups
        # in sequence
        pass

class TestPerformanceAndScalability:
    """Test performance characteristics"""
    
    def test_analytics_performance(self):
        """Test analytics calculation performance"""
        from services.analytics_service import analytics_service
        import time
        
        start_time = time.time()
        
        # Test large dataset processing
        metrics = analytics_service.get_hospital_utilization_metrics(days=365)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Should complete within reasonable time
        assert processing_time < 5.0  # 5 seconds max
        assert metrics is not None
    
    def test_concurrent_api_requests(self):
        """Test API handling concurrent requests"""
        # This would test API rate limiting and concurrent handling
        pass
    
    def test_large_export_handling(self):
        """Test handling large data exports"""
        from services.export_service import ExportService
        
        # Test export with large dataset simulation
        request = ExportRequest(
            format=ExportFormat.JSON,
            tables=['hospitals', 'bookings', 'users']
        )
        
        export_service = DataExportService()
        result = export_service.export_data(request)
        
        assert result.success is True

class TestSecurityAndValidation:
    """Test security features and data validation"""
    
    def test_api_authentication(self):
        """Test API authentication requirements"""
        # This would test JWT token validation and required auth
        pass
    
    def test_input_validation(self):
        """Test input validation in all endpoints"""
        from services.validation_service import validation_service
        
        # Test booking validation
        invalid_booking = {
            'hospital_id': 'invalid',
            'patient_name': '',
            'emergency_level': 'invalid_level'
        }
        
        result = validation_service.validate_booking_request(invalid_booking)
        assert result['valid'] is False
        assert 'message' in result
    
    def test_rate_limiting_security(self):
        """Test rate limiting as security measure"""
        from services.api_service import APIRateLimiter
        
        limiter = APIRateLimiter()
        
        # Test auth endpoint rate limiting (more restrictive)
        client_id = 'test_client'
        
        # Should allow initial requests
        for _ in range(10):
            assert limiter.is_allowed(client_id, 'auth') is True
        
        # Should block after limit
        assert limiter.is_allowed(client_id, 'auth') is False

def run_all_tests():
    """Run all tests and provide summary"""
    print("Running Enhanced Emergency Booking System Test Suite")
    print("=" * 60)
    
    test_classes = [
        TestAnalyticsService,
        TestAPIService,
        TestTaskService,
        TestExportService,
        TestEnhancedDashboard,
        TestIntegrationScenarios,
        TestPerformanceAndScalability,
        TestSecurityAndValidation
    ]
    
    total_tests = 0
    passed_tests = 0
    failed_tests = []
    
    for test_class in test_classes:
        print(f"\nTesting {test_class.__name__}...")
        
        # Get all test methods
        test_methods = [method for method in dir(test_class) 
                       if method.startswith('test_')]
        
        for test_method in test_methods:
            total_tests += 1
            
            try:
                # Create test instance and run test
                test_instance = test_class()
                if hasattr(test_instance, 'setup_method'):
                    test_instance.setup_method()
                
                getattr(test_instance, test_method)()
                
                if hasattr(test_instance, 'teardown_method'):
                    test_instance.teardown_method()
                
                passed_tests += 1
                print(f"  ✓ {test_method}")
                
            except Exception as e:
                failed_tests.append(f"{test_class.__name__}.{test_method}: {str(e)}")
                print(f"  ✗ {test_method}: {str(e)}")
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {len(failed_tests)}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if failed_tests:
        print("\nFAILED TESTS:")
        for failure in failed_tests:
            print(f"  - {failure}")
    
    return passed_tests, len(failed_tests), total_tests

if __name__ == '__main__':
    run_all_tests()
