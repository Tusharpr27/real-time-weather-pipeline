"""
Data export module
Exports alerts and weather data to CSV and JSON formats
"""
from typing import Dict, List, Optional, Any
from datetime import datetime
from io import StringIO
import csv
import json
from sqlalchemy.orm import Session

from src.database.database import create_session
from src.database.models import Alert, WeatherData, ProcessedMetrics
from src.utils.logger import logger


class ExportFormat:
    """Export format options"""
    CSV = "csv"
    JSON = "json"
    JSONL = "jsonl"  # JSON Lines


class DataExporter:
    """Exports data in various formats"""
    
    def __init__(self):
        self.db: Optional[Session] = None
    
    def start(self):
        """Initialize"""
        self.db = create_session()
    
    def finish(self):
        """Cleanup"""
        if self.db:
            self.db.close()
            self.db = None
    
    async def export_alerts(self,
                           format: str = ExportFormat.JSON,
                           filters: Dict = None,
                           fields: List[str] = None,
                           limit: int = 1000) -> Dict:
        """
        Export alerts in specified format
        
        Args:
            format: csv, json, or jsonl
            filters: Filter conditions
            fields: Specific fields to include
            limit: Maximum records
            
        Returns:
            Dictionary with export data/URL
        """
        self.start()
        
        try:
            # Query alerts
            query = self.db.query(Alert)
            
            if filters:
                query = self._apply_filters(query, Alert, filters)
            
            alerts = query.limit(limit).all()
            
            logger.info(f"Exporting {len(alerts)} alerts to {format}")
            
            if format == ExportFormat.CSV:
                data = self._export_to_csv(alerts, fields)
            elif format == ExportFormat.JSONL:
                data = self._export_to_jsonl(alerts, fields)
            else:  # JSON
                data = self._export_to_json(alerts, fields)
            
            return {
                "format": format,
                "count": len(alerts),
                "data": data,
                "timestamp": datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"Error exporting alerts: {e}")
            return {"error": str(e)}
        finally:
            self.finish()
    
    async def export_weather_data(self,
                                 format: str = ExportFormat.JSON,
                                 location_id: int = None,
                                 date_range: Dict = None,
                                 fields: List[str] = None,
                                 limit: int = 5000) -> Dict:
        """
        Export weather data
        
        Args:
            format: csv, json, or jsonl
            location_id: Filter by location
            date_range: Start and end dates
            fields: Specific fields
            limit: Maximum records
            
        Returns:
            Export data
        """
        self.start()
        
        try:
            query = self.db.query(WeatherData)
            
            if location_id:
                query = query.filter(WeatherData.location_id == location_id)
            
            if date_range:
                if "start" in date_range:
                    query = query.filter(WeatherData.collected_at >= date_range["start"])
                if "end" in date_range:
                    query = query.filter(WeatherData.collected_at <= date_range["end"])
            
            data_records = query.order_by(WeatherData.collected_at.desc()).limit(limit).all()
            
            logger.info(f"Exporting {len(data_records)} weather records to {format}")
            
            if format == ExportFormat.CSV:
                data = self._export_to_csv(data_records, fields)
            elif format == ExportFormat.JSONL:
                data = self._export_to_jsonl(data_records, fields)
            else:
                data = self._export_to_json(data_records, fields)
            
            return {
                "format": format,
                "count": len(data_records),
                "location_id": location_id,
                "data": data
            }
            
        except Exception as e:
            logger.error(f"Error exporting weather data: {e}")
            return {"error": str(e)}
        finally:
            self.finish()
    
    async def export_metrics(self,
                            format: str = ExportFormat.JSON,
                            metric_type: str = "hourly",
                            location_id: int = None,
                            date_range: Dict = None,
                            fields: List[str] = None,
                            limit: int = 5000) -> Dict:
        """
        Export processed metrics
        
        Args:
            format: Export format
            metric_type: hourly, daily, weekly
            location_id: Filter by location
            date_range: Date range
            fields: Specific fields
            limit: Maximum records
            
        Returns:
            Export data
        """
        self.start()
        
        try:
            query = self.db.query(ProcessedMetrics)
            
            if metric_type:
                query = query.filter(ProcessedMetrics.metric_type == metric_type)
            
            if location_id:
                query = query.filter(ProcessedMetrics.location_id == location_id)
            
            if date_range:
                if "start" in date_range:
                    query = query.filter(ProcessedMetrics.timestamp >= date_range["start"])
                if "end" in date_range:
                    query = query.filter(ProcessedMetrics.timestamp <= date_range["end"])
            
            metrics = query.order_by(ProcessedMetrics.timestamp.desc()).limit(limit).all()
            
            logger.info(f"Exporting {len(metrics)} {metric_type} metrics to {format}")
            
            if format == ExportFormat.CSV:
                data = self._export_to_csv(metrics, fields)
            elif format == ExportFormat.JSONL:
                data = self._export_to_jsonl(metrics, fields)
            else:
                data = self._export_to_json(metrics, fields)
            
            return {
                "format": format,
                "count": len(metrics),
                "metric_type": metric_type,
                "data": data
            }
            
        except Exception as e:
            logger.error(f"Error exporting metrics: {e}")
            return {"error": str(e)}
        finally:
            self.finish()
    
    def _export_to_json(self, records: List, fields: List[str] = None) -> str:
        """Export to JSON format"""
        data = []
        
        for record in records:
            row = self._record_to_dict(record, fields)
            data.append(row)
        
        return json.dumps(data, default=str, indent=2)
    
    def _export_to_jsonl(self, records: List, fields: List[str] = None) -> str:
        """Export to JSON Lines format"""
        lines = []
        
        for record in records:
            row = self._record_to_dict(record, fields)
            lines.append(json.dumps(row, default=str))
        
        return "\n".join(lines)
    
    def _export_to_csv(self, records: List, fields: List[str] = None) -> str:
        """Export to CSV format"""
        if not records:
            return ""
        
        output = StringIO()
        
        # Get all fields if not specified
        first_record = self._record_to_dict(records[0], fields)
        fieldnames = list(first_record.keys())
        
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        
        for record in records:
            row = self._record_to_dict(record, fields)
            writer.writerow(row)
        
        return output.getvalue()
    
    def _record_to_dict(self, record: Any, fields: List[str] = None) -> Dict:
        """Convert SQLAlchemy model to dictionary"""
        data = {}
        
        # Get all columns
        mapper = record.__class__.__mapper__
        
        for column in mapper.columns:
            col_name = column.name
            
            # Filter fields if specified
            if fields and col_name not in fields:
                continue
            
            value = getattr(record, col_name)
            data[col_name] = value
        
        return data
    
    def _apply_filters(self, query, model_class, filters: Dict):
        """Apply filter conditions to query"""
        for field, value in filters.items():
            if hasattr(model_class, field):
                if isinstance(value, dict):
                    # Handle complex filters
                    if "min" in value:
                        query = query.filter(getattr(model_class, field) >= value["min"])
                    if "max" in value:
                        query = query.filter(getattr(model_class, field) <= value["max"])
                else:
                    query = query.filter(getattr(model_class, field) == value)
        
        return query


# Global instance
data_exporter: Optional[DataExporter] = None


def get_data_exporter() -> DataExporter:
    """Get or create global data exporter"""
    global data_exporter
    if data_exporter is None:
        data_exporter = DataExporter()
    return data_exporter
