"""
Anomaly detection module
Detects unusual weather patterns and events
"""
from typing import List, Optional, Tuple
from datetime import datetime, timedelta
import statistics

from sqlalchemy.orm import Session

from src.database.models import WeatherData, Alert
from src.database.repository import AlertRepository, WeatherDataRepository
from src.utils.logger import logger


class AnomalyDetector:
    """Detects anomalies in weather data"""

    # Standard deviation multiplier for anomaly detection
    ANOMALY_THRESHOLD = 3.0

    @staticmethod
    def detect_temperature_anomaly(
        current_temp: float,
        historical_data: List[WeatherData]
    ) -> Tuple[bool, Optional[float]]:
        """
        Detect temperature anomaly using statistical method
        
        Args:
            current_temp: Current temperature reading
            historical_data: Previous temperature readings
            
        Returns:
            Tuple of (is_anomaly, z_score)
        """
        if len(historical_data) < 10:
            return False, None

        temps = [d.temperature for d in historical_data]
        mean = statistics.mean(temps)
        stdev = statistics.stdev(temps) if len(temps) > 1 else 0

        if stdev == 0:
            return False, None

        # Calculate Z-score
        z_score = abs((current_temp - mean) / stdev)

        # Consider anomaly if beyond threshold
        is_anomaly = z_score > AnomalyDetector.ANOMALY_THRESHOLD

        return is_anomaly, z_score

    @staticmethod
    def detect_humidity_anomaly(
        current_humidity: int,
        historical_data: List[WeatherData]
    ) -> Tuple[bool, Optional[float]]:
        """Detect humidity anomaly using statistical method"""
        if len(historical_data) < 10:
            return False, None

        humidities = [d.humidity for d in historical_data]
        mean = statistics.mean(humidities)
        stdev = statistics.stdev(humidities) if len(humidities) > 1 else 0

        if stdev == 0:
            return False, None

        z_score = abs((current_humidity - mean) / stdev)
        is_anomaly = z_score > AnomalyDetector.ANOMALY_THRESHOLD

        return is_anomaly, z_score

    @staticmethod
    def detect_wind_anomaly(
        current_wind: float,
        historical_data: List[WeatherData]
    ) -> Tuple[bool, Optional[float]]:
        """Detect wind speed anomaly using statistical method"""
        if len(historical_data) < 10:
            return False, None

        winds = [d.wind_speed for d in historical_data]
        mean = statistics.mean(winds)
        stdev = statistics.stdev(winds) if len(winds) > 1 else 0

        if stdev == 0:
            return False, None

        z_score = abs((current_wind - mean) / stdev)
        is_anomaly = z_score > AnomalyDetector.ANOMALY_THRESHOLD

        return is_anomaly, z_score

    @staticmethod
    def detect_rapid_temperature_change(
        current_temp: float,
        previous_temp: float,
        threshold: float = 5.0  # 5°C change
    ) -> bool:
        """
        Detect rapid temperature change
        
        Args:
            current_temp: Current temperature
            previous_temp: Previous temperature
            threshold: Temperature change threshold in °C
            
        Returns:
            True if change exceeds threshold
        """
        temp_change = abs(current_temp - previous_temp)
        return temp_change > threshold

    @staticmethod
    def detect_all_anomalies(
        db: Session,
        location_id: int,
        current_weather: dict
    ) -> List[Tuple[str, str, float]]:
        """
        Detect all anomalies for current weather data
        
        Args:
            db: Database session
            location_id: Location ID
            current_weather: Current weather data dictionary
            
        Returns:
            List of tuples: (anomaly_type, description, severity)
        """
        anomalies = []

        # Get historical data (last 30 days)
        history_start = datetime.utcnow() - timedelta(days=30)
        historical_data = db.query(WeatherData).filter(
            WeatherData.location_id == location_id,
            WeatherData.recorded_at >= history_start
        ).all()

        if not historical_data:
            return anomalies

        # Check temperature anomaly
        is_temp_anomaly, temp_zscore = AnomalyDetector.detect_temperature_anomaly(
            current_weather.get("temperature", 0),
            historical_data
        )
        if is_temp_anomaly:
            anomalies.append((
                "temperature_anomaly",
                f"Unusual temperature: {current_weather['temperature']}°C (Z-score: {temp_zscore:.2f})",
                min(temp_zscore / AnomalyDetector.ANOMALY_THRESHOLD, 1.0)  # Normalized 0-1
            ))

        # Check humidity anomaly
        is_humidity_anomaly, humidity_zscore = AnomalyDetector.detect_humidity_anomaly(
            current_weather.get("humidity", 50),
            historical_data
        )
        if is_humidity_anomaly:
            anomalies.append((
                "humidity_anomaly",
                f"Unusual humidity: {current_weather['humidity']}% (Z-score: {humidity_zscore:.2f})",
                min(humidity_zscore / AnomalyDetector.ANOMALY_THRESHOLD, 1.0)
            ))

        # Check wind anomaly
        is_wind_anomaly, wind_zscore = AnomalyDetector.detect_wind_anomaly(
            current_weather.get("wind_speed", 0),
            historical_data
        )
        if is_wind_anomaly:
            anomalies.append((
                "wind_anomaly",
                f"Unusual wind: {current_weather['wind_speed']} km/h (Z-score: {wind_zscore:.2f})",
                min(wind_zscore / AnomalyDetector.ANOMALY_THRESHOLD, 1.0)
            ))

        # Check rapid temperature change
        if historical_data:
            last_data = max(historical_data, key=lambda x: x.recorded_at)
            if AnomalyDetector.detect_rapid_temperature_change(
                current_weather.get("temperature", 0),
                last_data.temperature,
                threshold=5.0
            ):
                temp_change = abs(current_weather["temperature"] - last_data.temperature)
                anomalies.append((
                    "rapid_temp_change",
                    f"Rapid temperature change: {temp_change:.1f}°C",
                    0.7
                ))

        return anomalies

    @staticmethod
    def create_anomaly_alert(
        db: Session,
        location_id: int,
        anomaly_type: str,
        description: str,
        severity: float
    ) -> Optional[Alert]:
        """
        Create an alert for detected anomaly
        
        Args:
            db: Database session
            location_id: Location ID
            anomaly_type: Type of anomaly
            description: Anomaly description
            severity: Severity (0-1)
            
        Returns:
            Created Alert object or None
        """
        # Map severity to alert severity level
        if severity > 0.9:
            alert_severity = "critical"
        elif severity > 0.7:
            alert_severity = "high"
        elif severity > 0.5:
            alert_severity = "medium"
        else:
            alert_severity = "low"

        try:
            alert = AlertRepository.create(
                db,
                location_id=location_id,
                alert_type=anomaly_type,
                severity=alert_severity,
                message=description,
                metric_name=anomaly_type.replace("_", " ").title(),
                metric_value=severity,
                threshold_value=AnomalyDetector.ANOMALY_THRESHOLD
            )
            logger.info(f"✅ Created {alert_severity} anomaly alert: {description}")
            return alert
        except Exception as e:
            logger.error(f"Error creating anomaly alert: {e}")
            return None
