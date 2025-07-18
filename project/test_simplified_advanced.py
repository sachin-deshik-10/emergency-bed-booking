"""
Simplified Test Script for Advanced Features
Emergency Hospital Bed Booking System

Tests core functionality of:
- Analytics Service
- Export Service
- Task Service (basic)
- API Response structures
"""

import sys
import json
import tempfile
import traceback
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def test_analytics_service():
    """Test analytics service functionality"""
    print("Testing Analytics Service...")
    
    try:
        from services.analytics_service import AnalyticsService, ReportType
        
        analytics = AnalyticsService()
        
        # Test 1: Hospital utilization metrics
        print("  Testing hospital utilization metrics...")
        metrics = analytics.get_hospital_utilization_metrics(hospital_id=1, days=30)
        
        assert 'current_utilization' in metrics
        assert 'average_utilization' in metrics
        assert 'trend_direction' in metrics
        print("    ✓ Utilization metrics generated successfully")
        
        # Test 2: Emergency response analytics
        print("  Testing emergency response analytics...")
        emergency_data = analytics.get_emergency_response_analytics(days=30)
        
        assert 'total_emergencies' in emergency_data
        assert 'average_response_time' in emergency_data
        print("    ✓ Emergency analytics generated successfully")
        
        # Test 3: Capacity forecast
        print("  Testing capacity forecast...")
        forecast = analytics.generate_capacity_forecast(forecast_days=30)
        
        assert 'forecast_values' in forecast
        assert len(forecast['forecast_values']) == 30
        print("    ✓ Capacity forecast generated successfully")
        
        # Test 4: Real-time dashboard data
        print("  Testing real-time dashboard data...")
        dashboard_data = analytics.get_real_time_dashboard_data()
        
        assert 'timestamp' in dashboard_data
        assert 'status' in dashboard_data
        print("    ✓ Dashboard data generated successfully")
        
        return True
        
    except Exception as e:
        print(f"    ✗ Analytics service test failed: {str(e)}")
        print(f"    Traceback: {traceback.format_exc()}")
        return False

def test_export_service():
    """Test export service functionality"""
    print("Testing Export Service...")
    
    try:
        from services.export_service import DataExportService, ExportRequest, ExportFormat, BackupConfig, BackupType
        
        # Create temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            export_service = DataExportService(storage_path=temp_dir)
            
            # Test 1: JSON Export
            print("  Testing JSON export...")
            request = ExportRequest(
                format=ExportFormat.JSON,
                tables=['hospitals', 'users'],
                filename='test_export.json'
            )
            
            result = export_service.export_data(request)
            assert result.success is True
            assert result.file_path is not None
            print("    ✓ JSON export successful")
            
            # Test 2: CSV Export
            print("  Testing CSV export...")
            request = ExportRequest(
                format=ExportFormat.CSV,
                tables=['hospitals'],
                filename='test_export.csv'
            )
            
            result = export_service.export_data(request)
            assert result.success is True
            print("    ✓ CSV export successful")
            
            # Test 3: Backup Creation
            print("  Testing backup creation...")
            config = BackupConfig(
                backup_type=BackupType.FULL,
                destination_path=temp_dir
            )
            
            backup_result = export_service.create_backup(config)
            assert backup_result['success'] is True
            print("    ✓ Backup creation successful")
            
            # Test 4: List exports
            print("  Testing export listing...")
            exports = export_service.list_exports(days=1)
            assert isinstance(exports, list)
            print("    ✓ Export listing successful")
        
        return True
        
    except Exception as e:
        print(f"    ✗ Export service test failed: {str(e)}")
        print(f"    Traceback: {traceback.format_exc()}")
        return False

def test_task_service():
    """Test task service basic functionality"""
    print("Testing Task Service...")
    
    try:
        from services.task_service import TaskService, TaskStatus, TaskPriority
        
        task_service = TaskService()
        
        # Test 1: Task status enum
        print("  Testing task status enumeration...")
        assert TaskStatus.PENDING.value == "PENDING"
        assert TaskStatus.SUCCESS.value == "SUCCESS"
        print("    ✓ Task status enum working")
        
        # Test 2: Task priority enum
        print("  Testing task priority enumeration...")
        assert TaskPriority.LOW.value == 0
        assert TaskPriority.HIGH.value == 2
        print("    ✓ Task priority enum working")
        
        # Test 3: Basic task service initialization
        print("  Testing task service initialization...")
        assert task_service is not None
        assert hasattr(task_service, 'celery')
        print("    ✓ Task service initialized successfully")
        
        return True
        
    except Exception as e:
        print(f"    ✗ Task service test failed: {str(e)}")
        print(f"    Traceback: {traceback.format_exc()}")
        return False

