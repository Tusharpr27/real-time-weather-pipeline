"""
Data export REST API routes
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime

from src.api.data_exporter import get_data_exporter, ExportFormat
from src.utils.logger import logger

router = APIRouter(prefix="/api/export", tags=["export"])


@router.get("/alerts")
async def export_alerts(format: str = Query("json", description="Export format: csv, json, jsonl"),
                       fields: Optional[str] = Query(None, description="Comma-separated fields"),
                       limit: int = Query(1000, ge=1, le=10000)):
    """Export alerts"""
    try:
        exporter = get_data_exporter()
        
        field_list = fields.split(",") if fields else None
        
        result = await exporter.export_alerts(
            format=format,
            fields=field_list,
            limit=limit
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
    except Exception as e:
        logger.error(f"Error exporting alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/weather")
async def export_weather(format: str = Query("json"),
                        location_id: Optional[int] = Query(None),
                        start_date: Optional[str] = Query(None),
                        end_date: Optional[str] = Query(None),
                        fields: Optional[str] = Query(None),
                        limit: int = Query(5000, ge=1, le=50000)):
    """Export weather data"""
    try:
        exporter = get_data_exporter()
        
        date_range = None
        if start_date or end_date:
            date_range = {}
            if start_date:
                date_range["start"] = datetime.fromisoformat(start_date)
            if end_date:
                date_range["end"] = datetime.fromisoformat(end_date)
        
        field_list = fields.split(",") if fields else None
        
        result = await exporter.export_weather_data(
            format=format,
            location_id=location_id,
            date_range=date_range,
            fields=field_list,
            limit=limit
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
    except Exception as e:
        logger.error(f"Error exporting weather: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics")
async def export_metrics(format: str = Query("json"),
                        metric_type: str = Query("hourly", description="hourly, daily, weekly"),
                        location_id: Optional[int] = Query(None),
                        start_date: Optional[str] = Query(None),
                        end_date: Optional[str] = Query(None),
                        fields: Optional[str] = Query(None),
                        limit: int = Query(5000, ge=1, le=50000)):
    """Export metrics"""
    try:
        exporter = get_data_exporter()
        
        date_range = None
        if start_date or end_date:
            date_range = {}
            if start_date:
                date_range["start"] = datetime.fromisoformat(start_date)
            if end_date:
                date_range["end"] = datetime.fromisoformat(end_date)
        
        field_list = fields.split(",") if fields else None
        
        result = await exporter.export_metrics(
            format=format,
            metric_type=metric_type,
            location_id=location_id,
            date_range=date_range,
            fields=field_list,
            limit=limit
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
    except Exception as e:
        logger.error(f"Error exporting metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/formats")
async def get_export_formats():
    """Get available export formats"""
    return {
        "formats": [
            {
                "name": "json",
                "description": "JSON array format",
                "extension": ".json"
            },
            {
                "name": "jsonl",
                "description": "JSON Lines format (one record per line)",
                "extension": ".jsonl"
            },
            {
                "name": "csv",
                "description": "Comma-separated values",
                "extension": ".csv"
            }
        ]
    }
