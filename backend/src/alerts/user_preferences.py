"""
User preferences module
Manages user notification preferences and alert filtering
"""
from typing import Dict, List, Optional
from datetime import time
from pydantic import BaseModel

from src.utils.logger import logger


class QuietHours(BaseModel):
    """Quiet hours configuration"""
    enabled: bool = False
    start_time: str = "22:00"  # HH:MM format
    end_time: str = "08:00"    # HH:MM format
    skip_low_alerts: bool = True  # Skip LOW severity during quiet hours
    allow_high_alerts: bool = True  # Always allow HIGH severity


class NotificationPreferences(BaseModel):
    """User notification preferences"""
    user_id: str
    email_enabled: bool = True
    email_address: str = ""
    
    # Alert filtering
    alert_severity_filter: List[str] = ["LOW", "MEDIUM", "HIGH"]  # Which severities to notify
    alert_type_filter: List[str] = []  # Empty = all types
    location_filter: List[int] = []    # Empty = all locations
    
    # Notification frequency
    batch_notifications: bool = False
    batch_interval_minutes: int = 15
    
    # Quiet hours
    quiet_hours: QuietHours = QuietHours()
    
    # Other
    acknowledge_required: bool = False
    notification_history: bool = True


class UserPreferencesManager:
    """Manages user notification preferences"""
    
    def __init__(self):
        self.preferences: Dict[str, NotificationPreferences] = {}
        self.default_preferences = NotificationPreferences(user_id="default")
    
    def create_user_preferences(self, user_id: str, **kwargs) -> NotificationPreferences:
        """
        Create or update user preferences
        
        Args:
            user_id: User identifier
            **kwargs: Preference fields to set
            
        Returns:
            Updated preferences
        """
        try:
            prefs = NotificationPreferences(user_id=user_id, **kwargs)
            self.preferences[user_id] = prefs
            logger.info(f"✅ Created preferences for user {user_id}")
            return prefs
            
        except Exception as e:
            logger.error(f"Error creating preferences for {user_id}: {e}")
            return self.default_preferences
    
    def get_user_preferences(self, user_id: str) -> NotificationPreferences:
        """
        Get user preferences
        
        Args:
            user_id: User identifier
            
        Returns:
            User preferences or defaults
        """
        if user_id not in self.preferences:
            return self.default_preferences
        return self.preferences[user_id]
    
    def update_preferences(self, user_id: str, **kwargs) -> NotificationPreferences:
        """
        Update user preferences
        
        Args:
            user_id: User identifier
            **kwargs: Fields to update
            
        Returns:
            Updated preferences
        """
        prefs = self.get_user_preferences(user_id)
        
        try:
            for key, value in kwargs.items():
                if hasattr(prefs, key):
                    setattr(prefs, key, value)
            
            self.preferences[user_id] = prefs
            logger.info(f"✅ Updated preferences for user {user_id}")
            return prefs
            
        except Exception as e:
            logger.error(f"Error updating preferences for {user_id}: {e}")
            return prefs
    
    def should_notify_alert(self, user_id: str, 
                           alert_severity: str,
                           alert_type: str = None,
                           location_id: int = None) -> bool:
        """
        Check if user should be notified about an alert
        
        Args:
            user_id: User identifier
            alert_severity: Alert severity level
            alert_type: Alert type
            location_id: Location ID
            
        Returns:
            True if user should be notified
        """
        prefs = self.get_user_preferences(user_id)
        
        # Check if notifications enabled
        if not prefs.email_enabled:
            return False
        
        # Check severity filter
        if alert_severity not in prefs.alert_severity_filter:
            return False
        
        # Check type filter (empty = all types)
        if prefs.alert_type_filter and alert_type not in prefs.alert_type_filter:
            return False
        
        # Check location filter (empty = all locations)
        if prefs.location_filter and location_id not in prefs.location_filter:
            return False
        
        # Check quiet hours
        if prefs.quiet_hours.enabled:
            current_time = datetime.now().time()
            start_time = datetime.strptime(prefs.quiet_hours.start_time, "%H:%M").time()
            end_time = datetime.strptime(prefs.quiet_hours.end_time, "%H:%M").time()
            
            # Check if current time is in quiet hours
            if start_time <= end_time:
                in_quiet_hours = start_time <= current_time <= end_time
            else:
                # Quiet hours cross midnight
                in_quiet_hours = current_time >= start_time or current_time <= end_time
            
            if in_quiet_hours:
                # Skip LOW alerts during quiet hours
                if prefs.quiet_hours.skip_low_alerts and alert_severity == "LOW":
                    return False
                # Always allow HIGH severity
                if prefs.quiet_hours.allow_high_alerts and alert_severity == "HIGH":
                    return True
                if prefs.quiet_hours.skip_low_alerts:
                    return False
        
        return True
    
    def set_quiet_hours(self, user_id: str, 
                       enabled: bool,
                       start_time: str,
                       end_time: str,
                       skip_low: bool = True,
                       allow_high: bool = True):
        """
        Set quiet hours for a user
        
        Args:
            user_id: User identifier
            enabled: Enable quiet hours
            start_time: Start time (HH:MM format)
            end_time: End time (HH:MM format)
            skip_low: Skip LOW severity during quiet hours
            allow_high: Allow HIGH severity during quiet hours
        """
        prefs = self.get_user_preferences(user_id)
        
        try:
            prefs.quiet_hours = QuietHours(
                enabled=enabled,
                start_time=start_time,
                end_time=end_time,
                skip_low_alerts=skip_low,
                allow_high_alerts=allow_high
            )
            self.preferences[user_id] = prefs
            logger.info(f"✅ Updated quiet hours for {user_id}")
            
        except Exception as e:
            logger.error(f"Error setting quiet hours: {e}")
    
    def get_preferences_dict(self, user_id: str) -> Dict:
        """Get user preferences as dictionary"""
        prefs = self.get_user_preferences(user_id)
        return prefs.dict()


# Add missing import
from datetime import datetime

# Global instance
user_preferences_manager: Optional[UserPreferencesManager] = None


def get_user_preferences_manager() -> UserPreferencesManager:
    """Get or create global user preferences manager"""
    global user_preferences_manager
    if user_preferences_manager is None:
        user_preferences_manager = UserPreferencesManager()
    return user_preferences_manager
