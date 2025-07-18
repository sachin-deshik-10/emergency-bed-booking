"""
Real-Time Communication Service using WebSockets
Handles live bed availability updates, notifications, and real-time features
"""

from flask_socketio import SocketIO, emit, join_room, leave_room, disconnect
from flask_login import current_user
from flask import request
import json
import redis
from datetime import datetime
from typing import Dict, List, Optional
import logging

class RealTimeService:
    """Service for handling real-time communication and updates"""
    
    def __init__(self, app=None, redis_url: Optional[str] = None):
        self.socketio = None
        self.redis_client = None
        self.connected_users = {}
        self.hospital_rooms = {}
        
        if redis_url:
            try:
                self.redis_client = redis.from_url(redis_url)
            except Exception as e:
                logging.warning(f"Redis connection failed: {e}")
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize SocketIO with Flask app"""
        self.socketio = SocketIO(
            app,
            cors_allowed_origins="*",
            async_mode='eventlet',
            logger=True,
            engineio_logger=True
        )
        
        # Register event handlers
        self._register_handlers()
    
    def _register_handlers(self):
        """Register WebSocket event handlers"""
        
        @self.socketio.on('connect')
        def handle_connect():
            """Handle client connection"""
            if current_user.is_authenticated:
                user_id = str(current_user.id)
                user_type = getattr(current_user, 'user_type', 'patient')
                
                self.connected_users[request.sid] = {
                    'user_id': user_id,
                    'user_type': user_type,
                    'connected_at': datetime.utcnow().isoformat(),
                    'ip_address': request.remote_addr
                }
                
                # Join appropriate rooms based on user type
                if user_type == 'hospital':
                    hospital_code = getattr(current_user, 'hcode', None)
                    if hospital_code:
                        join_room(f"hospital_{hospital_code}")
                        self.hospital_rooms[request.sid] = hospital_code
                elif user_type == 'admin':
                    join_room('admin_room')
                
                join_room('all_users')
                
                emit('connection_confirmed', {
                    'status': 'connected',
                    'user_type': user_type,
                    'timestamp': datetime.utcnow().isoformat()
                })
                
                # Send current bed availability
                self._send_bed_availability_update(user_id, user_type)
                
                logging.info(f"User {user_id} ({user_type}) connected")
            else:
                disconnect()
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """Handle client disconnection"""
            if request.sid in self.connected_users:
                user_info = self.connected_users[request.sid]
                user_id = user_info['user_id']
                
                # Leave hospital room if applicable
                if request.sid in self.hospital_rooms:
                    hospital_code = self.hospital_rooms[request.sid]
                    leave_room(f"hospital_{hospital_code}")
                    del self.hospital_rooms[request.sid]
                
                del self.connected_users[request.sid]
                logging.info(f"User {user_id} disconnected")
        
        @self.socketio.on('join_hospital_updates')
        def handle_join_hospital_updates(data):
            """Allow users to subscribe to specific hospital updates"""
            hospital_code = data.get('hospital_code')
            if hospital_code and current_user.is_authenticated:
                join_room(f"hospital_{hospital_code}_public")
                emit('joined_hospital_updates', {
                    'hospital_code': hospital_code,
                    'status': 'subscribed'
                })
        
        @self.socketio.on('request_bed_update')
        def handle_bed_update_request():
            """Handle request for current bed availability"""
            if current_user.is_authenticated:
                user_type = getattr(current_user, 'user_type', 'patient')
                self._send_bed_availability_update(current_user.id, user_type)
        
        @self.socketio.on('hospital_bed_update')
        def handle_hospital_bed_update(data):
            """Handle bed availability updates from hospital staff"""
            if current_user.is_authenticated and getattr(current_user, 'user_type', '') == 'hospital':
                hospital_code = getattr(current_user, 'hcode', None)
                if hospital_code:
                    self._broadcast_bed_update(hospital_code, data)
        
        @self.socketio.on('emergency_alert')
        def handle_emergency_alert(data):
            """Handle emergency alerts from authorized users"""
            if current_user.is_authenticated:
                user_type = getattr(current_user, 'user_type', 'patient')
                if user_type in ['hospital', 'admin']:
                    self._broadcast_emergency_alert(data)
    
    def _send_bed_availability_update(self, user_id: str, user_type: str):
        """Send current bed availability to specific user"""
        try:
            bed_data = self._get_current_bed_availability()
            emit('bed_availability_update', {
                'timestamp': datetime.utcnow().isoformat(),
                'data': bed_data
            })
        except Exception as e:
            logging.error(f"Error sending bed availability: {e}")
    
    def _get_current_bed_availability(self) -> List[Dict]:
        """Get current bed availability from database"""
        # This would integrate with your database model
        # For now, returning mock data structure
        try:
            from project.main import Hospitaldata
            
            hospitals = Hospitaldata.query.all()
            bed_data = []
            
            for hospital in hospitals:
                bed_data.append({
                    'hcode': hospital.hcode,
                    'hname': hospital.hname,
                    'beds': {
                        'normal': hospital.normalbed,
                        'hicu': hospital.hicubed,
                        'icu': hospital.icubed,
                        'ventilator': hospital.vbed
                    },
                    'total_available': (
                        hospital.normalbed + 
                        hospital.hicubed + 
                        hospital.icubed + 
                        hospital.vbed
                    ),
                    'last_updated': datetime.utcnow().isoformat()
                })
            
            return bed_data
        except Exception as e:
            logging.error(f"Error fetching bed data: {e}")
            return []
    
    def _broadcast_bed_update(self, hospital_code: str, update_data: Dict):
        """Broadcast bed availability updates"""
        try:
            # Validate update data
            if not self._validate_bed_update(update_data):
                emit('error', {'message': 'Invalid bed update data'})
                return
            
            # Update database (integrate with your models)
            self._update_hospital_beds(hospital_code, update_data)
            
            # Broadcast to all interested parties
            broadcast_data = {
                'hospital_code': hospital_code,
                'timestamp': datetime.utcnow().isoformat(),
                'updates': update_data,
                'source': 'hospital_staff'
            }
            
            # Send to hospital staff
            self.socketio.emit('bed_update', broadcast_data, room=f"hospital_{hospital_code}")
            
            # Send to public subscribers
            self.socketio.emit('bed_availability_changed', broadcast_data, room=f"hospital_{hospital_code}_public")
            
            # Send to admin room
            self.socketio.emit('bed_update', broadcast_data, room='admin_room')
            
            # Store in Redis for persistence
            if self.redis_client:
                self._store_bed_update_history(hospital_code, broadcast_data)
            
            logging.info(f"Bed update broadcast for hospital {hospital_code}")
            
        except Exception as e:
            logging.error(f"Error broadcasting bed update: {e}")
            emit('error', {'message': 'Failed to update bed availability'})
    
    def _validate_bed_update(self, data: Dict) -> bool:
        """Validate bed update data"""
        required_fields = ['bed_type', 'action', 'count']
        
        if not all(field in data for field in required_fields):
            return False
        
        if data['bed_type'] not in ['normal', 'hicu', 'icu', 'ventilator']:
            return False
        
        if data['action'] not in ['increase', 'decrease', 'set']:
            return False
        
        try:
            count = int(data['count'])
            if count < 0:
                return False
        except (ValueError, TypeError):
            return False
        
        return True
    
    def _update_hospital_beds(self, hospital_code: str, update_data: Dict):
        """Update hospital bed count in database"""
        try:
            from project.main import Hospitaldata, db
            
            hospital = Hospitaldata.query.filter_by(hcode=hospital_code).first()
            if not hospital:
                raise ValueError(f"Hospital {hospital_code} not found")
            
            bed_type = update_data['bed_type']
            action = update_data['action']
            count = int(update_data['count'])
            
            # Map bed types to database fields
            bed_field_map = {
                'normal': 'normalbed',
                'hicu': 'hicubed',
                'icu': 'icubed',
                'ventilator': 'vbed'
            }
            
            field_name = bed_field_map[bed_type]
            current_value = getattr(hospital, field_name)
            
            if action == 'increase':
                new_value = current_value + count
            elif action == 'decrease':
                new_value = max(0, current_value - count)
            else:  # set
                new_value = count
            
            setattr(hospital, field_name, new_value)
            db.session.commit()
            
            # Log the change
            self._log_bed_change(hospital_code, bed_type, current_value, new_value, action)
            
        except Exception as e:
            logging.error(f"Error updating hospital beds: {e}")
            raise
    
    def _log_bed_change(self, hospital_code: str, bed_type: str, old_value: int, new_value: int, action: str):
        """Log bed changes for audit trail"""
        try:
            from project.main import Trig, db
            
            # Create trigger log entry
            log_entry = Trig(
                hcode=hospital_code,
                normalbed=0,  # Will be updated with actual values
                hicubed=0,
                icubed=0,
                vbed=0,
                querys=f"{action}_{bed_type}",
                date=datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            )
            
            # Set the specific bed type value
            if bed_type == 'normal':
                log_entry.normalbed = new_value
            elif bed_type == 'hicu':
                log_entry.hicubed = new_value
            elif bed_type == 'icu':
                log_entry.icubed = new_value
            elif bed_type == 'ventilator':
                log_entry.vbed = new_value
            
            db.session.add(log_entry)
            db.session.commit()
            
        except Exception as e:
            logging.error(f"Error logging bed change: {e}")
    
    def _store_bed_update_history(self, hospital_code: str, update_data: Dict):
        """Store bed update history in Redis"""
        try:
            key = f"bed_updates:{hospital_code}"
            self.redis_client.lpush(key, json.dumps(update_data))
            self.redis_client.ltrim(key, 0, 99)  # Keep last 100 updates
            self.redis_client.expire(key, 86400 * 7)  # Keep for 7 days
        except Exception as e:
            logging.error(f"Error storing bed update history: {e}")
    
    def _broadcast_emergency_alert(self, alert_data: Dict):
        """Broadcast emergency alerts to all users"""
        try:
            broadcast_data = {
                'type': 'emergency_alert',
                'message': alert_data.get('message', 'Emergency alert'),
                'priority': alert_data.get('priority', 'high'),
                'timestamp': datetime.utcnow().isoformat(),
                'source': getattr(current_user, 'hcode', 'system')
            }
            
            # Broadcast to all connected users
            self.socketio.emit('emergency_alert', broadcast_data, room='all_users')
            
            logging.warning(f"Emergency alert broadcast: {broadcast_data}")
            
        except Exception as e:
            logging.error(f"Error broadcasting emergency alert: {e}")
    
    def send_notification(self, user_ids: List[str], notification: Dict):
        """Send notification to specific users"""
        try:
            notification_data = {
                'type': 'notification',
                'title': notification.get('title', 'Notification'),
                'message': notification.get('message', ''),
                'timestamp': datetime.utcnow().isoformat(),
                'priority': notification.get('priority', 'normal')
            }
            
            # Send to specific users if they're connected
            for sid, user_info in self.connected_users.items():
                if user_info['user_id'] in user_ids:
                    self.socketio.emit('notification', notification_data, room=sid)
            
            # Store notification for offline users
            if self.redis_client:
                for user_id in user_ids:
                    key = f"notifications:{user_id}"
                    self.redis_client.lpush(key, json.dumps(notification_data))
                    self.redis_client.ltrim(key, 0, 49)  # Keep last 50 notifications
                    self.redis_client.expire(key, 86400 * 30)  # Keep for 30 days
            
        except Exception as e:
            logging.error(f"Error sending notification: {e}")
    
    def get_connected_users_count(self) -> Dict:
        """Get count of connected users by type"""
        counts = {
            'total': len(self.connected_users),
            'patients': 0,
            'hospitals': 0,
            'admins': 0
        }
        
        for user_info in self.connected_users.values():
            user_type = user_info.get('user_type', 'patient')
            if user_type in counts:
                counts[user_type] += 1
        
        return counts
    
    def get_hospital_activity(self, hospital_code: str) -> Dict:
        """Get activity statistics for a hospital"""
        if not self.redis_client:
            return {}
        
        try:
            key = f"bed_updates:{hospital_code}"
            recent_updates = self.redis_client.lrange(key, 0, 9)  # Last 10 updates
            
            activity_data = {
                'recent_updates_count': len(recent_updates),
                'connected_staff': sum(1 for room_code in self.hospital_rooms.values() 
                                     if room_code == hospital_code),
                'last_activity': None
            }
            
            if recent_updates:
                latest_update = json.loads(recent_updates[0])
                activity_data['last_activity'] = latest_update.get('timestamp')
            
            return activity_data
        except Exception as e:
            logging.error(f"Error getting hospital activity: {e}")
            return {}

# Create global instance
realtime_service = RealTimeService()
