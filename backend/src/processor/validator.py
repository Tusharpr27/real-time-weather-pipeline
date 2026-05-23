"""
Data validation and cleaning module
Ensures data quality before processing
"""
from typing import Optional, Tuple
from datetime import datetime

from src.utils.logger import logger


class WeatherDataValidator:
    """Validates and cleans weather data"""

    # Valid ranges for different metrics
    TEMP_MIN = -100  # °C
    TEMP_MAX = 60    # °C
    HUMIDITY_MIN = 0
    HUMIDITY_MAX = 100
    WIND_SPEED_MAX = 400  # km/h (hurricane speed limit)
    PRESSURE_MIN = 850    # hPa (minimum sea-level pressure)
    PRESSURE_MAX = 1050   # hPa (maximum sea-level pressure)
    VISIBILITY_MAX = 100000  # meters
    UV_INDEX_MAX = 20

    @staticmethod
    def validate_temperature(temp: Optional[float]) -> Tuple[bool, Optional[str]]:
        """
        Validate temperature value
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if temp is None:
            return False, "Temperature is required"
        
        if not isinstance(temp, (int, float)):
            return False, f"Temperature must be numeric, got {type(temp)}"
        
        if temp < WeatherDataValidator.TEMP_MIN or temp > WeatherDataValidator.TEMP_MAX:
            return False, f"Temperature {temp}°C out of valid range [{WeatherDataValidator.TEMP_MIN}, {WeatherDataValidator.TEMP_MAX}]"
        
        return True, None

    @staticmethod
    def validate_humidity(humidity: Optional[int]) -> Tuple[bool, Optional[str]]:
        """Validate humidity (0-100%)"""
        if humidity is None:
            return False, "Humidity is required"
        
        if not isinstance(humidity, (int, float)):
            return False, f"Humidity must be numeric, got {type(humidity)}"
        
        if humidity < WeatherDataValidator.HUMIDITY_MIN or humidity > WeatherDataValidator.HUMIDITY_MAX:
            return False, f"Humidity {humidity}% out of range [0-100]"
        
        return True, None

    @staticmethod
    def validate_wind_speed(wind_speed: Optional[float]) -> Tuple[bool, Optional[str]]:
        """Validate wind speed"""
        if wind_speed is None:
            return False, "Wind speed is required"
        
        if not isinstance(wind_speed, (int, float)):
            return False, f"Wind speed must be numeric, got {type(wind_speed)}"
        
        if wind_speed < 0 or wind_speed > WeatherDataValidator.WIND_SPEED_MAX:
            return False, f"Wind speed {wind_speed} km/h out of range [0-{WeatherDataValidator.WIND_SPEED_MAX}]"
        
        return True, None

    @staticmethod
    def validate_pressure(pressure: Optional[float]) -> Tuple[bool, Optional[str]]:
        """Validate atmospheric pressure"""
        if pressure is None:
            return True, None  # Optional field
        
        if not isinstance(pressure, (int, float)):
            return False, f"Pressure must be numeric, got {type(pressure)}"
        
        if pressure < WeatherDataValidator.PRESSURE_MIN or pressure > WeatherDataValidator.PRESSURE_MAX:
            return False, f"Pressure {pressure} hPa out of range [{WeatherDataValidator.PRESSURE_MIN}-{WeatherDataValidator.PRESSURE_MAX}]"
        
        return True, None

    @staticmethod
    def validate_weather_condition(condition: Optional[str]) -> Tuple[bool, Optional[str]]:
        """Validate weather condition description"""
        if not condition:
            return False, "Weather condition is required"
        
        if not isinstance(condition, str):
            return False, f"Weather condition must be string, got {type(condition)}"
        
        if len(condition.strip()) == 0:
            return False, "Weather condition cannot be empty"
        
        if len(condition) > 100:
            return False, "Weather condition too long (max 100 chars)"
        
        return True, None

    @staticmethod
    def validate_weather_data(weather_dict: dict) -> Tuple[bool, Optional[str]]:
        """
        Validate complete weather data dictionary
        
        Args:
            weather_dict: Dictionary with weather fields
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check required fields
        required_fields = ["temperature", "humidity", "wind_speed", "weather_condition"]
        for field in required_fields:
            if field not in weather_dict:
                return False, f"Missing required field: {field}"

        # Validate each field
        temp_valid, temp_error = WeatherDataValidator.validate_temperature(
            weather_dict.get("temperature")
        )
        if not temp_valid:
            return False, f"Temperature validation: {temp_error}"

        humidity_valid, humidity_error = WeatherDataValidator.validate_humidity(
            weather_dict.get("humidity")
        )
        if not humidity_valid:
            return False, f"Humidity validation: {humidity_error}"

        wind_valid, wind_error = WeatherDataValidator.validate_wind_speed(
            weather_dict.get("wind_speed")
        )
        if not wind_valid:
            return False, f"Wind validation: {wind_error}"

        condition_valid, condition_error = WeatherDataValidator.validate_weather_condition(
            weather_dict.get("weather_condition")
        )
        if not condition_valid:
            return False, f"Condition validation: {condition_error}"

        # Validate optional fields if present
        if "pressure" in weather_dict:
            pressure_valid, pressure_error = WeatherDataValidator.validate_pressure(
                weather_dict.get("pressure")
            )
            if not pressure_valid:
                return False, f"Pressure validation: {pressure_error}"

        return True, None

    @staticmethod
    def clean_temperature(temp: float) -> float:
        """Clean/round temperature to 1 decimal place"""
        return round(float(temp), 1)

    @staticmethod
    def clean_humidity(humidity: int) -> int:
        """Ensure humidity is integer"""
        return int(max(0, min(100, humidity)))

    @staticmethod
    def clean_wind_speed(speed: float) -> float:
        """Clean wind speed to 1 decimal place"""
        return round(max(0, float(speed)), 1)

    @staticmethod
    def clean_weather_data(weather_dict: dict) -> dict:
        """
        Clean and standardize weather data
        
        Args:
            weather_dict: Raw weather data
            
        Returns:
            Cleaned weather data
        """
        cleaned = weather_dict.copy()

        # Clean numeric values
        if "temperature" in cleaned:
            cleaned["temperature"] = WeatherDataValidator.clean_temperature(cleaned["temperature"])
        
        if "humidity" in cleaned:
            cleaned["humidity"] = WeatherDataValidator.clean_humidity(cleaned["humidity"])
        
        if "wind_speed" in cleaned:
            cleaned["wind_speed"] = WeatherDataValidator.clean_wind_speed(cleaned["wind_speed"])
        
        if "pressure" in cleaned and cleaned["pressure"] is not None:
            cleaned["pressure"] = round(float(cleaned["pressure"]), 2)

        # Clean string values
        if "weather_condition" in cleaned:
            cleaned["weather_condition"] = cleaned["weather_condition"].strip()[:100]

        return cleaned

    @staticmethod
    def detect_anomalies(current_value: float, expected_range: Tuple[float, float]) -> bool:
        """
        Simple anomaly detection based on expected range
        
        Args:
            current_value: Current measurement
            expected_range: Tuple of (min, max) expected values
            
        Returns:
            True if value is anomalous
        """
        min_val, max_val = expected_range
        return current_value < min_val or current_value > max_val
