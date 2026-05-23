"""
Main data processing pipeline
Orchestrates validation, calculation, aggregation, and anomaly detection
"""
from typing import List, Optional
from datetime import datetime

from sqlalchemy.orm import Session

from src.processor.validator import WeatherDataValidator
from src.processor.calculator import WeatherCalculator
from src.processor.aggregator import DataAggregator
from src.processor.anomaly_detector import AnomalyDetector
from src.database.models import WeatherData
from src.database.database import create_session
from src.database.repository import (
    LocationRepository,
    WeatherDataRepository,
    ProcessedMetricsRepository
)
from src.utils.logger import logger


class DataProcessingPipeline:
    """Orchestrates the complete data processing pipeline"""

    def __init__(self):
        self.db: Optional[Session] = None
        self.processed_count = 0
        self.error_count = 0

    def start(self):
        """Start the pipeline with database session"""
        self.db = create_session()
        self.processed_count = 0
        self.error_count = 0

    def finish(self):
        """Clean up database session"""
        if self.db:
            self.db.close()
            self.db = None

    async def process_recent_data(self) -> bool:
        """
        Process recently collected weather data
        Validates, calculates metrics, and detects anomalies
        
        Returns:
            True if successful
        """
        self.start()

        try:
            locations = LocationRepository.get_all(self.db, active_only=True)
            
            for location in locations:
                # Get latest weather data
                latest_weather = WeatherDataRepository.get_latest(self.db, location.id)
                
                if not latest_weather:
                    logger.warning(f"No weather data for location {location.name}")
                    continue

                # Validate data
                is_valid, error = WeatherDataValidator.validate_weather_data({
                    "temperature": latest_weather.temperature,
                    "humidity": latest_weather.humidity,
                    "wind_speed": latest_weather.wind_speed,
                    "weather_condition": latest_weather.weather_condition,
                    "pressure": latest_weather.pressure
                })

                if not is_valid:
                    logger.error(f"Data validation failed for {location.name}: {error}")
                    self.error_count += 1
                    continue

                # Process this location's data
                success = self._process_location(location.id, latest_weather)
                if success:
                    self.processed_count += 1

            logger.info(f"📊 Processing complete: {self.processed_count} processed, {self.error_count} errors")
            return self.error_count == 0

        except Exception as e:
            logger.error(f"Error in processing pipeline: {e}")
            return False
        finally:
            self.finish()

    def _process_location(self, location_id: int, latest_weather: WeatherData) -> bool:
        """
        Process data for a single location
        
        Args:
            location_id: Location ID
            latest_weather: Latest weather data
            
        Returns:
            True if successful
        """
        try:
            # 1. Calculate derived metrics
            heat_index = WeatherCalculator.calculate_heat_index(
                latest_weather.temperature,
                latest_weather.humidity
            )
            wind_chill = WeatherCalculator.calculate_wind_chill(
                latest_weather.temperature,
                latest_weather.wind_speed
            )

            logger.debug(f"Calculated heat index: {heat_index}, wind chill: {wind_chill}")

            # 2. Detect anomalies
            anomalies = AnomalyDetector.detect_all_anomalies(
                self.db,
                location_id,
                {
                    "temperature": latest_weather.temperature,
                    "humidity": latest_weather.humidity,
                    "wind_speed": latest_weather.wind_speed,
                    "weather_condition": latest_weather.weather_condition
                }
            )

            # 3. Create alerts for anomalies
            for anomaly_type, description, severity in anomalies:
                AnomalyDetector.create_anomaly_alert(
                    self.db,
                    location_id,
                    anomaly_type,
                    description,
                    severity
                )

            logger.info(f"✅ Processed location {location_id}: {len(anomalies)} anomalies detected")
            return True

        except Exception as e:
            logger.error(f"Error processing location {location_id}: {e}")
            return False

    async def aggregate_metrics(self, locations: List[int], metric_types: List[str] = None) -> int:
        """
        Aggregate weather data into processed metrics
        
        Args:
            locations: List of location IDs
            metric_types: Types to aggregate: ["hourly", "daily", "weekly"]
            
        Returns:
            Number of metrics created
        """
        if metric_types is None:
            metric_types = ["hourly", "daily", "weekly"]

        self.start()
        total_created = 0

        try:
            if "hourly" in metric_types:
                count = DataAggregator.aggregate_all_locations_hourly(self.db, locations)
                total_created += count
                logger.info(f"📊 Created {count} hourly metrics")

            if "daily" in metric_types:
                count = DataAggregator.aggregate_all_locations_daily(self.db, locations)
                total_created += count
                logger.info(f"📊 Created {count} daily metrics")

            if "weekly" in metric_types:
                count = DataAggregator.aggregate_all_locations_weekly(self.db, locations)
                total_created += count
                logger.info(f"📊 Created {count} weekly metrics")

            return total_created

        except Exception as e:
            logger.error(f"Error in metric aggregation: {e}")
            return total_created
        finally:
            self.finish()


# Global pipeline instance
processing_pipeline: Optional[DataProcessingPipeline] = None


async def get_processing_pipeline() -> DataProcessingPipeline:
    """Get or create global pipeline instance"""
    global processing_pipeline
    if processing_pipeline is None:
        processing_pipeline = DataProcessingPipeline()
    return processing_pipeline
