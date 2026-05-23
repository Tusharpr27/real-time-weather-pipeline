"""
Pydantic schemas for API requests/responses
Data validation and serialization
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


# ======================== Location Schemas ========================

class LocationBase(BaseModel):
    """Base location schema"""
    name: str
    latitude: float
    longitude: float
    country: Optional[str] = None
    timezone: str = "UTC"


class LocationCreate(LocationBase):
    """Schema for creating location"""
    pass


class LocationResponse(LocationBase):
    """Schema for location response"""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ======================== Weather Data Schemas ========================

class WeatherDataBase(BaseModel):
    """Base weather data schema"""
    temperature: float = Field(..., description="Temperature in Celsius")
    feels_like: Optional[float] = None
    temp_min: Optional[float] = None
    temp_max: Optional[float] = None
    humidity: int = Field(..., ge=0, le=100, description="Humidity percentage")
    pressure: Optional[float] = None
    wind_speed: float = Field(..., description="Wind speed in km/h")
    wind_direction: Optional[int] = Field(None, ge=0, le=360)
    wind_gust: Optional[float] = None
    rainfall: Optional[float] = None
    snowfall: Optional[float] = None
    weather_condition: str
    description: Optional[str] = None
    visibility: Optional[float] = None
    uv_index: Optional[float] = None
    cloud_coverage: Optional[int] = Field(None, ge=0, le=100)


class WeatherDataCreate(WeatherDataBase):
    """Schema for creating weather data"""
    location_id: int


class WeatherDataResponse(WeatherDataBase):
    """Schema for weather data response"""
    id: int
    location_id: int
    recorded_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True


# ======================== Processed Metrics Schemas ========================

class ProcessedMetricsResponse(BaseModel):
    """Schema for processed metrics response"""
    id: int
    location_id: int
    metric_type: str
    period_start: datetime
    period_end: datetime
    avg_temperature: float
    min_temperature: float
    max_temperature: float
    temp_trend: Optional[str] = None
    avg_humidity: float
    min_humidity: Optional[float] = None
    max_humidity: Optional[float] = None
    avg_wind_speed: float
    max_wind_speed: Optional[float] = None
    total_rainfall: float
    total_snowfall: float
    heat_index: Optional[float] = None
    wind_chill: Optional[float] = None
    air_quality_index: Optional[float] = None
    data_points_count: int
    created_at: datetime

    class Config:
        from_attributes = True


# ======================== Alert Schemas ========================

class AlertResponse(BaseModel):
    """Schema for alert response"""
    id: int
    location_id: int
    alert_type: str
    severity: str
    message: str
    metric_name: str
    metric_value: float
    threshold_value: float
    status: str
    triggered_at: datetime
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    resolution_notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class AlertCreate(BaseModel):
    """Schema for creating alert"""
    alert_id: int


# ======================== System Schemas ========================

class HealthCheckResponse(BaseModel):
    """Schema for health check response"""
    status: str
    app_name: str
    environment: str
    version: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ErrorResponse(BaseModel):
    """Schema for error responses"""
    detail: str
    status_code: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)
