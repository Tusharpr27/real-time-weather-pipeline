"""
System API routes
Health checks and system information
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime

from src.database.database import get_db
from src.database.repository import SystemMetricRepository
from src.api.schemas import HealthCheckResponse
from src.utils.logger import logger
from config import settings

router = APIRouter(prefix="/api", tags=["System"])


@router.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """System health check endpoint"""
    return HealthCheckResponse(
        status="healthy",
        app_name=settings.app_name,
        environment=settings.app_env,
        version="0.1.0"
    )


@router.get("/system/metrics")
async def get_system_metrics(db: Session = Depends(get_db)):
    """Get current system metrics"""
    try:
        metrics = SystemMetricRepository.get_latest(db)
        
        if not metrics:
            return {
                "message": "No metrics available yet",
                "timestamp": datetime.utcnow()
            }
        
        return {
            "api_calls": {
                "total": metrics.total_api_calls,
                "successful": metrics.successful_api_calls,
                "failed": metrics.failed_api_calls
            },
            "performance": {
                "avg_api_response_time_ms": metrics.api_response_time_avg,
                "avg_processing_time_ms": metrics.processing_time_avg,
                "avg_database_query_time_ms": metrics.database_query_time_avg
            },
            "processing": {
                "total_records": metrics.total_records_processed
            },
            "alerts": {
                "total_triggered": metrics.total_alerts_triggered
            },
            "last_sync": metrics.last_successful_sync,
            "measurement_time": metrics.measurement_time
        }
    except Exception as e:
        logger.error(f"Error fetching system metrics: {e}")
        return {
            "error": "Failed to fetch system metrics",
            "timestamp": datetime.utcnow()
        }


@router.get("/system/status")
async def get_system_status():
    """Get overall system status"""
    return {
        "status": "running",
        "app_name": settings.app_name,
        "environment": settings.app_env,
        "version": "0.1.0",
        "locations_monitored": len(settings.location_list),
        "fetch_interval_minutes": settings.fetch_interval_minutes,
        "data_retention_days": settings.data_retention_days,
        "alerts_enabled": settings.alert_enabled,
        "timestamp": datetime.utcnow()
    }


@router.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Real-Time Weather Pipeline API",
        "version": "0.1.0",
        "docs": "/docs",
        "endpoints": {
            "system": "/api/health",
            "weather": "/api/weather/locations",
            "documentation": "/docs"
        }
    }
