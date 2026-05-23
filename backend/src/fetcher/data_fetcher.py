"""
Data fetcher service
Continuously fetches weather data from API and stores in database
"""
import asyncio
from typing import List, Optional
from datetime import datetime

from config import settings
from src.fetcher.weather_client import get_weather_client
from src.database.database import create_session
from src.database.repository import (
    LocationRepository,
    WeatherDataRepository,
    SystemMetricRepository
)
from src.utils.logger import logger


class WeatherDataFetcher:
    """Service to fetch and store weather data"""

    def __init__(self):
        self.provider = settings.weather_api_provider
        self.api_key = settings.weather_api_key
        self.locations: List = []
        self.running = False

    async def initialize(self):
        """Initialize fetcher with locations from database"""
        db = create_session()
        try:
            self.locations = LocationRepository.get_all(db, active_only=True)
            logger.info(f"âœ… Initialized fetcher with {len(self.locations)} locations")
        except Exception as e:
            logger.error(f"âŒ Error initializing fetcher: {e}")
        finally:
            db.close()

    async def fetch_weather_for_all_locations(self) -> bool:
        """
        Fetch weather data for all configured locations
        
        Returns:
            True if successful, False otherwise
        """
        if not self.locations:
            logger.warning("No locations configured")
            return False

        db = create_session()
        successful_fetches = 0
        failed_fetches = 0

        try:
            client = await get_weather_client(self.provider, self.api_key)
            
            async with client:
                for location in self.locations:
                    try:
                        weather_data = await client.get_current_weather(
                            location.latitude,
                            location.longitude
                        )

                        if weather_data:
                            self._save_weather_data(db, location.id, weather_data)
                            successful_fetches += 1
                            logger.info(f"âœ… Fetched weather for {location.name}")
                        else:
                            failed_fetches += 1
                            logger.warning(f"âš ï¸  Failed to fetch weather for {location.name}")

                    except Exception as e:
                        failed_fetches += 1
                        logger.error(f"âŒ Error fetching weather for {location.name}: {e}")

                    # Small delay between API calls to avoid rate limiting
                    await asyncio.sleep(0.5)

            # Log system metrics
            self._log_system_metrics(db, successful_fetches, failed_fetches)

            logger.info(f"âœ… Weather fetch cycle complete: {successful_fetches} successful, {failed_fetches} failed")
            return failed_fetches == 0

        except Exception as e:
            logger.error(f"âŒ Error in fetch cycle: {e}")
            return False
        finally:
            db.close()

    def _save_weather_data(self, db, location_id: int, weather_data: dict):
        """Save weather data to database"""
        try:
            WeatherDataRepository.create(
                db,
                location_id=location_id,
                temperature=weather_data.get("temperature", 0),
                humidity=weather_data.get("humidity", 0),
                wind_speed=weather_data.get("wind_speed", 0),
                weather_condition=weather_data.get("weather_condition", "Unknown"),
                feels_like=weather_data.get("feels_like"),
                temp_min=weather_data.get("temp_min"),
                temp_max=weather_data.get("temp_max"),
                pressure=weather_data.get("pressure"),
                wind_direction=weather_data.get("wind_direction"),
                wind_gust=weather_data.get("wind_gust"),
                rainfall=weather_data.get("rainfall"),
                snowfall=weather_data.get("snowfall"),
                description=weather_data.get("description"),
                visibility=weather_data.get("visibility"),
                uv_index=weather_data.get("uv_index"),
                cloud_coverage=weather_data.get("cloud_coverage"),
                recorded_at=weather_data.get("timestamp", datetime.utcnow())
            )
        except Exception as e:
            logger.error(f"Error saving weather data for location {location_id}: {e}")

    def _log_system_metrics(self, db, successful: int, failed: int):
        """Log system metrics for monitoring"""
        try:
            SystemMetricRepository.create(
                db,
                total_api_calls=successful + failed,
                successful_api_calls=successful,
                failed_api_calls=failed,
                last_successful_sync=datetime.utcnow()
            )
        except Exception as e:
            logger.error(f"Error logging system metrics: {e}")

    async def start(self):
        """Start fetching weather data"""
        self.running = True
        logger.info("ðŸš€ Weather data fetcher started")

    async def stop(self):
        """Stop fetching weather data"""
        self.running = False
        logger.info("ðŸ›‘ Weather data fetcher stopped")


# Global fetcher instance
fetcher: Optional[WeatherDataFetcher] = None


async def get_fetcher() -> WeatherDataFetcher:
    """Get or create global fetcher instance"""
    global fetcher
    if fetcher is None:
        fetcher = WeatherDataFetcher()
        await fetcher.initialize()
    return fetcher

