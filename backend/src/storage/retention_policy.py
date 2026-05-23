"""
Data retention policy module
Defines and manages data retention rules per data type
"""
from typing import Dict
from pydantic import BaseModel

from src.utils.logger import logger


class RetentionPolicy(BaseModel):
    """Data retention policy configuration"""
    
    # Raw weather data retention (15-minute readings)
    weather_data_days: int = 30
    
    # Processed metrics retention (hourly/daily/weekly aggregations)
    hourly_metrics_days: int = 90
    daily_metrics_days: int = 180
    weekly_metrics_days: int = 365
    
    # Alerts retention
    active_alerts_days: int = 30
    resolved_alerts_days: int = 60
    
    # System metrics retention
    system_metrics_days: int = 30
    
    # Archives retention
    archive_retention_days: int = 90
    max_archives_to_keep: int = 12


class RetentionPolicyManager:
    """Manages data retention policies"""
    
    def __init__(self):
        self.policy = RetentionPolicy()
        logger.info("📋 Data Retention Policy initialized")
        self._log_policy()
    
    def _log_policy(self):
        """Log current retention policy"""
        logger.info("📋 Current Data Retention Policy:")
        logger.info(f"   Weather Data: {self.policy.weather_data_days} days")
        logger.info(f"   Hourly Metrics: {self.policy.hourly_metrics_days} days")
        logger.info(f"   Daily Metrics: {self.policy.daily_metrics_days} days")
        logger.info(f"   Weekly Metrics: {self.policy.weekly_metrics_days} days")
        logger.info(f"   Active Alerts: {self.policy.active_alerts_days} days")
        logger.info(f"   Resolved Alerts: {self.policy.resolved_alerts_days} days")
        logger.info(f"   System Metrics: {self.policy.system_metrics_days} days")
        logger.info(f"   Archives: {self.policy.archive_retention_days} days")
    
    def update_policy(self, **kwargs):
        """
        Update retention policy settings
        
        Args:
            **kwargs: Policy fields to update
        """
        try:
            for key, value in kwargs.items():
                if hasattr(self.policy, key):
                    setattr(self.policy, key, value)
                    logger.info(f"✅ Updated {key} to {value} days")
                else:
                    logger.warning(f"Unknown policy field: {key}")
            
            self._log_policy()
            
        except Exception as e:
            logger.error(f"Error updating retention policy: {e}")
    
    def get_retention_days(self, data_type: str) -> int:
        """
        Get retention days for specific data type
        
        Args:
            data_type: Type of data (weather, hourly_metrics, etc.)
            
        Returns:
            Days to retain
        """
        type_mapping = {
            "weather": self.policy.weather_data_days,
            "weather_data": self.policy.weather_data_days,
            "hourly_metrics": self.policy.hourly_metrics_days,
            "hourly": self.policy.hourly_metrics_days,
            "daily_metrics": self.policy.daily_metrics_days,
            "daily": self.policy.daily_metrics_days,
            "weekly_metrics": self.policy.weekly_metrics_days,
            "weekly": self.policy.weekly_metrics_days,
            "active_alerts": self.policy.active_alerts_days,
            "alerts": self.policy.resolved_alerts_days,
            "system_metrics": self.policy.system_metrics_days,
            "archives": self.policy.archive_retention_days
        }
        
        days = type_mapping.get(data_type.lower(), None)
        if days is None:
            logger.warning(f"Unknown data type: {data_type}")
            return 30  # Default to 30 days
        
        return days
    
    def get_policy_dict(self) -> Dict:
        """
        Get policy as dictionary
        
        Returns:
            Dictionary representation of policy
        """
        return self.policy.dict()
    
    def validate_policy(self) -> bool:
        """
        Validate retention policy settings
        
        Returns:
            True if valid
        """
        try:
            # All retention days should be positive
            for key, value in self.policy.dict().items():
                if not isinstance(value, int) or value <= 0:
                    logger.error(f"Invalid retention value for {key}: {value}")
                    return False
            
            # Weekly should be longer than daily
            if self.policy.weekly_metrics_days < self.policy.daily_metrics_days:
                logger.warning("Weekly metrics retention is less than daily")
            
            # Daily should be longer than hourly
            if self.policy.daily_metrics_days < self.policy.hourly_metrics_days:
                logger.warning("Daily metrics retention is less than hourly")
            
            logger.info("✅ Retention policy validated")
            return True
            
        except Exception as e:
            logger.error(f"Error validating retention policy: {e}")
            return False


# Global instance
retention_policy_manager: RetentionPolicyManager = None


def get_retention_policy_manager() -> RetentionPolicyManager:
    """Get or create global retention policy manager"""
    global retention_policy_manager
    if retention_policy_manager is None:
        retention_policy_manager = RetentionPolicyManager()
    return retention_policy_manager
