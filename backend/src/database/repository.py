"""
Database repository classes for data access layer
Provides abstraction for database operations
"""
from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_

from src.database.models import (
    Location, WeatherData, ProcessedMetrics, Alert, SystemMetric
)


class LocationRepository:
    """Repository for Location operations"""

    @staticmethod
    def create(db: Session, name: str, latitude: float, longitude: float,
               country: Optional[str] = None, timezone: str = "UTC") -> Location:
        """Create a new location"""
        location = Location(
            name=name,
            latitude=latitude,
            longitude=longitude,
            country=country,
            timezone=timezone
        )
        db.add(location)
        db.commit()
        db.refresh(location)
        return location

    @staticmethod
    def get_all(db: Session, active_only: bool = True) -> List[Location]:
        """Get all locations"""
        query = db.query(Location)
        if active_only:
            query = query.filter(Location.is_active == True)
        return query.all()

    @staticmethod
    def get_by_name(db: Session, name: str) -> Optional[Location]:
        """Get location by name"""
        return db.query(Location).filter(Location.name == name).first()

    @staticmethod
    def get_by_id(db: Session, location_id: int) -> Optional[Location]:
        """Get location by ID"""
        return db.query(Location).filter(Location.id == location_id).first()

    @staticmethod
    def delete(db: Session, location_id: int) -> bool:
        """Delete a location"""
        location = db.query(Location).filter(Location.id == location_id).first()
        if location:
            db.delete(location)
            db.commit()
            return True
        return False


class WeatherDataRepository:
    """Repository for WeatherData operations"""

    @staticmethod
    def create(db: Session, location_id: int, temperature: float,
               humidity: int, wind_speed: float, weather_condition: str,
               **kwargs) -> WeatherData:
        """Create new weather data record"""
        weather = WeatherData(
            location_id=location_id,
            temperature=temperature,
            humidity=humidity,
            wind_speed=wind_speed,
            weather_condition=weather_condition,
            **kwargs
        )
        db.add(weather)
        db.commit()
        db.refresh(weather)
        return weather

    @staticmethod
    def get_latest(db: Session, location_id: int) -> Optional[WeatherData]:
        """Get latest weather data for a location"""
        return db.query(WeatherData)\
            .filter(WeatherData.location_id == location_id)\
            .order_by(desc(WeatherData.recorded_at))\
            .first()

    @staticmethod
    def get_history(db: Session, location_id: int, days: int = 7) -> List[WeatherData]:
        """Get weather history for specified number of days"""
        start_date = datetime.utcnow() - timedelta(days=days)
        return db.query(WeatherData)\
            .filter(
                and_(
                    WeatherData.location_id == location_id,
                    WeatherData.recorded_at >= start_date
                )
            )\
            .order_by(WeatherData.recorded_at)\
            .all()

    @staticmethod
    def get_by_date_range(db: Session, location_id: int,
                         start_date: datetime, end_date: datetime) -> List[WeatherData]:
        """Get weather data for a date range"""
        return db.query(WeatherData)\
            .filter(
                and_(
                    WeatherData.location_id == location_id,
                    WeatherData.recorded_at >= start_date,
                    WeatherData.recorded_at <= end_date
                )
            )\
            .order_by(WeatherData.recorded_at)\
            .all()

    @staticmethod
    def cleanup_old_data(db: Session, days_to_keep: int) -> int:
        """Delete weather data older than specified days"""
        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
        count = db.query(WeatherData)\
            .filter(WeatherData.recorded_at < cutoff_date)\
            .delete()
        db.commit()
        return count


