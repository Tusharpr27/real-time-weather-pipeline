"""
Weather API routes
Endpoints for accessing weather data
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List

from src.database.database import get_db
from src.database.repository import (
    LocationRepository,
    WeatherDataRepository,
    ProcessedMetricsRepository
)
from src.api.schemas import (
    LocationResponse,
    WeatherDataResponse,
    ProcessedMetricsResponse
)
from src.utils.logger import logger

router = APIRouter(prefix="/api/weather", tags=["Weather"])


@router.get("/locations", response_model=List[LocationResponse])
async def get_locations(db: Session = Depends(get_db)):
    """Get all active monitored locations"""
    try:
        locations = LocationRepository.get_all(db, active_only=True)
        return locations
    except Exception as e:
        logger.error(f"Error fetching locations: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch locations")


@router.get("/locations/{location_id}", response_model=LocationResponse)
async def get_location(location_id: int, db: Session = Depends(get_db)):
    """Get specific location details"""
    try:
        location = LocationRepository.get_by_id(db, location_id)
        if not location:
            raise HTTPException(status_code=404, detail="Location not found")
        return location
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching location: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch location")


@router.get("/current/{location_name}", response_model=WeatherDataResponse)
async def get_current_weather(location_name: str, db: Session = Depends(get_db)):
    """
    Get current weather for a location
    
    Args:
        location_name: Name of the location (e.g., "Delhi", "Mumbai")
    """
    try:
        location = LocationRepository.get_by_name(db, location_name)
        if not location:
            raise HTTPException(status_code=404, detail=f"Location '{location_name}' not found")
        
        weather = WeatherDataRepository.get_latest(db, location.id)
        if not weather:
            raise HTTPException(status_code=404, detail=f"No weather data available for {location_name}")
        
        return weather
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching current weather for {location_name}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch weather data")


@router.get("/current/id/{location_id}", response_model=WeatherDataResponse)
async def get_current_weather_by_id(location_id: int, db: Session = Depends(get_db)):
    """Get current weather for a location by ID"""
    try:
        location = LocationRepository.get_by_id(db, location_id)
        if not location:
            raise HTTPException(status_code=404, detail="Location not found")
        
        weather = WeatherDataRepository.get_latest(db, location_id)
        if not weather:
            raise HTTPException(status_code=404, detail="No weather data available for this location")
        
        return weather
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching current weather: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch weather data")


@router.get("/history/{location_name}", response_model=List[WeatherDataResponse])
async def get_weather_history(
    location_name: str,
    days: int = Query(7, ge=1, le=30, description="Number of days of history"),
    db: Session = Depends(get_db)
):
    """
    Get historical weather data for a location
    
    Args:
        location_name: Name of the location
        days: Number of days of history (1-30, default: 7)
    """
    try:
        location = LocationRepository.get_by_name(db, location_name)
        if not location:
            raise HTTPException(status_code=404, detail=f"Location '{location_name}' not found")
        
        weather_history = WeatherDataRepository.get_history(db, location.id, days=days)
        if not weather_history:
            raise HTTPException(status_code=404, detail="No weather history available")
        
        return weather_history
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching weather history for {location_name}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch weather history")


@router.get("/history/id/{location_id}", response_model=List[WeatherDataResponse])
async def get_weather_history_by_id(
    location_id: int,
    days: int = Query(7, ge=1, le=30),
    db: Session = Depends(get_db)
):
    """Get historical weather data by location ID"""
    try:
        location = LocationRepository.get_by_id(db, location_id)
        if not location:
            raise HTTPException(status_code=404, detail="Location not found")
        
        weather_history = WeatherDataRepository.get_history(db, location_id, days=days)
        if not weather_history:
            raise HTTPException(status_code=404, detail="No weather history available")
        
        return weather_history
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching weather history: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch weather history")


@router.get("/stats/{location_name}", response_model=ProcessedMetricsResponse)
async def get_weather_stats(
    location_name: str,
    metric_type: str = Query("daily", regex="^(hourly|daily|weekly)$"),
    db: Session = Depends(get_db)
):
    """
    Get aggregated weather statistics for a location
    
    Args:
        location_name: Name of the location
        metric_type: Type of aggregation (hourly, daily, weekly)
    """
    try:
        location = LocationRepository.get_by_name(db, location_name)
        if not location:
            raise HTTPException(status_code=404, detail=f"Location '{location_name}' not found")
        
        metrics = ProcessedMetricsRepository.get_latest(db, location.id, metric_type)
        if not metrics:
            raise HTTPException(status_code=404, detail="No statistics available")
        
        return metrics
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching weather stats for {location_name}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch weather statistics")


@router.get("/{location_name}/summary")
async def get_location_summary(
    location_name: str,
    db: Session = Depends(get_db)
):
    """
    Get summary of weather data for a location
    Includes current weather and recent statistics
    """
    try:
        location = LocationRepository.get_by_name(db, location_name)
        if not location:
            raise HTTPException(status_code=404, detail=f"Location '{location_name}' not found")
        
        current = WeatherDataRepository.get_latest(db, location.id)
        history = WeatherDataRepository.get_history(db, location.id, days=7)
        metrics = ProcessedMetricsRepository.get_latest(db, location.id, "daily")
        
        if not current:
            raise HTTPException(status_code=404, detail="No weather data available")
        
        return {
            "location": {
                "id": location.id,
                "name": location.name,
                "latitude": location.latitude,
                "longitude": location.longitude,
                "country": location.country,
                "timezone": location.timezone
            },
            "current": {
                "temperature": current.temperature,
                "feels_like": current.feels_like,
                "humidity": current.humidity,
                "wind_speed": current.wind_speed,
                "weather_condition": current.weather_condition,
                "recorded_at": current.recorded_at
            },
            "statistics": {
                "data_points": len(history),
                "temperature_range": {
                    "min": min((w.temperature for w in history), default=None),
                    "max": max((w.temperature for w in history), default=None),
                    "avg": sum((w.temperature for w in history), 0) / len(history) if history else None
                },
                "humidity_avg": sum((w.humidity for w in history), 0) / len(history) if history else None
            } if metrics else {}
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching location summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch location summary")
