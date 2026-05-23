"""
Application configuration module
Loads settings from .env file using Pydantic Settings
"""
from typing import List
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # App Configuration
    app_name: str = "Real-Time Weather Pipeline"
    app_env: str = "development"
    debug: bool = True

    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_reload: bool = True

    # Weather API Configuration
    weather_api_provider: str = "open-meteo"
    weather_api_key: str = ""
    weather_api_base_url: str = "https://api.open-meteo.com/v1"

    # Database Configuration
    database_url: str = "sqlite:///./weather_pipeline.db"

    # Authentication Configuration
    secret_key: str = "your-secret-key-change-in-production-environment"
    jwt_algorithm: str = "HS256"
    access_token_expire_hours: int = 24

    # Data Collection
    fetch_interval_minutes: int = 15
    locations: str = "Delhi,Mumbai,Bangalore,Chennai,Kolkata"

    # Alert Configuration
    alert_enabled: bool = True
    temp_alert_high: int = 35
    temp_alert_low: int = -10
    wind_alert_threshold: int = 50
    humidity_alert_high: int = 95
    humidity_alert_low: int = 5

    # Data Processing Configuration
    processing_enabled: bool = True
    aggregation_interval_hours: int = 1
    anomaly_detection_enabled: bool = True
    alert_on_anomaly: bool = True
    anomaly_detection_method: str = "zscore"  # zscore or isolation_forest
    anomaly_threshold: float = 3.0

    # Storage & Retention Configuration
    storage_enabled: bool = True
    weather_data_retention_days: int = 30
    hourly_metrics_retention_days: int = 90
    daily_metrics_retention_days: int = 180
    weekly_metrics_retention_days: int = 365
    alerts_retention_days: int = 60
    system_metrics_retention_days: int = 30
    archive_retention_days: int = 90
    max_archives_to_keep: int = 12
    archive_directory: str = "archives"
    enable_automatic_cleanup: bool = True
    enable_automatic_archiving: bool = True

    # Logging
    log_level: str = "INFO"
    log_file: str = "logs/weather_pipeline.log"

    # Email Configuration
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    alert_email_to: str = ""

    # Alert System Configuration
    alert_system_enabled: bool = False
    alert_notification_enabled: bool = False
    alert_escalation_enabled: bool = False
    alert_escalation_enabled: bool = True
    alert_batch_notifications: bool = False
    alert_batch_interval_minutes: int = 15
    
    # Escalation Rules
    alert_low_initial_delay_hours: int = 24
    alert_low_escalation_delay_hours: int = 48
    alert_low_max_escalations: int = 0
    
    alert_medium_initial_delay_hours: int = 2
    alert_medium_escalation_delay_hours: int = 4
    alert_medium_max_escalations: int = 2
    
    alert_high_initial_delay_hours: int = 0
    alert_high_escalation_delay_hours: int = 1
    alert_high_max_escalations: int = 5
    
    # Quiet Hours
    quiet_hours_enabled: bool = False
    quiet_hours_start: str = "22:00"
    quiet_hours_end: str = "08:00"
    quiet_hours_skip_low: bool = True
    quiet_hours_allow_high: bool = True

    # Data Retention
    data_retention_days: int = 30

    # Phase 1.7: API Enhancement Settings
    
    # Webhook Configuration
    webhooks_enabled: bool = True
    webhook_max_retries: int = 3
    webhook_retry_delay_seconds: int = 60
    
    # Export Configuration
    export_enabled: bool = True
    export_max_records: int = 50000
    export_formats: str = "json,csv,jsonl"
    
    # Real-time Configuration
    realtime_enabled: bool = True
    websocket_max_connections: int = 1000
    websocket_message_queue_size: int = 100
    
    # Advanced Filtering
    filtering_enabled: bool = True
    filter_max_conditions: int = 50
    
    # Phase 1.8: Monitoring & Logging Settings
    
    # Performance Monitoring
    performance_monitoring_enabled: bool = True
    metrics_history_limit: int = 100000
    metrics_window_size_seconds: int = 3600
    metric_alert_cpu_threshold: float = 75.0
    metric_alert_memory_threshold: float = 70.0
    metric_alert_request_time_threshold: float = 1.0
    
    # Health Checking
    health_check_enabled: bool = True
    health_check_timeout_seconds: int = 5
    health_check_interval_seconds: int = 60
    
    # Error Tracking
    error_tracking_enabled: bool = True
    error_history_limit: int = 10000
    error_window_size_seconds: int = 3600
    error_spike_threshold_multiplier: float = 2.0
    
    # Audit Logging
    audit_logging_enabled: bool = True
    audit_history_limit: int = 50000
    audit_retention_days: int = 90
    audit_log_sensitive_data: bool = False
    
    # Monitoring API
    monitoring_api_enabled: bool = True
    monitoring_api_rate_limit: int = 1000
    
    class Config:
        env_file = ".env"
        case_sensitive = False

    @property
    def location_list(self) -> List[str]:
        """Convert comma-separated locations to list"""
        return [loc.strip() for loc in self.locations.split(",")]

    @property
    def database_engine_kwargs(self) -> dict:
        """Return database engine configuration"""
        if "postgresql" in self.database_url:
            return {"pool_pre_ping": True, "pool_size": 10}
        return {}


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance
    Uses lru_cache to ensure only one Settings object is created
    """
    return Settings()


# Singleton instance
settings = get_settings()
