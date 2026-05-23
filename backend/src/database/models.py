"""
Database models using SQLAlchemy ORM
Defines all database tables for the weather pipeline
"""
from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, DateTime, Boolean, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Location(Base):
    """
    Represents a geographic location being monitored
    """
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    country = Column(String(100), nullable=True)
    timezone = Column(String(50), nullable=True, default="UTC")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    weather_data = relationship("WeatherData", back_populates="location", cascade="all, delete-orphan")
    processed_metrics = relationship("ProcessedMetrics", back_populates="location", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="location", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Location(name={self.name}, lat={self.latitude}, lon={self.longitude})>"


class WeatherData(Base):
    """
    Raw weather data fetched from API
    Stores current weather information for each location
    """
    __tablename__ = "weather_data"

    id = Column(Integer, primary_key=True, index=True)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)
    
    # Temperature readings
    temperature = Column(Float, nullable=False)  # Celsius
    feels_like = Column(Float, nullable=True)    # Felt temperature
    temp_min = Column(Float, nullable=True)      # Daily min
    temp_max = Column(Float, nullable=True)      # Daily max
    
    # Humidity and Pressure
    humidity = Column(Integer, nullable=False)   # 0-100 %
    pressure = Column(Float, nullable=True)      # hPa
    
    # Wind conditions
    wind_speed = Column(Float, nullable=False)   # km/h or m/s
    wind_direction = Column(Integer, nullable=True)  # Degrees 0-360
    wind_gust = Column(Float, nullable=True)     # Wind gust speed
    
    # Precipitation
    rainfall = Column(Float, nullable=True)      # mm
    snowfall = Column(Float, nullable=True)      # mm
    
    # Weather conditions
    weather_condition = Column(String(50), nullable=False)  # e.g., "Clear", "Rainy"
    description = Column(String(255), nullable=True)
    visibility = Column(Float, nullable=True)    # meters
    uv_index = Column(Float, nullable=True)      # UV Index
    cloud_coverage = Column(Integer, nullable=True)  # 0-100 %
    
    # Timestamps
    recorded_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Indexes for performance
    __table_args__ = (
        Index("ix_weather_data_location_created", "location_id", "created_at"),
        Index("ix_weather_data_location_date", "location_id", "recorded_at"),
    )

    # Relationships
    location = relationship("Location", back_populates="weather_data")

    def __repr__(self):
        return f"<WeatherData(location_id={self.location_id}, temp={self.temperature}, recorded_at={self.recorded_at})>"


class ProcessedMetrics(Base):
    """
    Aggregated and processed weather metrics
    Stores calculated values like averages, trends, etc.
    """
    __tablename__ = "processed_metrics"

    id = Column(Integer, primary_key=True, index=True)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)
    
    # Time aggregation
    metric_type = Column(String(20), nullable=False)  # "hourly", "daily", "weekly"
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    
    # Temperature statistics
    avg_temperature = Column(Float, nullable=False)
    min_temperature = Column(Float, nullable=False)
    max_temperature = Column(Float, nullable=False)
    temp_trend = Column(String(20), nullable=True)  # "increasing", "decreasing", "stable"
    
    # Humidity statistics
    avg_humidity = Column(Float, nullable=False)
    min_humidity = Column(Float, nullable=True)
    max_humidity = Column(Float, nullable=True)
    
    # Wind statistics
    avg_wind_speed = Column(Float, nullable=False)
    max_wind_speed = Column(Float, nullable=True)
    dominant_wind_direction = Column(Integer, nullable=True)
    
    # Precipitation
    total_rainfall = Column(Float, default=0.0)
    total_snowfall = Column(Float, default=0.0)
    
    # Comfort index
    heat_index = Column(Float, nullable=True)
    wind_chill = Column(Float, nullable=True)
    air_quality_index = Column(Float, nullable=True)
    
    # Metadata
    data_points_count = Column(Integer, default=0)  # Number of raw data points used
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Indexes
    __table_args__ = (
        Index("ix_processed_metrics_location_type", "location_id", "metric_type"),
        Index("ix_processed_metrics_period", "period_start", "period_end"),
    )

    # Relationships
    location = relationship("Location", back_populates="processed_metrics")

    def __repr__(self):
        return f"<ProcessedMetrics(location_id={self.location_id}, type={self.metric_type}, period={self.period_start})>"


class Alert(Base):
    """
    Alert records for significant weather events
    Tracks anomalies and threshold breaches
    """
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)
    
    # Alert details
    alert_type = Column(String(50), nullable=False)  # e.g., "temp_high", "wind_high", "anomaly"
    severity = Column(String(20), nullable=False)    # "low", "medium", "high", "critical"
    message = Column(String(500), nullable=False)
    
    # Threshold information
    metric_name = Column(String(100), nullable=False)  # e.g., "temperature"
    metric_value = Column(Float, nullable=False)       # Actual value that triggered alert
    threshold_value = Column(Float, nullable=False)    # Threshold that was exceeded
    
    # Status tracking
    status = Column(String(20), default="new")  # "new", "acknowledged", "resolved"
    acknowledged_at = Column(DateTime, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    resolution_notes = Column(String(500), nullable=True)
    
    # Timestamps
    triggered_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Indexes
    __table_args__ = (
        Index("ix_alerts_location_status", "location_id", "status"),
        Index("ix_alerts_triggered", "triggered_at"),
        Index("ix_alerts_created", "created_at"),
    )

    # Relationships
    location = relationship("Location", back_populates="alerts")

    def __repr__(self):
        return f"<Alert(location_id={self.location_id}, type={self.alert_type}, severity={self.severity})>"


class SystemMetric(Base):
    """
    System-level metrics for monitoring pipeline health
    Tracks API calls, database operations, etc.
    """
    __tablename__ = "system_metrics"

    id = Column(Integer, primary_key=True, index=True)
    
    # API Metrics
    total_api_calls = Column(Integer, default=0)
    successful_api_calls = Column(Integer, default=0)
    failed_api_calls = Column(Integer, default=0)
    api_response_time_avg = Column(Float, nullable=True)  # milliseconds
    
    # Data Processing
    total_records_processed = Column(Integer, default=0)
    processing_time_avg = Column(Float, nullable=True)  # milliseconds
    
    # Database
    database_query_time_avg = Column(Float, nullable=True)  # milliseconds
    last_successful_sync = Column(DateTime, nullable=True)
    
    # Alerts
    total_alerts_triggered = Column(Integer, default=0)
    
    # Timestamps
    measurement_time = Column(DateTime, default=datetime.utcnow, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<SystemMetric(api_calls={self.total_api_calls}, errors={self.failed_api_calls})>"


class User(Base):
    """
    User account for authentication and dashboard access
    Stores user credentials and profile information
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    
    # Authentication
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    
    # Profile
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    
    # Account status
    email_verified = Column(Boolean, default=False)
    last_login = Column(DateTime, nullable=True)
    
    # Preferences
    preferred_locations = Column(String(500), nullable=True)  # JSON string of location IDs
    theme_preference = Column(String(20), default="light")    # "light" or "dark"
    notifications_enabled = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<User(email={self.email}, full_name={self.full_name})>"
