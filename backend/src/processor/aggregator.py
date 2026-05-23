"""
Data aggregation module
Aggregates raw weather data into hourly, daily, and weekly metrics
"""
from typing import List, Optional
from datetime import datetime, timedelta
import statistics

from sqlalchemy.orm import Session
from sqlalchemy import and_

from src.database.models import WeatherData, ProcessedMetrics
from src.database.repository import (
    WeatherDataRepository,
    ProcessedMetricsRepository
)
from src.processor.calculator import WeatherCalculator
from src.utils.logger import logger


class DataAggregator:
    """Aggregates weather data into processed metrics"""

    @staticmethod
    def aggregate_hourly(db: Session, location_id: int, hour_start: datetime) -> Optional[ProcessedMetrics]:
        """
        Aggregate weather data for one hour
        
        Args:
            db: Database session
            location_id: Location ID
            hour_start: Start of the hour
            
        Returns:
            ProcessedMetrics object or None if no data
        """
        hour_end = hour_start + timedelta(hours=1)

        # Query hourly data
        hourly_data = db.query(WeatherData).filter(
            and_(
                WeatherData.location_id == location_id,
                WeatherData.recorded_at >= hour_start,
                WeatherData.recorded_at < hour_end
            )
        ).order_by(WeatherData.recorded_at).all()

        if not hourly_data:
            return None

        # Calculate statistics
        stats = WeatherCalculator.calculate_statistics(hourly_data)

        # Create metrics record
        metrics = ProcessedMetrics(
            location_id=location_id,
            metric_type="hourly",
            period_start=hour_start,
            period_end=hour_end,
            avg_temperature=stats["temperature"]["avg"],
            min_temperature=stats["temperature"]["min"],
            max_temperature=stats["temperature"]["max"],
            avg_humidity=stats["humidity"]["avg"],
            min_humidity=stats["humidity"]["min"],
            max_humidity=stats["humidity"]["max"],
            avg_wind_speed=stats["wind"]["avg"],
            max_wind_speed=stats["wind"]["max"],
            data_points_count=stats["count"],
            temp_trend=WeatherCalculator.calculate_temperature_trend(hourly_data),
            heat_index=WeatherCalculator.calculate_heat_index(
                stats["temperature"]["avg"],
                int(stats["humidity"]["avg"])
            )
        )

        return metrics

    @staticmethod
    def aggregate_daily(db: Session, location_id: int, date: datetime) -> Optional[ProcessedMetrics]:
        """
        Aggregate weather data for one day
        
        Args:
            db: Database session
            location_id: Location ID
            date: Date to aggregate
            
        Returns:
            ProcessedMetrics object or None if no data
        """
        day_start = datetime.combine(date.date(), datetime.min.time())
        day_end = day_start + timedelta(days=1)

        # Query daily data
        daily_data = db.query(WeatherData).filter(
            and_(
                WeatherData.location_id == location_id,
                WeatherData.recorded_at >= day_start,
                WeatherData.recorded_at < day_end
            )
        ).order_by(WeatherData.recorded_at).all()

        if not daily_data:
            return None

        # Calculate statistics
        stats = WeatherCalculator.calculate_statistics(daily_data)

        # Create metrics record
        metrics = ProcessedMetrics(
            location_id=location_id,
            metric_type="daily",
            period_start=day_start,
            period_end=day_end,
            avg_temperature=stats["temperature"]["avg"],
            min_temperature=stats["temperature"]["min"],
            max_temperature=stats["temperature"]["max"],
            avg_humidity=stats["humidity"]["avg"],
            min_humidity=stats["humidity"]["min"],
            max_humidity=stats["humidity"]["max"],
            avg_wind_speed=stats["wind"]["avg"],
            max_wind_speed=stats["wind"]["max"],
            data_points_count=stats["count"],
            temp_trend=WeatherCalculator.calculate_temperature_trend(daily_data),
            heat_index=WeatherCalculator.calculate_heat_index(
                stats["temperature"]["avg"],
                int(stats["humidity"]["avg"])
            ),
            total_rainfall=sum(d.rainfall for d in daily_data if d.rainfall) or 0.0,
            total_snowfall=sum(d.snowfall for d in daily_data if d.snowfall) or 0.0
        )

        return metrics

    @staticmethod
    def aggregate_weekly(db: Session, location_id: int, week_start: datetime) -> Optional[ProcessedMetrics]:
        """
        Aggregate weather data for one week
        
        Args:
            db: Database session
            location_id: Location ID
            week_start: Start of the week
            
        Returns:
            ProcessedMetrics object or None if no data
        """
        week_end = week_start + timedelta(days=7)

        # Query weekly data
        weekly_data = db.query(WeatherData).filter(
            and_(
                WeatherData.location_id == location_id,
                WeatherData.recorded_at >= week_start,
                WeatherData.recorded_at < week_end
            )
        ).order_by(WeatherData.recorded_at).all()

        if not weekly_data:
            return None

        # Calculate statistics
        stats = WeatherCalculator.calculate_statistics(weekly_data)

        # Create metrics record
        metrics = ProcessedMetrics(
            location_id=location_id,
            metric_type="weekly",
            period_start=week_start,
            period_end=week_end,
            avg_temperature=stats["temperature"]["avg"],
            min_temperature=stats["temperature"]["min"],
            max_temperature=stats["temperature"]["max"],
            avg_humidity=stats["humidity"]["avg"],
            min_humidity=stats["humidity"]["min"],
            max_humidity=stats["humidity"]["max"],
            avg_wind_speed=stats["wind"]["avg"],
            max_wind_speed=stats["wind"]["max"],
            data_points_count=stats["count"],
            temp_trend=WeatherCalculator.calculate_temperature_trend(weekly_data),
            total_rainfall=sum(d.rainfall for d in weekly_data if d.rainfall) or 0.0,
            total_snowfall=sum(d.snowfall for d in weekly_data if d.snowfall) or 0.0
        )

        return metrics

    @staticmethod
    def save_metrics(db: Session, metrics: ProcessedMetrics) -> bool:
        """Save metrics to database"""
        try:
            db.add(metrics)
            db.commit()
            return True
        except Exception as e:
            logger.error(f"Error saving metrics: {e}")
            db.rollback()
            return False

    @staticmethod
    def aggregate_all_locations_hourly(db: Session, location_ids: List[int]) -> int:
        """
        Aggregate hourly metrics for all locations
        
        Returns:
            Number of metrics created
        """
        count = 0
        now = datetime.utcnow()
        hour_start = now.replace(minute=0, second=0, microsecond=0) - timedelta(hours=1)

        for location_id in location_ids:
            metrics = DataAggregator.aggregate_hourly(db, location_id, hour_start)
            if metrics and DataAggregator.save_metrics(db, metrics):
                count += 1
                logger.info(f"✅ Saved hourly metrics for location {location_id}")

        return count

    @staticmethod
    def aggregate_all_locations_daily(db: Session, location_ids: List[int]) -> int:
        """
        Aggregate daily metrics for all locations
        
        Returns:
            Number of metrics created
        """
        count = 0
        yesterday = datetime.utcnow().date() - timedelta(days=1)

        for location_id in location_ids:
            metrics = DataAggregator.aggregate_daily(db, location_id, datetime.combine(yesterday, datetime.min.time()))
            if metrics and DataAggregator.save_metrics(db, metrics):
                count += 1
                logger.info(f"✅ Saved daily metrics for location {location_id}")

        return count

    @staticmethod
    def aggregate_all_locations_weekly(db: Session, location_ids: List[int]) -> int:
        """
        Aggregate weekly metrics for all locations
        
        Returns:
            Number of metrics created
        """
        count = 0
        now = datetime.utcnow()
        # Get start of week (Monday)
        week_start = now - timedelta(days=now.weekday(), hours=now.hour, minutes=now.minute, seconds=now.second, microseconds=now.microsecond)
        week_start -= timedelta(weeks=1)

        for location_id in location_ids:
            metrics = DataAggregator.aggregate_weekly(db, location_id, week_start)
            if metrics and DataAggregator.save_metrics(db, metrics):
                count += 1
                logger.info(f"✅ Saved weekly metrics for location {location_id}")

        return count
