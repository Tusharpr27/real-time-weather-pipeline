"""
Scheduler service
Manages background tasks for continuous data fetching
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
import asyncio

from config import settings
from src.fetcher.data_fetcher import get_fetcher
from src.utils.logger import logger


class WeatherScheduler:
    """Manages scheduled weather data fetching"""

    def __init__(self):
        self.scheduler: AsyncIOScheduler = None
        self.job_id = "fetch_weather_job"

    def initialize(self):
        """Initialize the scheduler"""
        self.scheduler = AsyncIOScheduler()
        logger.info("âœ… Weather scheduler initialized")

    async def start(self):
        """Start the scheduler"""
        if not self.scheduler:
            self.initialize()

        # Add periodic job
        self.scheduler.add_job(
            self._fetch_weather_task,
            trigger=IntervalTrigger(minutes=settings.fetch_interval_minutes),
            id=self.job_id,
            name=f"Fetch weather every {settings.fetch_interval_minutes} minutes",
            replace_existing=True
        )

        self.scheduler.start()
        logger.info(f"ðŸš€ Weather scheduler started - fetching every {settings.fetch_interval_minutes} minutes")
        
        # Execute first fetch immediately
        asyncio.create_task(self._fetch_weather_task())

    async def stop(self):
        """Stop the scheduler"""
        if self.scheduler and self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("ðŸ›‘ Weather scheduler stopped")

    async def _fetch_weather_task(self):
        """Background task to fetch weather"""
        try:
            logger.info("ðŸ“¡ Starting scheduled weather fetch...")
            fetcher = await get_fetcher()
            success = await fetcher.fetch_weather_for_all_locations()
            
            if success:
                logger.info("âœ… Scheduled weather fetch completed successfully")
            else:
                logger.warning("âš ï¸  Scheduled weather fetch completed with errors")
                
        except Exception as e:
            logger.error(f"âŒ Error in scheduled fetch task: {e}")


# Global scheduler instance
scheduler: WeatherScheduler = None


def get_scheduler() -> WeatherScheduler:
    """Get or create global scheduler instance"""
    global scheduler
    if scheduler is None:
        scheduler = WeatherScheduler()
        scheduler.initialize()
    return scheduler

