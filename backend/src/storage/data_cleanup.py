"""
Data cleanup module
Handles deletion of old data and archiving strategies
"""
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import delete

from src.database.models import WeatherData, ProcessedMetrics, Alert, SystemMetric
from src.database.database import create_session
from src.database.repository import (
    WeatherDataRepository,
    ProcessedMetricsRepository,
    AlertRepository
)
from src.utils.logger import logger


class DataCleanup:
    """Manages data cleanup and deletion"""

    def __init__(self):
        self.db: Session = None
        self.cleanup_stats = {
            "weather_data_deleted": 0,
            "metrics_deleted": 0,
            "alerts_deleted": 0,
            "system_metrics_deleted": 0,
            "total_records_deleted": 0
        }

    def start(self):
        """Initialize database session"""
        self.db = create_session()
        self.cleanup_stats = {
            "weather_data_deleted": 0,
            "metrics_deleted": 0,
            "alerts_deleted": 0,
            "system_metrics_deleted": 0,
            "total_records_deleted": 0
        }

    def finish(self):
        """Close database session"""
        if self.db:
            self.db.close()
            self.db = None

    async def cleanup_old_weather_data(self, retention_days: int = 30) -> int:
        """
        Delete weather data older than retention period
        
        Args:
            retention_days: Days to keep (default: 30)
            
        Returns:
            Number of records deleted
        """
        self.start()
        deleted_count = 0

        try:
            cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
            
            logger.info(f"🗑️  Cleaning weather data older than {retention_days} days ({cutoff_date})")
            
            # Delete old weather data
            stmt = delete(WeatherData).where(WeatherData.created_at < cutoff_date)
            result = self.db.execute(stmt)
            deleted_count = result.rowcount
            self.db.commit()
            
            self.cleanup_stats["weather_data_deleted"] = deleted_count
            self.cleanup_stats["total_records_deleted"] += deleted_count
            
            logger.info(f"✅ Deleted {deleted_count} old weather records")
            return deleted_count

        except Exception as e:
            logger.error(f"Error cleaning weather data: {e}")
            self.db.rollback()
            return 0
        finally:
            self.finish()

    async def cleanup_old_metrics(self, retention_days: int = 90) -> int:
        """
        Delete processed metrics older than retention period
        
        Args:
            retention_days: Days to keep (default: 90)
            
        Returns:
            Number of records deleted
        """
        self.start()
        deleted_count = 0

        try:
            cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
            
            logger.info(f"🗑️  Cleaning processed metrics older than {retention_days} days")
            
            # Delete old metrics
            stmt = delete(ProcessedMetrics).where(ProcessedMetrics.created_at < cutoff_date)
            result = self.db.execute(stmt)
            deleted_count = result.rowcount
            self.db.commit()
            
            self.cleanup_stats["metrics_deleted"] = deleted_count
            self.cleanup_stats["total_records_deleted"] += deleted_count
            
            logger.info(f"✅ Deleted {deleted_count} old metric records")
            return deleted_count

        except Exception as e:
            logger.error(f"Error cleaning metrics: {e}")
            self.db.rollback()
            return 0
        finally:
            self.finish()

    async def cleanup_old_alerts(self, retention_days: int = 60) -> int:
        """
        Delete resolved alerts older than retention period
        
        Args:
            retention_days: Days to keep (default: 60)
            
        Returns:
            Number of records deleted
        """
        self.start()
        deleted_count = 0

        try:
            cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
            
            logger.info(f"🗑️  Cleaning alerts older than {retention_days} days")
            
            # Delete old alerts (keep unresolved ones)
            stmt = delete(Alert).where(
                (Alert.created_at < cutoff_date) & 
                (Alert.status != "active")
            )
            result = self.db.execute(stmt)
            deleted_count = result.rowcount
            self.db.commit()
            
            self.cleanup_stats["alerts_deleted"] = deleted_count
            self.cleanup_stats["total_records_deleted"] += deleted_count
            
            logger.info(f"✅ Deleted {deleted_count} old alert records")
            return deleted_count

        except Exception as e:
            logger.error(f"Error cleaning alerts: {e}")
            self.db.rollback()
            return 0
        finally:
            self.finish()

    async def cleanup_old_system_metrics(self, retention_days: int = 30) -> int:
        """
        Delete system metrics older than retention period
        
        Args:
            retention_days: Days to keep (default: 30)
            
        Returns:
            Number of records deleted
        """
        self.start()
        deleted_count = 0

        try:
            cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
            
            logger.info(f"🗑️  Cleaning system metrics older than {retention_days} days")
            
            # Delete old system metrics
            stmt = delete(SystemMetric).where(SystemMetric.created_at < cutoff_date)
            result = self.db.execute(stmt)
            deleted_count = result.rowcount
            self.db.commit()
            
            self.cleanup_stats["system_metrics_deleted"] = deleted_count
            self.cleanup_stats["total_records_deleted"] += deleted_count
            
            logger.info(f"✅ Deleted {deleted_count} old system metric records")
            return deleted_count

        except Exception as e:
            logger.error(f"Error cleaning system metrics: {e}")
            self.db.rollback()
            return 0
        finally:
            self.finish()

    async def cleanup_all(self, 
                         weather_retention: int = 30,
                         metrics_retention: int = 90,
                         alerts_retention: int = 60,
                         system_retention: int = 30) -> Dict:
        """
        Run complete cleanup across all data types
        
        Args:
            weather_retention: Days to keep weather data (default: 30)
            metrics_retention: Days to keep metrics (default: 90)
            alerts_retention: Days to keep alerts (default: 60)
            system_retention: Days to keep system metrics (default: 30)
            
        Returns:
            Dictionary with cleanup statistics
        """
        logger.info("🧹 Starting full data cleanup cycle...")
        
        # Run all cleanup jobs
        await self.cleanup_old_weather_data(weather_retention)
        await self.cleanup_old_metrics(metrics_retention)
        await self.cleanup_old_alerts(alerts_retention)
        await self.cleanup_old_system_metrics(system_retention)
        
        logger.info(f"📊 Cleanup complete - Total deleted: {self.cleanup_stats['total_records_deleted']} records")
        return self.cleanup_stats

    async def get_data_size_info(self) -> Dict:
        """
        Get information about database size and data distribution
        
        Returns:
            Dictionary with size statistics
        """
        self.start()

        try:
            info = {
                "weather_data_count": self.db.query(WeatherData).count(),
                "metrics_count": self.db.query(ProcessedMetrics).count(),
                "alerts_count": self.db.query(Alert).count(),
                "system_metrics_count": self.db.query(SystemMetric).count(),
            }
            
            # Get date ranges
            weather_old = self.db.query(WeatherData).order_by(WeatherData.created_at).first()
            weather_new = self.db.query(WeatherData).order_by(WeatherData.created_at.desc()).first()
            
            if weather_old:
                info["weather_data_date_range"] = {
                    "oldest": weather_old.created_at,
                    "newest": weather_new.created_at if weather_new else None
                }
            
            return info

        except Exception as e:
            logger.error(f"Error getting data size info: {e}")
            return {}
        finally:
            self.finish()


# Global instance
data_cleanup: DataCleanup = None


def get_data_cleanup() -> DataCleanup:
    """Get or create global cleanup instance"""
    global data_cleanup
    if data_cleanup is None:
        data_cleanup = DataCleanup()
    return data_cleanup
