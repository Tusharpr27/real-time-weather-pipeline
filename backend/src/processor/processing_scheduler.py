"""
Processing job scheduler
Runs data processing pipeline on a schedule
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
import asyncio

from config import settings
from src.processor.pipeline import get_processing_pipeline
from src.database.database import create_session
from src.database.repository import LocationRepository
from src.utils.logger import logger


class ProcessingScheduler:
    """Manages scheduled data processing jobs"""

    def __init__(self):
        self.scheduler: AsyncIOScheduler = None
        self.jobs_map = {
            "process_recent": "process_recent_job",
            "aggregate_hourly": "aggregate_hourly_job",
            "aggregate_daily": "aggregate_daily_job",
            "aggregate_weekly": "aggregate_weekly_job"
        }

    def initialize(self):
        """Initialize the scheduler"""
        self.scheduler = AsyncIOScheduler()
        logger.info("✅ Data processing scheduler initialized")

    async def start(self):
        """Start the processing scheduler"""
        if not self.scheduler:
            self.initialize()

        # Job 1: Process recent data (every hour)
        self.scheduler.add_job(
            self._process_recent_task,
            trigger=IntervalTrigger(hours=1),
            id=self.jobs_map["process_recent"],
            name="Process recent weather data",
            replace_existing=True
        )

        # Job 2: Aggregate hourly metrics (every 2 hours)
        self.scheduler.add_job(
            self._aggregate_hourly_task,
            trigger=IntervalTrigger(hours=2),
            id=self.jobs_map["aggregate_hourly"],
            name="Aggregate hourly metrics",
            replace_existing=True
        )

        # Job 3: Aggregate daily metrics (daily at 01:00 UTC)
        self.scheduler.add_job(
            self._aggregate_daily_task,
            trigger="cron",
            hour=1,
            minute=0,
            id=self.jobs_map["aggregate_daily"],
            name="Aggregate daily metrics",
            replace_existing=True
        )

        # Job 4: Aggregate weekly metrics (every Monday at 02:00 UTC)
        self.scheduler.add_job(
            self._aggregate_weekly_task,
            trigger="cron",
            day_of_week="mon",
            hour=2,
            minute=0,
            id=self.jobs_map["aggregate_weekly"],
            name="Aggregate weekly metrics",
            replace_existing=True
        )

        self.scheduler.start()
        logger.info("🚀 Data processing scheduler started with 4 jobs")

    async def stop(self):
        """Stop the scheduler"""
        if self.scheduler and self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("🛑 Data processing scheduler stopped")

    async def _process_recent_task(self):
        """Background task to process recent weather data"""
        try:
            logger.info("📡 Starting recent data processing...")
            pipeline = await get_processing_pipeline()
            success = await pipeline.process_recent_data()
            
            if success:
                logger.info("✅ Recent data processing completed successfully")
            else:
                logger.warning("⚠️  Recent data processing completed with errors")
                
        except Exception as e:
            logger.error(f"❌ Error in recent data processing task: {e}")

    async def _aggregate_hourly_task(self):
        """Background task to aggregate hourly metrics"""
        try:
            logger.info("📊 Aggregating hourly metrics...")
            db = create_session()
            
            try:
                locations = LocationRepository.get_all(db, active_only=True)
                location_ids = [loc.id for loc in locations]
                
                pipeline = await get_processing_pipeline()
                count = await pipeline.aggregate_metrics(location_ids, ["hourly"])
                
                logger.info(f"✅ Hourly aggregation complete: {count} metrics created")
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"❌ Error in hourly aggregation task: {e}")

    async def _aggregate_daily_task(self):
        """Background task to aggregate daily metrics"""
        try:
            logger.info("📊 Aggregating daily metrics...")
            db = create_session()
            
            try:
                locations = LocationRepository.get_all(db, active_only=True)
                location_ids = [loc.id for loc in locations]
                
                pipeline = await get_processing_pipeline()
                count = await pipeline.aggregate_metrics(location_ids, ["daily"])
                
                logger.info(f"✅ Daily aggregation complete: {count} metrics created")
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"❌ Error in daily aggregation task: {e}")

    async def _aggregate_weekly_task(self):
        """Background task to aggregate weekly metrics"""
        try:
            logger.info("📊 Aggregating weekly metrics...")
            db = create_session()
            
            try:
                locations = LocationRepository.get_all(db, active_only=True)
                location_ids = [loc.id for loc in locations]
                
                pipeline = await get_processing_pipeline()
                count = await pipeline.aggregate_metrics(location_ids, ["weekly"])
                
                logger.info(f"✅ Weekly aggregation complete: {count} metrics created")
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"❌ Error in weekly aggregation task: {e}")


# Global scheduler instance
processing_scheduler: ProcessingScheduler = None


def get_processing_scheduler() -> ProcessingScheduler:
    """Get or create global processing scheduler instance"""
    global processing_scheduler
    if processing_scheduler is None:
        processing_scheduler = ProcessingScheduler()
        processing_scheduler.initialize()
    return processing_scheduler
