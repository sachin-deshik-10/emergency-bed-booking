"""
Background Task Management Service for Emergency Hospital Bed Booking System

Handles asynchronous background tasks using Celery:
- Email notifications
- SMS alerts
- Report generation
- Data processing
- Scheduled maintenance
- Capacity predictions
- Performance monitoring

Features:
- Redis-backed task queue
- Task retry mechanisms
- Progress tracking
- Error handling
- Task scheduling
- Performance monitoring
"""

from celery import Celery, Task
from celery.result import AsyncResult
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import json
import logging
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from email.mime.base import MimeBase
from email import encoders
import requests
from dataclasses import dataclass, asdict
from enum import Enum

class TaskStatus(Enum):
    PENDING = "PENDING"
    STARTED = "STARTED" 
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    RETRY = "RETRY"
    REVOKED = "REVOKED"

class TaskPriority(Enum):
    LOW = 0
    NORMAL = 1
    HIGH = 2
    URGENT = 3

@dataclass
class TaskResult:
    task_id: str
    status: TaskStatus
    result: Any = None
    error: Optional[str] = None
    progress: float = 0.0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    metadata: Optional[Dict] = None

class BaseTaskClass(Task):
    """Base task class with common functionality"""
    
    def on_success(self, retval, task_id, args, kwargs):
        """Called on task success"""
        logging.info(f"Task {task_id} completed successfully")
        
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Called on task failure"""
        logging.error(f"Task {task_id} failed: {str(exc)}")
        
    def on_retry(self, exc, task_id, args, kwargs, einfo):
        """Called on task retry"""
        logging.warning(f"Task {task_id} retrying: {str(exc)}")

# Initialize Celery
def create_celery_app(app=None):
    """Create and configure Celery application"""
    celery = Celery(
        'emergency_booking_tasks',
        broker='redis://localhost:6379/0',
        backend='redis://localhost:6379/0',
        include=['services.task_service']
    )
    
    # Configuration
    celery.conf.update(
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone='UTC',
        enable_utc=True,
        task_track_started=True,
        task_time_limit=30 * 60,  # 30 minutes
        task_soft_time_limit=25 * 60,  # 25 minutes
        worker_prefetch_multiplier=1,
        worker_max_tasks_per_child=1000,
        task_routes={
            'services.task_service.send_email_notification': {'queue': 'notifications'},
            'services.task_service.send_sms_alert': {'queue': 'notifications'},
            'services.task_service.generate_analytics_report': {'queue': 'analytics'},
            'services.task_service.process_bed_utilization': {'queue': 'processing'},
            'services.task_service.cleanup_old_data': {'queue': 'maintenance'},
        },
        beat_schedule={
            'process-utilization-every-5-minutes': {
                'task': 'services.task_service.process_bed_utilization',
                'schedule': 300.0,  # 5 minutes
            },
            'cleanup-old-data-daily': {
                'task': 'services.task_service.cleanup_old_data',
                'schedule': 86400.0,  # 24 hours
            },
            'generate-daily-reports': {
                'task': 'services.task_service.generate_daily_reports',
                'schedule': 86400.0,  # 24 hours
                'options': {'queue': 'analytics'}
            },
        }
    )
    
    # Update task base
    celery.Task = BaseTaskClass
    
    if app:
        # Initialize Celery with Flask app context
        class ContextTask(celery.Task):
            def __call__(self, *args, **kwargs):
                with app.app_context():
                    return self.run(*args, **kwargs)
        celery.Task = ContextTask
    
    return celery

# Create global Celery instance
celery_app = create_celery_app()

class TaskService:
    """Service for managing background tasks"""
    
    def __init__(self, celery_app=None):
        self.celery = celery_app or celery_app
        self.email_config = {
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587,
            'username': 'your-email@gmail.com',
            'password': 'your-app-password'
        }
        self.sms_config = {
            'api_key': 'your-sms-api-key',
            'api_url': 'https://api.twilio.com/2010-04-01/Accounts/your-sid/Messages.json'
        }
    
    def submit_task(self, task_name: str, args: tuple = (), kwargs: dict = None,
                   priority: TaskPriority = TaskPriority.NORMAL,
                   eta: datetime = None, countdown: int = None) -> str:
        """
        Submit a background task for execution
        
        Args:
            task_name: Name of the task function
            args: Positional arguments for the task
            kwargs: Keyword arguments for the task
            priority: Task priority level
            eta: Absolute time when task should be executed
            countdown: Delay in seconds before executing task
            
        Returns:
            Task ID for tracking
        """
        if kwargs is None:
            kwargs = {}
            
        try:
            task = self.celery.send_task(
                task_name,
                args=args,
                kwargs=kwargs,
                priority=priority.value,
                eta=eta,
                countdown=countdown
            )
            
            logging.info(f"Task {task.id} submitted: {task_name}")
            return task.id
            
        except Exception as e:
            logging.error(f"Failed to submit task {task_name}: {str(e)}")
            raise
    
    def get_task_status(self, task_id: str) -> TaskResult:
        """Get status and result of a task"""
        try:
            result = AsyncResult(task_id, app=self.celery)
            
            return TaskResult(
                task_id=task_id,
                status=TaskStatus(result.status),
                result=result.result if result.successful() else None,
                error=str(result.result) if result.failed() else None,
                progress=getattr(result.result, 'progress', 0.0) if hasattr(result.result, 'progress') else 0.0,
                started_at=result.date_done,
                completed_at=result.date_done if result.ready() else None,
                metadata=getattr(result.result, 'metadata', {}) if hasattr(result.result, 'metadata') else {}
            )
            
        except Exception as e:
            return TaskResult(
                task_id=task_id,
                status=TaskStatus.FAILURE,
                error=f"Failed to get task status: {str(e)}"
            )
    
    def cancel_task(self, task_id: str) -> bool:
        """Cancel a pending or running task"""
        try:
            self.celery.control.revoke(task_id, terminate=True)
            logging.info(f"Task {task_id} cancelled")
            return True
        except Exception as e:
            logging.error(f"Failed to cancel task {task_id}: {str(e)}")
            return False
    
    def get_active_tasks(self) -> List[Dict]:
        """Get list of currently active tasks"""
        try:
            inspect = self.celery.control.inspect()
            active_tasks = inspect.active()
            
            if active_tasks:
                all_tasks = []
                for worker, tasks in active_tasks.items():
                    for task in tasks:
                        all_tasks.append({
                            'task_id': task['id'],
                            'name': task['name'],
                            'worker': worker,
                            'args': task.get('args', []),
                            'kwargs': task.get('kwargs', {}),
                            'time_start': task.get('time_start')
                        })
                return all_tasks
            return []
            
        except Exception as e:
            logging.error(f"Failed to get active tasks: {str(e)}")
            return []

# Global task service instance
task_service = TaskService(celery_app)

# Task Definitions
@celery_app.task(bind=True, name='services.task_service.send_email_notification')
def send_email_notification(self, to_email: str, subject: str, body: str, 
                           is_html: bool = False, attachments: List[Dict] = None):
    """
    Send email notification
    
    Args:
        to_email: Recipient email address
        subject: Email subject
        body: Email body content
        is_html: Whether body is HTML format
        attachments: List of attachment dictionaries
    """
    try:
        self.update_state(state='STARTED', meta={'progress': 0, 'status': 'Preparing email'})
        
        # Create message
        msg = MimeMultipart()
        msg['From'] = task_service.email_config['username']
        msg['To'] = to_email
        msg['Subject'] = subject
        
        # Attach body
        if is_html:
            msg.attach(MimeText(body, 'html'))
        else:
            msg.attach(MimeText(body, 'plain'))
        
        self.update_state(state='STARTED', meta={'progress': 30, 'status': 'Adding attachments'})
        
        # Add attachments
        if attachments:
            for attachment in attachments:
                part = MimeBase('application', 'octet-stream')
                part.set_payload(attachment['content'])
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename= {attachment["filename"]}'
                )
                msg.attach(part)
        
        self.update_state(state='STARTED', meta={'progress': 50, 'status': 'Connecting to SMTP server'})
        
        # Send email
        server = smtplib.SMTP(task_service.email_config['smtp_server'], 
                             task_service.email_config['smtp_port'])
        server.starttls()
        server.login(task_service.email_config['username'], 
                    task_service.email_config['password'])
        
        self.update_state(state='STARTED', meta={'progress': 80, 'status': 'Sending email'})
        
        text = msg.as_string()
        server.sendmail(task_service.email_config['username'], to_email, text)
        server.quit()
        
        logging.info(f"Email sent successfully to {to_email}")
        return {
            'status': 'success',
            'message': f'Email sent to {to_email}',
            'timestamp': datetime.now().isoformat(),
            'progress': 100
        }
        
    except Exception as e:
        logging.error(f"Failed to send email to {to_email}: {str(e)}")
        raise self.retry(exc=e, countdown=60, max_retries=3)

@celery_app.task(bind=True, name='services.task_service.send_sms_alert')
def send_sms_alert(self, phone_number: str, message: str, priority: str = 'normal'):
    """
    Send SMS alert notification
    
    Args:
        phone_number: Recipient phone number
        message: SMS message content
        priority: Message priority level
    """
    try:
        self.update_state(state='STARTED', meta={'progress': 0, 'status': 'Preparing SMS'})
        
        # Prepare SMS data
        sms_data = {
            'From': '+1234567890',  # Your Twilio number
            'To': phone_number,
            'Body': message
        }
        
        self.update_state(state='STARTED', meta={'progress': 50, 'status': 'Sending SMS'})
        
        # Send SMS (simulate for demo)
        # In production, use actual SMS service like Twilio
        response = {
            'sid': f'SM{datetime.now().strftime("%Y%m%d%H%M%S")}',
            'status': 'sent',
            'to': phone_number,
            'body': message
        }
        
        logging.info(f"SMS sent successfully to {phone_number}")
        return {
            'status': 'success',
            'message': f'SMS sent to {phone_number}',
            'sms_id': response['sid'],
            'timestamp': datetime.now().isoformat(),
            'progress': 100
        }
        
    except Exception as e:
        logging.error(f"Failed to send SMS to {phone_number}: {str(e)}")
        raise self.retry(exc=e, countdown=30, max_retries=3)

@celery_app.task(bind=True, name='services.task_service.generate_analytics_report')
def generate_analytics_report(self, report_type: str, parameters: Dict = None,
                             email_recipients: List[str] = None):
    """
    Generate and optionally email analytics report
    
    Args:
        report_type: Type of report to generate
        parameters: Report generation parameters
        email_recipients: List of email addresses to send report to
    """
    try:
        if parameters is None:
            parameters = {}
            
        self.update_state(state='STARTED', meta={'progress': 10, 'status': 'Initializing report generation'})
        
        # Import analytics service
        from .analytics_service import analytics_service, ReportType
        
        self.update_state(state='STARTED', meta={'progress': 30, 'status': 'Generating report data'})
        
        # Generate report
        report_enum = ReportType(report_type)
        report_data = analytics_service.export_analytics_report(
            report_enum,
            parameters.get('format', 'json'),
            **parameters
        )
        
        self.update_state(state='STARTED', meta={'progress': 70, 'status': 'Formatting report'})
        
        # Create report metadata
        report_info = {
            'report_id': f'RPT_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
            'type': report_type,
            'generated_at': datetime.now().isoformat(),
            'parameters': parameters,
            'data_size': len(str(report_data))
        }
        
        self.update_state(state='STARTED', meta={'progress': 85, 'status': 'Sending email notifications'})
        
        # Send email if recipients specified
        if email_recipients:
            for email in email_recipients:
                send_email_notification.delay(
                    to_email=email,
                    subject=f'Analytics Report: {report_type}',
                    body=f'Your requested analytics report has been generated.\n\nReport ID: {report_info["report_id"]}\nGenerated: {report_info["generated_at"]}',
                    attachments=[{
                        'filename': f'{report_type}_report.json',
                        'content': report_data.encode() if isinstance(report_data, str) else str(report_data).encode()
                    }]
                )
        
        logging.info(f"Analytics report generated: {report_info['report_id']}")
        return {
            'status': 'success',
            'report_info': report_info,
            'report_data': report_data if len(str(report_data)) < 10000 else 'Report too large for inline display',
            'progress': 100
        }
        
    except Exception as e:
        logging.error(f"Failed to generate analytics report: {str(e)}")
        raise self.retry(exc=e, countdown=120, max_retries=2)

@celery_app.task(bind=True, name='services.task_service.process_bed_utilization')
def process_bed_utilization(self):
    """
    Process bed utilization data and update metrics
    Runs every 5 minutes to keep utilization data current
    """
    try:
        self.update_state(state='STARTED', meta={'progress': 0, 'status': 'Starting utilization processing'})
        
        # Simulate bed utilization processing
        hospitals = [1, 2, 3, 4, 5]  # Hospital IDs
        
        for i, hospital_id in enumerate(hospitals):
            self.update_state(
                state='STARTED', 
                meta={
                    'progress': (i / len(hospitals)) * 100,
                    'status': f'Processing hospital {hospital_id}'
                }
            )
            
            # Simulate processing time
            import time
            time.sleep(2)
            
            # Update utilization metrics (integrate with database)
            utilization_data = {
                'hospital_id': hospital_id,
                'timestamp': datetime.now().isoformat(),
                'total_beds': 100,
                'occupied_beds': 75 + (i * 2),  # Simulate different utilization
                'utilization_rate': (75 + (i * 2)) / 100 * 100
            }
            
            logging.info(f"Updated utilization for hospital {hospital_id}: {utilization_data['utilization_rate']:.1f}%")
        
        return {
            'status': 'success',
            'hospitals_processed': len(hospitals),
            'timestamp': datetime.now().isoformat(),
            'progress': 100
        }
        
    except Exception as e:
        logging.error(f"Failed to process bed utilization: {str(e)}")
        raise

@celery_app.task(bind=True, name='services.task_service.cleanup_old_data')
def cleanup_old_data(self, days_to_keep: int = 90):
    """
    Clean up old data to maintain database performance
    Runs daily to remove old logs, expired sessions, etc.
    """
    try:
        self.update_state(state='STARTED', meta={'progress': 0, 'status': 'Starting data cleanup'})
        
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        cleanup_tasks = [
            'old_log_entries',
            'expired_sessions',
            'completed_bookings',
            'old_analytics_cache'
        ]
        
        results = {}
        
        for i, task in enumerate(cleanup_tasks):
            self.update_state(
                state='STARTED',
                meta={
                    'progress': (i / len(cleanup_tasks)) * 100,
                    'status': f'Cleaning up {task}'
                }
            )
            
            # Simulate cleanup (integrate with actual database cleanup)
            import time
            time.sleep(1)
            
            # Simulate cleanup results
            cleaned_count = 100 + (i * 50)  # Simulate different amounts cleaned
            results[task] = {
                'items_cleaned': cleaned_count,
                'cutoff_date': cutoff_date.isoformat()
            }
            
            logging.info(f"Cleaned up {cleaned_count} items from {task}")
        
        return {
            'status': 'success',
            'cleanup_results': results,
            'total_items_cleaned': sum(r['items_cleaned'] for r in results.values()),
            'cutoff_date': cutoff_date.isoformat(),
            'progress': 100
        }
        
    except Exception as e:
        logging.error(f"Failed to cleanup old data: {str(e)}")
        raise

@celery_app.task(bind=True, name='services.task_service.generate_daily_reports')
def generate_daily_reports(self):
    """
    Generate daily summary reports for administrators
    Runs once per day to create management reports
    """
    try:
        self.update_state(state='STARTED', meta={'progress': 0, 'status': 'Generating daily reports'})
        
        # Generate different types of daily reports
        reports = [
            'utilization_summary',
            'emergency_response_summary',
            'booking_statistics',
            'system_performance'
        ]
        
        generated_reports = {}
        
        for i, report_type in enumerate(reports):
            self.update_state(
                state='STARTED',
                meta={
                    'progress': (i / len(reports)) * 100,
                    'status': f'Generating {report_type}'
                }
            )
            
            # Generate report (integrate with analytics service)
            report_data = {
                'report_type': report_type,
                'date': datetime.now().strftime('%Y-%m-%d'),
                'summary': f'Daily {report_type.replace("_", " ")} report',
                'metrics': {
                    'total_entries': 100 + (i * 25),
                    'average_value': 75.5 + (i * 2.5),
                    'peak_value': 95.0 + (i * 1.5)
                }
            }
            
            generated_reports[report_type] = report_data
            
            # Send report to administrators (simulate)
            admin_emails = ['admin@hospital.com', 'manager@hospital.com']
            for email in admin_emails:
                send_email_notification.delay(
                    to_email=email,
                    subject=f'Daily Report: {report_type.replace("_", " ").title()}',
                    body=f'Daily report for {datetime.now().strftime("%Y-%m-%d")}:\n\n{json.dumps(report_data, indent=2)}'
                )
        
        logging.info(f"Generated {len(reports)} daily reports")
        return {
            'status': 'success',
            'reports_generated': list(generated_reports.keys()),
            'date': datetime.now().strftime('%Y-%m-%d'),
            'progress': 100
        }
        
    except Exception as e:
        logging.error(f"Failed to generate daily reports: {str(e)}")
        raise

# Export the Celery app and service
__all__ = ['celery_app', 'task_service', 'TaskService', 'TaskStatus', 'TaskPriority', 'TaskResult']
