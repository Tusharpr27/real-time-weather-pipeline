"""
Storage scheduler module
Manages background jobs for cleanup, archiving, and optimization
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
import asyncio

from config import settings
from src.storage.data_cleanup import get_data_cleanup
from src.storage.archive_manager import get_archive_manager
from src.storage.db_optimizer import get_db_optimizer
from src.storage.retention_policy import get_retention_policy_manager
from src.utils.logger import logger


class StorageScheduler:
    """Manages scheduled storage optimization jobs"""

    def __init__(self):
        self.scheduler: AsyncIOScheduler = None
        self.retention_policy = get_retention_policy_manager()

    def initialize(self):
        """Initialize the scheduler"""
        self.scheduler = AsyncIOScheduler()
        logger.info("✅ Storage scheduler initialized")

    async def start(self):
        """Start the storage scheduler"""
        if not self.scheduler:
            self.initialize()

        # Job 1: Daily cleanup of old data (runs at 02:00 UTC)
        self.scheduler.add_job(
            self._daily_cleanup_task,
            trigger=CronTrigger(hour=2, minute=0),
            id="daily_cleanup",
            name="Daily data cleanup",
            replace_existing=True
        )

        # Job 2: Weekly archiving (runs on Sunday at 03:00 UTC)
        self.scheduler.add_job(
            self._weekly_archive_task,
            trigger=CronTrigger(day_of_week="sun", hour=3, minute=0),
            id="weekly_archive",
            name="Weekly metrics archiving",
            replace_existing=True
        )

        # Job 3: Daily database optimization (runs at 04:00 UTC)
        self.scheduler.add_job(
            self._daily_optimization_task,
            trigger=CronTrigger(hour=4, minute=0),
            id="daily_optimization",
            name="Database optimization",
            replace_existing=True
        )

        # Job 4: Archive rotation - keep only last N archives (weekly)
        self.scheduler.add_job(
            self._archive_rotation_task,
            trigger=CronTrigger(day_of_week="sat", hour=3, minute=0),
            id="archive_rotation",
            name="Archive rotation",
            replace_existing=True
        )

        self.scheduler.start()
        logger.info("🚀 Storage scheduler started with 4 jobs")

    async def stop(self):
        """Stop the scheduler"""
        if self.scheduler and self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("🛑 Storage scheduler stopped")

    async def _daily_cleanup_task(self):
        """Background task to cleanup old data"""
        try:
            logger.info("🧹 Starting daily cleanup task...")
            
            cleanup = get_data_cleanup()
            policy = self.retention_policy
            
            # Get retention days from policy
            weather_retention = policy.get_retention_days("weather")
            metrics_retention = policy.get_retention_days("daily_metrics")
            alerts_retention = policy.get_retention_days("alerts")
            system_retention = policy.get_retention_days("system_metrics")
            
            # Run cleanup
            stats = await cleanup.cleanup_all(
                weather_retention=weather_retention,
                metrics_retention=metrics_retention,
                alerts_retention=alerts_retention,
                system_retention=system_retention
            )
            
            logger.info(f"✅ Daily cleanup completed: {stats['total_records_deleted']} records deleted")
            
        except Exception as e:
            logger.error(f"❌ Error in daily cleanup task: {e}")

    async def _weekly_archive_task(self):
        """Background task to archive weekly metrics"""
        try:
            logger.info("📦 Starting weekly archiving task...")
            
            archive_mgr = get_archive_manager()
            
            # Export weekly metrics
            metrics_file = await archive_mgr.export_weekly_metrics(compress=True)
            
            # Export alerts
            alerts_file = await archive_mgr.export_alerts(days=7, compress=True)
            
            logger.info(f"✅ Weekly archiving completed")
            logger.info(f"   Metrics archive: {metrics_file}")
            logger.info(f"   Alerts archive: {alerts_file}")
            
        except Exception as e:
            logger.error(f"❌ Error in weekly archiving task: {e}")

    async def _daily_optimization_task(self):
        """Background task to optimize database"""
        try:
            logger.info("🔧 Starting database optimization task...")
            
            optimizer = get_db_optimizer()
            results = await optimizer.optimize_all()
            
            logger.info(f"✅ Database optimization completed: {results}")
            
        except Exception as e:
            logger.error(f"❌ Error in optimization task: {e}")

    async def _archive_rotation_task(self):
        """Background task to rotate archives"""
        try:
            logger.info("🔄 Starting archive rotation task...")
            
            archive_mgr = get_archive_manager()
            policy = self.retention_policy
            
            # Rotate archives based on policy
            deleted = await archive_mgr.rotate_archives(
                max_count=policy.policy.max_archives_to_keep
            )
            
            logger.info(f"✅ Archive rotation completed: {deleted} archives deleted")
            
        except Exception as e:
            logger.error(f"❌ Error in archive rotation task: {e}")


# Global scheduler instance
storage_scheduler: StorageScheduler = None


def get_storage_scheduler() -> StorageScheduler:
    """Get or create global storage scheduler instance"""
    global storage_scheduler
    if storage_scheduler is None:
        storage_scheduler = StorageScheduler()
        storage_scheduler.initialize()
    return storage_scheduler