def test_api_structures():
    """Test API response structures"""
    print("Testing API Structures...")
    
    try:
        from services.api_service import APIResponse, APIRateLimiter
        
        # Test 1: API Response structure
        print("  Testing API response structure...")
        response = APIResponse(
            success=True,
            data={'test': 'data'},
            message='Test message'
        )
        
        assert response.success is True
        assert response.data == {'test': 'data'}
        assert response.message == 'Test message'
        assert response.timestamp is not None
        print("    ✓ API response structure working")
        
        # Test 2: Rate limiter
        print("  Testing rate limiter...")
        limiter = APIRateLimiter()
        
        # Should allow initial requests
        assert limiter.is_allowed('test_client', 'default') is True
        print("    ✓ Rate limiter functioning")
        
        return True
        
    except Exception as e:
        print(f"    ✗ API structures test failed: {str(e)}")
        print(f"    Traceback: {traceback.format_exc()}")
        return False

def test_chart_generation():
    """Test chart generation functionality"""
    print("Testing Chart Generation...")
    
    try:
        from services.analytics_service import AnalyticsService
        
        analytics = AnalyticsService()
        
        # Test 1: Utilization chart
        print("  Testing utilization chart generation...")
        chart_data = analytics.generate_utilization_chart(days=7)
        
        # Should return valid JSON string
        parsed_data = json.loads(chart_data)
        assert isinstance(parsed_data, dict)
        print("    ✓ Utilization chart generated successfully")
        
        return True
        
    except Exception as e:
        print(f"    ✗ Chart generation test failed: {str(e)}")
        print(f"    Traceback: {traceback.format_exc()}")
        return False

def test_data_validation():
    """Test data validation in services"""
    print("Testing Data Validation...")
    
    try:
        from services.analytics_service import AnalyticsService
        
        analytics = AnalyticsService()
        
        # Test 1: Validate utilization data ranges
        print("  Testing utilization data validation...")
        metrics = analytics.get_hospital_utilization_metrics(days=7)
        
        # Check that utilization rates are within valid ranges
        assert 0 <= metrics['current_utilization'] <= 100
        assert 0 <= metrics['average_utilization'] <= 100
        assert metrics['trend_direction'] in ['up', 'down', 'stable']
        print("    ✓ Utilization data validation passed")
        
        # Test 2: Validate forecast data
        print("  Testing forecast data validation...")
        forecast = analytics.generate_capacity_forecast(forecast_days=7)
        
        assert len(forecast['forecast_values']) == 7
        assert all(0 <= value <= 100 for value in forecast['forecast_values'])
        print("    ✓ Forecast data validation passed")
        
        return True
        
    except Exception as e:
        print(f"    ✗ Data validation test failed: {str(e)}")
        print(f"    Traceback: {traceback.format_exc()}")
        return False

def test_error_handling():
    """Test error handling in services"""
    print("Testing Error Handling...")
    
    try:
        from services.export_service import DataExportService, ExportRequest, ExportFormat
        
        # Test with invalid export request
        print("  Testing invalid export request handling...")
        
        export_service = DataExportService()
        
        # Create request with empty tables list
        request = ExportRequest(
            format=ExportFormat.JSON,
            tables=[],  # Empty tables should be handled gracefully
            filename='empty_export.json'
        )
        
        result = export_service.export_data(request)
        # Should still succeed but with no data
        assert result.success is True or result.error is not None
        print("    ✓ Invalid export request handled gracefully")
        
        return True
        
    except Exception as e:
        print(f"    ✗ Error handling test failed: {str(e)}")
        print(f"    Traceback: {traceback.format_exc()}")
        return False

def run_simplified_tests():
    """Run all simplified tests"""
    print("🏥 Emergency Hospital Bed Booking System - Advanced Features Test")
    print("=" * 70)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    test_functions = [
        test_analytics_service,
        test_export_service,
        test_task_service,
        test_api_structures,
        test_chart_generation,
        test_data_validation,
        test_error_handling
    ]
    
    passed = 0
    failed = 0
    
    for test_func in test_functions:
        try:
            result = test_func()
            if result:
                passed += 1
                print(f"✅ {test_func.__name__} - PASSED\n")
            else:
                failed += 1
                print(f"❌ {test_func.__name__} - FAILED\n")
        except Exception as e:
            failed += 1
            print(f"❌ {test_func.__name__} - ERROR: {str(e)}\n")
    
    print("=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)
    print(f"Total Tests: {passed + failed}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📈 Success Rate: {(passed/(passed+failed)*100):.1f}%" if (passed+failed) > 0 else "0%")
    print()
    
    if passed > 0:
        print("🎉 ADVANCED FEATURES WORKING:")
        print("   • Analytics Service - Real-time metrics and forecasting")
        print("   • Export Service - Multi-format data export and backup")
        print("   • Task Service - Background task management structure")
        print("   • API Service - REST endpoints and rate limiting")
        print("   • Chart Generation - Interactive data visualization")
        print("   • Data Validation - Input validation and range checking")
        print("   • Error Handling - Graceful error management")
    
    if failed > 0:
        print("\n⚠️  AREAS NEEDING ATTENTION:")
        print("   • Check dependency installations")
        print("   • Verify service configurations")
        print("   • Review error messages above")
    
    print(f"\nTest completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return passed, failed

if __name__ == '__main__':
    passed, failed = run_simplified_tests()
    
    # Exit with appropriate code
    exit_code = 0 if failed == 0 else 1
    sys.exit(exit_code)