class ProcessedMetricsRepository:
    """Repository for ProcessedMetrics operations"""

    @staticmethod
    def create(db: Session, location_id: int, metric_type: str,
               avg_temperature: float, min_temperature: float,
               max_temperature: float, avg_humidity: float,
               avg_wind_speed: float, **kwargs) -> ProcessedMetrics:
        """Create processed metrics record"""
        metrics = ProcessedMetrics(
            location_id=location_id,
            metric_type=metric_type,
            avg_temperature=avg_temperature,
            min_temperature=min_temperature,
            max_temperature=max_temperature,
            avg_humidity=avg_humidity,
            avg_wind_speed=avg_wind_speed,
            period_start=datetime.utcnow(),
            period_end=datetime.utcnow(),
            **kwargs
        )
        db.add(metrics)
        db.commit()
        db.refresh(metrics)
        return metrics

    @staticmethod
    def get_latest(db: Session, location_id: int,
                   metric_type: str = "hourly") -> Optional[ProcessedMetrics]:
        """Get latest metrics for a location"""
        return db.query(ProcessedMetrics)\
            .filter(
                and_(
                    ProcessedMetrics.location_id == location_id,
                    ProcessedMetrics.metric_type == metric_type
                )
            )\
            .order_by(desc(ProcessedMetrics.period_end))\
            .first()

    @staticmethod
    def get_range(db: Session, location_id: int,
                  start_date: datetime, end_date: datetime,
                  metric_type: str = "daily") -> List[ProcessedMetrics]:
        """Get metrics for a date range"""
        return db.query(ProcessedMetrics)\
            .filter(
                and_(
                    ProcessedMetrics.location_id == location_id,
                    ProcessedMetrics.metric_type == metric_type,
                    ProcessedMetrics.period_start >= start_date,
                    ProcessedMetrics.period_end <= end_date
                )
            )\
            .order_by(ProcessedMetrics.period_start)\
            .all()


class AlertRepository:
    """Repository for Alert operations"""

    @staticmethod
    def create(db: Session, location_id: int, alert_type: str,
               severity: str, message: str, metric_name: str,
               metric_value: float, threshold_value: float) -> Alert:
        """Create new alert"""
        alert = Alert(
            location_id=location_id,
            alert_type=alert_type,
            severity=severity,
            message=message,
            metric_name=metric_name,
            metric_value=metric_value,
            threshold_value=threshold_value
        )
        db.add(alert)
        db.commit()
        db.refresh(alert)
        return alert

    @staticmethod
    def get_active_alerts(db: Session, location_id: Optional[int] = None) -> List[Alert]:
        """Get active (new or acknowledged) alerts"""
        query = db.query(Alert).filter(
            Alert.status.in_(["new", "acknowledged"])
        )
        if location_id:
            query = query.filter(Alert.location_id == location_id)
        return query.order_by(desc(Alert.triggered_at)).all()

    @staticmethod
    def get_recent_alerts(db: Session, location_id: int, hours: int = 24) -> List[Alert]:
        """Get recent alerts for a location"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        return db.query(Alert)\
            .filter(
                and_(
                    Alert.location_id == location_id,
                    Alert.triggered_at >= cutoff_time
                )
            )\
            .order_by(desc(Alert.triggered_at))\
            .all()

    @staticmethod
    def acknowledge(db: Session, alert_id: int) -> Optional[Alert]:
        """Acknowledge an alert"""
        alert = db.query(Alert).filter(Alert.id == alert_id).first()
        if alert:
            alert.status = "acknowledged"
            alert.acknowledged_at = datetime.utcnow()
            db.commit()
            db.refresh(alert)
        return alert

    @staticmethod
    def resolve(db: Session, alert_id: int, notes: Optional[str] = None) -> Optional[Alert]:
        """Resolve an alert"""
        alert = db.query(Alert).filter(Alert.id == alert_id).first()
        if alert:
            alert.status = "resolved"
            alert.resolved_at = datetime.utcnow()
            if notes:
                alert.resolution_notes = notes
            db.commit()
            db.refresh(alert)
        return alert


class SystemMetricRepository:
    """Repository for SystemMetric operations"""

    @staticmethod
    def create(db: Session, **kwargs) -> SystemMetric:
        """Create system metric record"""
        metric = SystemMetric(**kwargs)
        db.add(metric)
        db.commit()
        db.refresh(metric)
        return metric

    @staticmethod
    def get_latest(db: Session) -> Optional[SystemMetric]:
        """Get latest system metrics"""
        return db.query(SystemMetric)\
            .order_by(desc(SystemMetric.measurement_time))\
            .first()

    @staticmethod
    def get_history(db: Session, hours: int = 24) -> List[SystemMetric]:
        """Get system metrics history"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        return db.query(SystemMetric)\
            .filter(SystemMetric.measurement_time >= cutoff_time)\
            .order_by(SystemMetric.measurement_time)\
            .all()
