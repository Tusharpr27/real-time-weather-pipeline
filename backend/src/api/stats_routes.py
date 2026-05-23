"""
Statistics and processed data API routes
Provides endpoints for processed metrics and analytics
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime, timedelta

from src.database.database import get_db
from src.database.repository import ProcessedMetricsRepository, LocationRepository
from src.utils.logger import logger


router = APIRouter(prefix="/api/stats", tags=["Statistics"])


# Pydantic schemas for responses
from pydantic import BaseModel


class ProcessedMetricResponse(BaseModel):
    """Response model for processed metrics"""
    id: int
    location_id: int
    location_name: str
    metric_type: str  # hourly, daily, weekly
    timestamp: datetime
    
    # Statistics
    avg_temperature: float
    max_temperature: float
    min_temperature: float
    
    avg_humidity: float
    max_humidity: float
    min_humidity: float
    
    avg_wind_speed: float
    max_wind_speed: float
    
    avg_pressure: float
    
    # Derived metrics
    avg_heat_index: Optional[float] = None
    avg_comfort_index: Optional[float] = None
    
    # Summary
    data_points: int
    created_at: datetime

    class Config:
        from_attributes = True


class StatsResponse(BaseModel):
    """Generic stats response"""
    location: str
    metric_type: str
    period: str
    data: List[ProcessedMetricResponse]
    summary: dict


@router.get("/{location_name}/hourly", response_model=StatsResponse, summary="Get hourly statistics")
async def get_hourly_stats(
    location_name: str,
    hours: int = Query(24, ge=1, le=240, description="Hours to retrieve (default: 24, max: 240)"),
    db = None
):
    """
    Get hourly aggregated metrics for a location
    
    Args:
        location_name: Name of the location
        hours: Number of hours to retrieve (default: 24)
    """
    # Get database session
    db = next(get_db())
    
    try:
        # Get location
        location = LocationRepository.get_by_name(db, location_name)
        if not location:
            raise HTTPException(status_code=404, detail=f"Location '{location_name}' not found")
        
        # Get metrics
        since = datetime.utcnow() - timedelta(hours=hours)
        metrics = ProcessedMetricsRepository.get_by_location_and_type(
            db,
            location.id,
            "hourly",
            since_datetime=since
        )
        
        if not metrics:
            logger.warning(f"No hourly metrics found for {location_name} in last {hours} hours")
            return StatsResponse(
                location=location_name,
                metric_type="hourly",
                period=f"Last {hours} hours",
                data=[],
                summary={"count": 0}
            )
        
        # Build response
        metric_responses = [ProcessedMetricResponse.from_orm(m) for m in metrics]
        
        # Calculate summary
        summary = {
            "count": len(metrics),
            "period_start": min(m.timestamp for m in metrics),
            "period_end": max(m.timestamp for m in metrics),
            "avg_temp": round(sum(m.avg_temperature for m in metrics) / len(metrics), 2),
            "min_temp": round(min(m.min_temperature for m in metrics), 2),
            "max_temp": round(max(m.max_temperature for m in metrics), 2),
            "avg_humidity": round(sum(m.avg_humidity for m in metrics) / len(metrics), 2)
        }
        
        return StatsResponse(
            location=location_name,
            metric_type="hourly",
            period=f"Last {hours} hours",
            data=metric_responses,
            summary=summary
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching hourly stats for {location_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router.get("/{location_name}/daily", response_model=StatsResponse, summary="Get daily statistics")
async def get_daily_stats(
    location_name: str,
    days: int = Query(7, ge=1, le=90, description="Days to retrieve (default: 7, max: 90)"),
    db = None
):
    """
    Get daily aggregated metrics for a location
    
    Args:
        location_name: Name of the location
        days: Number of days to retrieve (default: 7)
    """
    db = next(get_db())
    
    try:
        # Get location
        location = LocationRepository.get_by_name(db, location_name)
        if not location:
            raise HTTPException(status_code=404, detail=f"Location '{location_name}' not found")
        
        # Get metrics
        since = datetime.utcnow() - timedelta(days=days)
        metrics = ProcessedMetricsRepository.get_by_location_and_type(
            db,
            location.id,
            "daily",
            since_datetime=since
        )
        
        if not metrics:
            logger.warning(f"No daily metrics found for {location_name} in last {days} days")
            return StatsResponse(
                location=location_name,
                metric_type="daily",
                period=f"Last {days} days",
                data=[],
                summary={"count": 0}
            )
        
        # Build response
        metric_responses = [ProcessedMetricResponse.from_orm(m) for m in metrics]
        
        # Calculate summary
        summary = {
            "count": len(metrics),
            "period_start": min(m.timestamp for m in metrics),
            "period_end": max(m.timestamp for m in metrics),
            "avg_temp": round(sum(m.avg_temperature for m in metrics) / len(metrics), 2),
            "min_temp": round(min(m.min_temperature for m in metrics), 2),
            "max_temp": round(max(m.max_temperature for m in metrics), 2),
            "max_heat_index": round(max(m.avg_heat_index for m in metrics if m.avg_heat_index), 2) if any(m.avg_heat_index for m in metrics) else None
        }
        
        return StatsResponse(
            location=location_name,
            metric_type="daily",
            period=f"Last {days} days",
            data=metric_responses,
            summary=summary
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching daily stats for {location_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router.get("/{location_name}/weekly", response_model=StatsResponse, summary="Get weekly statistics")
async def get_weekly_stats(
    location_name: str,
    weeks: int = Query(4, ge=1, le=12, description="Weeks to retrieve (default: 4, max: 12)"),
    db = None
):
    """
    Get weekly aggregated metrics for a location
    
    Args:
        location_name: Name of the location
        weeks: Number of weeks to retrieve (default: 4)
    """
    db = next(get_db())
    
    try:
        # Get location
        location = LocationRepository.get_by_name(db, location_name)
        if not location:
            raise HTTPException(status_code=404, detail=f"Location '{location_name}' not found")
        
        # Get metrics
        since = datetime.utcnow() - timedelta(weeks=weeks)
        metrics = ProcessedMetricsRepository.get_by_location_and_type(
            db,
            location.id,
            "weekly",
            since_datetime=since
        )
        
        if not metrics:
            logger.warning(f"No weekly metrics found for {location_name} in last {weeks} weeks")
            return StatsResponse(
                location=location_name,
                metric_type="weekly",
                period=f"Last {weeks} weeks",
                data=[],
                summary={"count": 0}
            )
        
        # Build response
        metric_responses = [ProcessedMetricResponse.from_orm(m) for m in metrics]
        
        # Calculate summary
        summary = {
            "count": len(metrics),
            "period_start": min(m.timestamp for m in metrics),
            "period_end": max(m.timestamp for m in metrics),
            "avg_temp": round(sum(m.avg_temperature for m in metrics) / len(metrics), 2),
            "trend": "warming" if metrics[-1].avg_temperature > metrics[0].avg_temperature else "cooling"
        }
        
        return StatsResponse(
            location=location_name,
            metric_type="weekly",
            period=f"Last {weeks} weeks",
            data=metric_responses,
            summary=summary
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching weekly stats for {location_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router.get("/{location_name}/trends", summary="Get weather trends")
async def get_trends(
    location_name: str,
    days: int = Query(7, ge=1, le=30),
    db = None
):
    """Get weather trends for a location"""
    db = next(get_db())
    
    try:
        # Get location
        location = LocationRepository.get_by_name(db, location_name)
        if not location:
            raise HTTPException(status_code=404, detail=f"Location '{location_name}' not found")
        
        # Get daily metrics
        since = datetime.utcnow() - timedelta(days=days)
        metrics = ProcessedMetricsRepository.get_by_location_and_type(
            db,
            location.id,
            "daily",
            since_datetime=since
        )
        
        if not metrics:
            return {
                "location": location_name,
                "period_days": days,
                "status": "no_data"
            }
        
        # Calculate trends
        temps = [m.avg_temperature for m in sorted(metrics, key=lambda x: x.timestamp)]
        humidity = [m.avg_humidity for m in sorted(metrics, key=lambda x: x.timestamp)]
        
        # Linear trend
        temp_trend = (temps[-1] - temps[0]) / len(temps) if len(temps) > 1 else 0
        humidity_trend = (humidity[-1] - humidity[0]) / len(humidity) if len(humidity) > 1 else 0
        
        return {
            "location": location_name,
            "period_days": days,
            "temperature_trend": round(temp_trend, 3),
            "humidity_trend": round(humidity_trend, 3),
            "trend_description": f"Temperature {'increasing' if temp_trend > 0 else 'decreasing'} by {abs(round(temp_trend, 2))}°C/day",
            "data_points": len(metrics),
            "start_date": min(m.timestamp for m in metrics),
            "end_date": max(m.timestamp for m in metrics)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching trends for {location_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router.get("/comparison/all-locations", summary="Compare all locations")
async def compare_locations(
    metric_type: str = Query("daily", regex="^(hourly|daily|weekly)$"),
    db = None
):
    """Compare current metrics across all locations"""
    db = next(get_db())
    
    try:
        locations = LocationRepository.get_all(db, active_only=True)
        
        comparison = {
            "metric_type": metric_type,
            "timestamp": datetime.utcnow(),
            "locations": []
        }
        
        for location in locations:
            metrics = ProcessedMetricsRepository.get_by_location_and_type(
                db,
                location.id,
                metric_type,
                limit=1,
                order_by_desc=True
            )
            
            if metrics:
                m = metrics[0]
                comparison["locations"].append({
                    "name": location.name,
                    "temperature": m.avg_temperature,
                    "humidity": m.avg_humidity,
                    "wind_speed": m.avg_wind_speed,
                    "heat_index": m.avg_heat_index,
                    "timestamp": m.timestamp
                })
        
        return comparison
        
    except Exception as e:
        logger.error(f"Error comparing locations: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()
