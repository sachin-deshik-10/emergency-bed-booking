"""
Analytics and Reporting Service for Emergency Hospital Bed Booking System

This service provides comprehensive analytics, reporting, and data visualization
capabilities for hospital administrators and system operators.

Features:
- Hospital bed utilization analytics
- Peak usage tracking and predictions
- Emergency response metrics
- User activity analytics
- Performance monitoring
- Custom report generation
- Data export capabilities
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from plotly.utils import PlotlyJSONEncoder
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import io
import base64
from dataclasses import dataclass
from enum import Enum

class ReportType(Enum):
    UTILIZATION = "utilization"
    EMERGENCY_RESPONSE = "emergency_response"
    USER_ACTIVITY = "user_activity"
    PERFORMANCE = "performance"
    CAPACITY_PLANNING = "capacity_planning"

@dataclass
class AnalyticsMetric:
    name: str
    value: float
    unit: str
    trend: str  # 'up', 'down', 'stable'
    change_percent: float
    description: str

class AnalyticsService:
    """Advanced analytics and reporting service"""
    
    def __init__(self, db_session=None):
        """Initialize analytics service with database session"""
        self.db = db_session
        self.cache_timeout = 300  # 5 minutes cache
        self._cache = {}
        
    def get_hospital_utilization_metrics(self, hospital_id: Optional[int] = None, 
                                       days: int = 30) -> Dict:
        """
        Calculate comprehensive hospital bed utilization metrics
        
        Args:
            hospital_id: Specific hospital ID (None for all hospitals)
            days: Number of days to analyze
            
        Returns:
            Dictionary containing utilization metrics and trends
        """
        cache_key = f"utilization_{hospital_id}_{days}"
        if self._is_cached(cache_key):
            return self._cache[cache_key]
            
        try:
            # Get historical bed booking data
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Simulate data for demonstration (replace with real database queries)
            metrics = self._calculate_utilization_metrics(hospital_id, start_date, end_date)
            
            self._cache[cache_key] = metrics
            return metrics
            
        except Exception as e:
            return {"error": f"Failed to calculate utilization metrics: {str(e)}"}
    
    def _calculate_utilization_metrics(self, hospital_id: Optional[int], 
                                     start_date: datetime, end_date: datetime) -> Dict:
        """Calculate detailed utilization metrics"""
        
        # Simulate realistic hospital data
        np.random.seed(42)  # For consistent results
        days = (end_date - start_date).days
        
        # Generate sample bed utilization data
        dates = pd.date_range(start=start_date, end=end_date, freq='H')
        base_utilization = 0.7  # 70% base utilization
        
        # Add realistic patterns (higher during day, peaks during emergencies)
        hourly_pattern = np.sin(np.arange(len(dates)) * 2 * np.pi / 24) * 0.1
        random_variation = np.random.normal(0, 0.05, len(dates))
        emergency_spikes = np.random.exponential(0.02, len(dates)) * (np.random.random(len(dates)) > 0.95)
        
        utilization_rates = base_utilization + hourly_pattern + random_variation + emergency_spikes
        utilization_rates = np.clip(utilization_rates, 0, 1)  # Keep between 0 and 1
        
        df = pd.DataFrame({
            'timestamp': dates,
            'utilization_rate': utilization_rates,
            'occupied_beds': (utilization_rates * 100).astype(int),
            'total_beds': 100,
            'available_beds': (100 - (utilization_rates * 100)).astype(int)
        })
        
        # Calculate key metrics
        current_utilization = utilization_rates[-1]
        avg_utilization = np.mean(utilization_rates)
        peak_utilization = np.max(utilization_rates)
        min_utilization = np.min(utilization_rates)
        
        # Calculate trends (compare last 7 days to previous 7 days)
        if days >= 14:
            recent_avg = np.mean(utilization_rates[-7*24:])  # Last 7 days (hourly data)
            previous_avg = np.mean(utilization_rates[-14*24:-7*24])  # Previous 7 days
            trend_change = ((recent_avg - previous_avg) / previous_avg) * 100
        else:
            trend_change = 0
            
        # Peak hours analysis
        df['hour'] = df['timestamp'].dt.hour
        hourly_avg = df.groupby('hour')['utilization_rate'].mean()
        peak_hours = hourly_avg.nlargest(3).index.tolist()
        
        # Weekly patterns
        df['day_of_week'] = df['timestamp'].dt.day_name()
        daily_avg = df.groupby('day_of_week')['utilization_rate'].mean()
        
        return {
            'current_utilization': round(current_utilization * 100, 1),
            'average_utilization': round(avg_utilization * 100, 1),
            'peak_utilization': round(peak_utilization * 100, 1),
            'minimum_utilization': round(min_utilization * 100, 1),
            'trend_change_percent': round(trend_change, 1),
            'trend_direction': 'up' if trend_change > 2 else 'down' if trend_change < -2 else 'stable',
            'peak_hours': peak_hours,
            'busiest_days': daily_avg.nlargest(3).to_dict(),
            'data_points': len(df),
            'analysis_period': f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
            'metrics': [
                AnalyticsMetric(
                    name="Current Occupancy",
                    value=current_utilization * 100,
                    unit="%",
                    trend='up' if trend_change > 0 else 'down' if trend_change < 0 else 'stable',
                    change_percent=trend_change,
                    description="Current bed utilization rate"
                ),
                AnalyticsMetric(
                    name="Average Utilization",
                    value=avg_utilization * 100,
                    unit="%",
                    trend='stable',
                    change_percent=0,
                    description=f"Average utilization over {days} days"
                ),
                AnalyticsMetric(
                    name="Peak Capacity",
                    value=peak_utilization * 100,
                    unit="%",
                    trend='neutral',
                    change_percent=0,
                    description="Maximum utilization reached"
                )
            ]
        }
    
    def generate_utilization_chart(self, hospital_id: Optional[int] = None, 
                                 days: int = 7) -> str:
        """
        Generate interactive utilization chart using Plotly
        
        Returns:
            JSON string containing Plotly chart data
        """
        try:
            # Get utilization data
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Generate sample data (replace with real database queries)
            dates = pd.date_range(start=start_date, end=end_date, freq='H')
            np.random.seed(42)
            
            base_utilization = 0.7
            hourly_pattern = np.sin(np.arange(len(dates)) * 2 * np.pi / 24) * 0.1
            random_variation = np.random.normal(0, 0.05, len(dates))
            utilization_rates = base_utilization + hourly_pattern + random_variation
            utilization_rates = np.clip(utilization_rates, 0, 1) * 100
            
            # Create interactive Plotly chart
            fig = go.Figure()
            
            # Add utilization line
            fig.add_trace(go.Scatter(
                x=dates,
                y=utilization_rates,
                mode='lines',
                name='Bed Utilization',
                line=dict(color='#3498db', width=2),
                hovertemplate='<b>%{x}</b><br>Utilization: %{y:.1f}%<extra></extra>'
            ))
            
            # Add critical threshold line
            fig.add_hline(y=90, line_dash="dash", line_color="red", 
                         annotation_text="Critical Threshold (90%)")
            
            # Add optimal threshold line
            fig.add_hline(y=75, line_dash="dash", line_color="orange", 
                         annotation_text="Optimal Threshold (75%)")
            
            # Update layout
            fig.update_layout(
                title=f'Hospital Bed Utilization - Last {days} Days',
                xaxis_title='Date/Time',
                yaxis_title='Utilization (%)',
                template='plotly_white',
                height=400,
                showlegend=True,
                hovermode='x unified'
            )
            
            return json.dumps(fig, cls=PlotlyJSONEncoder)
            
        except Exception as e:
            return json.dumps({"error": f"Failed to generate chart: {str(e)}"})
    
    def get_emergency_response_analytics(self, days: int = 30) -> Dict:
        """
        Analyze emergency response metrics and performance
        
        Returns:
            Dictionary containing emergency response analytics
        """
        try:
            # Simulate emergency response data
            np.random.seed(42)
            
            # Generate emergency incidents
            num_incidents = np.random.poisson(50)  # Average 50 incidents per month
            response_times = np.random.gamma(2, 15)  # Gamma distribution for response times
            
            # Calculate metrics
            avg_response_time = np.mean(response_times)
            median_response_time = np.median(response_times)
            response_time_90th = np.percentile(response_times, 90)
            
            # Response time categories
            fast_responses = np.sum(response_times <= 10)  # Under 10 minutes
            medium_responses = np.sum((response_times > 10) & (response_times <= 30))
            slow_responses = np.sum(response_times > 30)
            
            # Peak emergency hours
            emergency_hours = np.random.choice(24, num_incidents, 
                                             p=self._get_emergency_hour_probabilities())
            peak_hours = pd.Series(emergency_hours).value_counts().head(3)
            
            return {
                'total_emergencies': num_incidents,
                'average_response_time': round(avg_response_time, 1),
                'median_response_time': round(median_response_time, 1),
                'response_time_90th_percentile': round(response_time_90th, 1),
                'fast_responses': int(fast_responses),
                'medium_responses': int(medium_responses),
                'slow_responses': int(slow_responses),
                'response_rate_sla': round((fast_responses / num_incidents) * 100, 1),
                'peak_emergency_hours': peak_hours.to_dict(),
                'analysis_period_days': days
            }
            
        except Exception as e:
            return {"error": f"Failed to analyze emergency response: {str(e)}"}
    
    def _get_emergency_hour_probabilities(self) -> np.ndarray:
        """Get realistic probability distribution for emergency hours"""
        # Higher probability during evening/night and early morning
        probs = np.ones(24)
        probs[18:24] *= 1.5  # Evening spike
        probs[0:6] *= 1.3    # Early morning spike  
        probs[8:17] *= 0.8   # Lower during business hours
        return probs / np.sum(probs)
    
    def generate_capacity_forecast(self, hospital_id: Optional[int] = None, 
                                 forecast_days: int = 30) -> Dict:
        """
        Generate capacity planning forecast using trend analysis
        
        Returns:
            Dictionary containing forecast data and recommendations
        """
        try:
            # Get historical data for forecasting
            historical_data = self.get_hospital_utilization_metrics(hospital_id, 90)
            
            # Simulate forecast (in production, use time series forecasting)
            current_utilization = historical_data.get('current_utilization', 70)
            trend_change = historical_data.get('trend_change_percent', 0)
            
            # Generate forecast points
            forecast_dates = pd.date_range(
                start=datetime.now(),
                periods=forecast_days,
                freq='D'
            )
            
            # Simple linear trend with seasonal variation
            base_forecast = current_utilization
            daily_trend = trend_change / 30  # Daily trend rate
            seasonal_variation = np.sin(np.arange(forecast_days) * 2 * np.pi / 7) * 3  # Weekly pattern
            
            forecast_values = []
            for i in range(forecast_days):
                value = base_forecast + (daily_trend * i) + seasonal_variation[i]
                # Add some noise
                value += np.random.normal(0, 2)
                value = max(0, min(100, value))  # Clamp between 0-100%
                forecast_values.append(value)
            
            # Identify capacity warnings
            warnings = []
            critical_days = sum(1 for v in forecast_values if v > 90)
            if critical_days > 5:
                warnings.append(f"Expected {critical_days} days above 90% capacity")
            
            peak_forecast = max(forecast_values)
            if peak_forecast > 95:
                warnings.append(f"Peak capacity forecast: {peak_forecast:.1f}%")
            
            # Recommendations
            recommendations = []
            if current_utilization > 80:
                recommendations.append("Consider increasing bed capacity")
            if trend_change > 5:
                recommendations.append("Monitor upward trend closely")
            if critical_days > 0:
                recommendations.append("Prepare overflow protocols")
                
            return {
                'forecast_period_days': forecast_days,
                'forecast_dates': [d.strftime('%Y-%m-%d') for d in forecast_dates],
                'forecast_values': [round(v, 1) for v in forecast_values],
                'peak_forecast': round(peak_forecast, 1),
                'average_forecast': round(np.mean(forecast_values), 1),
                'critical_days_count': critical_days,
                'warnings': warnings,
                'recommendations': recommendations,
                'confidence_level': 75  # Simulation confidence
            }
            
        except Exception as e:
            return {"error": f"Failed to generate forecast: {str(e)}"}
    
    def export_analytics_report(self, report_type: ReportType, 
                               format: str = 'json', **kwargs) -> str:
        """
        Export comprehensive analytics report in specified format
        
        Args:
            report_type: Type of report to generate
            format: Export format ('json', 'csv', 'pdf')
            **kwargs: Additional parameters specific to report type
            
        Returns:
            Serialized report data or file path
        """
        try:
            report_data = {}
            
            if report_type == ReportType.UTILIZATION:
                report_data = self.get_hospital_utilization_metrics(
                    kwargs.get('hospital_id'),
                    kwargs.get('days', 30)
                )
                
            elif report_type == ReportType.EMERGENCY_RESPONSE:
                report_data = self.get_emergency_response_analytics(
                    kwargs.get('days', 30)
                )
                
            elif report_type == ReportType.CAPACITY_PLANNING:
                report_data = self.generate_capacity_forecast(
                    kwargs.get('hospital_id'),
                    kwargs.get('forecast_days', 30)
                )
            
            # Add metadata
            report_data['report_metadata'] = {
                'generated_at': datetime.now().isoformat(),
                'report_type': report_type.value,
                'format': format,
                'parameters': kwargs
            }
            
            if format.lower() == 'json':
                return json.dumps(report_data, indent=2, default=str)
            elif format.lower() == 'csv':
                return self._export_to_csv(report_data)
            else:
                return json.dumps(report_data, default=str)
                
        except Exception as e:
            return json.dumps({"error": f"Failed to export report: {str(e)}"})
    
    def _export_to_csv(self, data: Dict) -> str:
        """Convert report data to CSV format"""
        try:
            # Flatten nested data for CSV export
            flat_data = []
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    flat_data.append({
                        'metric': key,
                        'value': str(value),
                        'type': type(value).__name__
                    })
                else:
                    flat_data.append({
                        'metric': key,
                        'value': value,
                        'type': type(value).__name__
                    })
            
            df = pd.DataFrame(flat_data)
            return df.to_csv(index=False)
            
        except Exception as e:
            return f"Error converting to CSV: {str(e)}"
    
    def _is_cached(self, cache_key: str) -> bool:
        """Check if data is cached and still valid"""
        if cache_key not in self._cache:
            return False
        
        # Simple time-based cache invalidation
        cache_time = getattr(self._cache[cache_key], '_cache_time', None)
        if cache_time is None:
            return False
            
        return (datetime.now() - cache_time).total_seconds() < self.cache_timeout
    
    def get_real_time_dashboard_data(self) -> Dict:
        """
        Get real-time dashboard data for live monitoring
        
        Returns:
            Dictionary containing current system status and metrics
        """
        try:
            current_time = datetime.now()
            
            # Get current metrics (simulated)
            utilization_data = self.get_hospital_utilization_metrics(days=1)
            emergency_data = self.get_emergency_response_analytics(days=1)
            
            # System health metrics
            system_health = {
                'api_response_time': round(np.random.normal(150, 30), 1),  # ms
                'database_connections': np.random.randint(5, 20),
                'active_users': np.random.randint(50, 200),
                'websocket_connections': np.random.randint(10, 100),
                'server_cpu_usage': round(np.random.normal(45, 15), 1),
                'memory_usage': round(np.random.normal(60, 20), 1)
            }
            
            # Alerts and notifications
            alerts = []
            if utilization_data.get('current_utilization', 0) > 90:
                alerts.append({
                    'level': 'critical',
                    'message': 'Hospital capacity above 90%',
                    'timestamp': current_time.isoformat()
                })
            
            if system_health['server_cpu_usage'] > 80:
                alerts.append({
                    'level': 'warning',
                    'message': 'High server CPU usage',
                    'timestamp': current_time.isoformat()
                })
            
            return {
                'timestamp': current_time.isoformat(),
                'utilization_summary': {
                    'current': utilization_data.get('current_utilization', 0),
                    'trend': utilization_data.get('trend_direction', 'stable'),
                    'peak_today': utilization_data.get('peak_utilization', 0)
                },
                'emergency_summary': {
                    'total_today': emergency_data.get('total_emergencies', 0),
                    'avg_response_time': emergency_data.get('average_response_time', 0),
                    'sla_compliance': emergency_data.get('response_rate_sla', 0)
                },
                'system_health': system_health,
                'alerts': alerts,
                'status': 'operational' if len(alerts) == 0 else 'degraded' if any(a['level'] == 'warning' for a in alerts) else 'critical'
            }
            
        except Exception as e:
            return {
                'error': f"Failed to get dashboard data: {str(e)}",
                'timestamp': datetime.now().isoformat(),
                'status': 'error'
            }

# Global analytics service instance
analytics_service = AnalyticsService()
