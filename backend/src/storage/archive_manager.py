"""
Archive manager module
Handles data archiving and compression strategies
"""
import json
import gzip
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List
from sqlalchemy.orm import Session

from src.database.models import ProcessedMetrics, Alert
from src.database.database import create_session
from src.utils.logger import logger


class ArchiveManager:
    """Manages data archiving and compression"""

    def __init__(self, archive_dir: str = "archives"):
        self.archive_dir = Path(archive_dir)
        self.archive_dir.mkdir(exist_ok=True)
        self.db: Session = None

    def start(self):
        """Initialize database session"""
        self.db = create_session()

    def finish(self):
        """Close database session"""
        if self.db:
            self.db.close()
            self.db = None

    async def export_weekly_metrics(self, location_id: int = None, compress: bool = True) -> str:
        """
        Export weekly metrics to file (optionally compressed)
        
        Args:
            location_id: Specific location or None for all
            compress: Whether to gzip compress
            
        Returns:
            Path to exported file
        """
        self.start()

        try:
            logger.info("📦 Exporting weekly metrics to archive...")
            
            # Query weekly metrics from last month
            query = self.db.query(ProcessedMetrics).filter(
                ProcessedMetrics.metric_type == "weekly",
                ProcessedMetrics.timestamp >= datetime.utcnow() - timedelta(days=30)
            )
            
            if location_id:
                query = query.filter(ProcessedMetrics.location_id == location_id)
            
            metrics = query.all()
            
            # Convert to JSON-serializable format
            data = []
            for m in metrics:
                data.append({
                    "location_id": m.location_id,
                    "timestamp": m.timestamp.isoformat(),
                    "metric_type": m.metric_type,
                    "avg_temperature": m.avg_temperature,
                    "max_temperature": m.max_temperature,
                    "min_temperature": m.min_temperature,
                    "avg_humidity": m.avg_humidity,
                    "max_humidity": m.max_humidity,
                    "min_humidity": m.min_humidity,
                    "avg_wind_speed": m.avg_wind_speed,
                    "max_wind_speed": m.max_wind_speed,
                    "avg_pressure": m.avg_pressure,
                    "avg_heat_index": m.avg_heat_index,
                    "avg_comfort_index": m.avg_comfort_index,
                    "data_points": m.data_points
                })
            
            # Create filename
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = f"weekly_metrics_{timestamp}.json"
            filepath = self.archive_dir / filename
            
            # Write data
            if compress:
                filepath = Path(str(filepath) + ".gz")
                with gzip.open(filepath, 'wt') as f:
                    json.dump(data, f, indent=2)
                logger.info(f"✅ Exported {len(metrics)} weekly metrics (compressed) to {filepath}")
            else:
                with open(filepath, 'w') as f:
                    json.dump(data, f, indent=2)
                logger.info(f"✅ Exported {len(metrics)} weekly metrics to {filepath}")
            
            return str(filepath)

        except Exception as e:
            logger.error(f"Error exporting metrics: {e}")
            return ""
        finally:
            self.finish()

    async def export_alerts(self, days: int = 30, compress: bool = True) -> str:
        """
        Export alerts to archive file
        
        Args:
            days: Days of alerts to export
            compress: Whether to gzip compress
            
        Returns:
            Path to exported file
        """
        self.start()

        try:
            logger.info(f"📦 Exporting alerts from last {days} days...")
            
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            alerts = self.db.query(Alert).filter(Alert.created_at >= cutoff_date).all()
            
            # Convert to JSON-serializable format
            data = []
            for alert in alerts:
                data.append({
                    "location_id": alert.location_id,
                    "type": alert.alert_type,
                    "description": alert.description,
                    "severity": alert.severity,
                    "status": alert.status,
                    "created_at": alert.created_at.isoformat(),
                    "resolved_at": alert.resolved_at.isoformat() if alert.resolved_at else None
                })
            
            # Create filename
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = f"alerts_{timestamp}.json"
            filepath = self.archive_dir / filename
            
            # Write data
            if compress:
                filepath = Path(str(filepath) + ".gz")
                with gzip.open(filepath, 'wt') as f:
                    json.dump(data, f, indent=2)
                logger.info(f"✅ Exported {len(alerts)} alerts (compressed) to {filepath}")
            else:
                with open(filepath, 'w') as f:
                    json.dump(data, f, indent=2)
                logger.info(f"✅ Exported {len(alerts)} alerts to {filepath}")
            
            return str(filepath)

        except Exception as e:
            logger.error(f"Error exporting alerts: {e}")
            return ""
        finally:
            self.finish()

    async def get_archive_stats(self) -> Dict:
        """
        Get statistics about archived files
        
        Returns:
            Dictionary with archive statistics
        """
        try:
            stats = {
                "archive_count": 0,
                "total_size_bytes": 0,
                "total_size_mb": 0,
                "archives": []
            }
            
            if not self.archive_dir.exists():
                return stats
            
            for file in self.archive_dir.iterdir():
                if file.is_file():
                    size = file.stat().st_size
                    stats["archive_count"] += 1
                    stats["total_size_bytes"] += size
                    stats["archives"].append({
                        "name": file.name,
                        "size_bytes": size,
                        "size_mb": round(size / (1024 * 1024), 2),
                        "created": datetime.fromtimestamp(file.stat().st_ctime)
                    })
            
            stats["total_size_mb"] = round(stats["total_size_bytes"] / (1024 * 1024), 2)
            
            return stats

        except Exception as e:
            logger.error(f"Error getting archive stats: {e}")
            return {}

    async def cleanup_old_archives(self, retention_days: int = 90) -> int:
        """
        Delete archived files older than retention period
        
        Args:
            retention_days: Days to keep archives (default: 90)
            
        Returns:
            Number of archives deleted
        """
        try:
            logger.info(f"🗑️  Cleaning archives older than {retention_days} days...")
            
            cutoff_time = datetime.utcnow() - timedelta(days=retention_days)
            deleted_count = 0
            
            if not self.archive_dir.exists():
                return 0
            
            for file in self.archive_dir.iterdir():
                if file.is_file():
                    file_time = datetime.fromtimestamp(file.stat().st_ctime)
                    if file_time < cutoff_time:
                        file.unlink()
                        deleted_count += 1
                        logger.info(f"  Deleted archive: {file.name}")
            
            logger.info(f"✅ Deleted {deleted_count} old archives")
            return deleted_count

        except Exception as e:
            logger.error(f"Error cleaning archives: {e}")
            return 0

    async def rotate_archives(self, max_count: int = 12) -> int:
        """
        Keep only the most recent N archives (rotation)
        
        Args:
            max_count: Maximum archives to keep (default: 12)
            
        Returns:
            Number of archives deleted
        """
        try:
            logger.info(f"🔄 Rotating archives - keeping last {max_count}...")
            
            if not self.archive_dir.exists():
                return 0
            
            # Get all archive files sorted by modification time (newest first)
            files = sorted(
                self.archive_dir.iterdir(),
                key=lambda x: x.stat().st_mtime,
                reverse=True
            )
            
            deleted_count = 0
            for file in files[max_count:]:
                if file.is_file():
                    file.unlink()
                    deleted_count += 1
                    logger.info(f"  Deleted old archive: {file.name}")
            
            logger.info(f"✅ Archive rotation complete - {deleted_count} old archives removed")
            return deleted_count

        except Exception as e:
            logger.error(f"Error rotating archives: {e}")
            return 0


# Global instance
archive_manager: ArchiveManager = None


def get_archive_manager(archive_dir: str = "archives") -> ArchiveManager:
    """Get or create global archive manager instance"""
    global archive_manager
    if archive_manager is None:
        archive_manager = ArchiveManager(archive_dir)
    return archive_manager
