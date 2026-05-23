"""
Weather data calculations and trend analysis
Computes derived metrics and trends from raw data
"""
from typing import List, Optional, Tuple
from datetime import datetime, timedelta
import statistics

from src.database.models import WeatherData
from src.utils.logger import logger


class WeatherCalculator:
    """Performs calculations on weather data"""

    @staticmethod
    def calculate_heat_index(temp_celsius: float, humidity: int) -> float:
        """
        Calculate heat index (apparent temperature)
        Uses Rothfusz regression formula
        
        Args:
            temp_celsius: Temperature in Celsius
            humidity: Humidity percentage (0-100)
            
        Returns:
            Heat index in Celsius
        """
        if temp_celsius < 27 or humidity < 40:
            return temp_celsius  # Heat index only relevant for high temp/humidity

        # Convert to Fahrenheit
        t = (temp_celsius * 9/5) + 32
        rh = float(humidity)

        # Rothfusz regression coefficients
        hi = (
            -42.379 + 2.04901523 * t + 10.14333127 * rh
            - 0.22475541 * t * rh
            - 0.00683783 * t * t
            - 0.05481717 * rh * rh
            + 0.00122874 * t * t * rh
            + 0.00085282 * t * rh * rh
            - 0.00000199 * t * t * rh * rh
        )

        # Convert back to Celsius
        return round((hi - 32) * 5/9, 2)

    @staticmethod
    def calculate_wind_chill(temp_celsius: float, wind_speed_kmh: float) -> Optional[float]:
        """
        Calculate wind chill factor
        Only applicable when temp < 10°C and wind > 4.8 km/h
        
        Args:
            temp_celsius: Temperature in Celsius
            wind_speed_kmh: Wind speed in km/h
            
        Returns:
            Wind chill in Celsius, or None if not applicable
        """
        if temp_celsius >= 10 or wind_speed_kmh <= 4.8:
            return None

        # Convert to knots for calculation
        wind_knots = wind_speed_kmh / 1.852

        # Wind chill formula
        wc = 13.12 + 0.6215 * temp_celsius - 11.37 * (wind_knots ** 0.16) + \
             0.3965 * temp_celsius * (wind_knots ** 0.16)

        return round(wc, 2)

    @staticmethod
    def calculate_dew_point(temp_celsius: float, humidity: int) -> float:
        """
        Calculate dew point temperature
        
        Args:
            temp_celsius: Temperature in Celsius
            humidity: Humidity percentage (0-100)
            
        Returns:
            Dew point in Celsius
        """
        if humidity == 0:
            return None

        # Magnus formula approximation
        a = 17.27
        b = 237.7
        alpha = ((a * temp_celsius) / (b + temp_celsius)) + (np.log(humidity / 100))
        dew_point = (b * alpha) / (a - alpha)

        return round(dew_point, 2)

    @staticmethod
    def calculate_temperature_trend(measurements: List[WeatherData]) -> Optional[str]:
        """
        Determine temperature trend from measurements
        
        Args:
            measurements: List of WeatherData objects sorted by time
            
        Returns:
            "increasing", "decreasing", "stable", or None
        """
        if len(measurements) < 2:
            return None

        temps = [m.temperature for m in measurements]
        first_third = statistics.mean(temps[:len(temps)//3])
        last_third = statistics.mean(temps[-len(temps)//3:])

        diff = last_third - first_third
        threshold = 2.0  # 2°C threshold for change

        if diff > threshold:
            return "increasing"
        elif diff < -threshold:
            return "decreasing"
        else:
            return "stable"

    @staticmethod
    def calculate_statistics(measurements: List[WeatherData]) -> dict:
        """
        Calculate statistics from multiple measurements
        
        Args:
            measurements: List of WeatherData objects
            
        Returns:
            Dictionary with statistics
        """
        if not measurements:
            return {}

        temps = [m.temperature for m in measurements]
        humidities = [m.humidity for m in measurements]
        winds = [m.wind_speed for m in measurements]

        return {
            "temperature": {
                "min": round(min(temps), 1),
                "max": round(max(temps), 1),
                "avg": round(statistics.mean(temps), 1),
                "stdev": round(statistics.stdev(temps), 1) if len(temps) > 1 else 0,
            },
            "humidity": {
                "min": min(humidities),
                "max": max(humidities),
                "avg": round(statistics.mean(humidities), 1),
            },
            "wind": {
                "min": round(min(winds), 1),
                "max": round(max(winds), 1),
                "avg": round(statistics.mean(winds), 1),
            },
            "count": len(measurements),
        }

    @staticmethod
    def calculate_comfort_index(temp: float, humidity: int, wind: float) -> str:
        """
        Calculate comfort level based on multiple factors
        
        Args:
            temp: Temperature in Celsius
            humidity: Humidity percentage
            wind: Wind speed in km/h
            
        Returns:
            Comfort level: "cold", "cool", "comfortable", "warm", "hot"
        """
        # Heat index consideration
        heat_index = WeatherCalculator.calculate_heat_index(temp, humidity)

        # Wind chill consideration
        wind_chill = WeatherCalculator.calculate_wind_chill(temp, wind)

        # Determine effective temperature
        if wind_chill is not None:
            effective_temp = wind_chill
        else:
            effective_temp = heat_index

        # Classify comfort
        if effective_temp < 0:
            return "cold"
        elif effective_temp < 15:
            return "cool"
        elif effective_temp < 25:
            return "comfortable"
        elif effective_temp < 35:
            return "warm"
        else:
            return "hot"


# Note: Import numpy for dew point calculation
try:
    import numpy as np
except ImportError:
    logger.warning("NumPy not available for advanced calculations")
    np = None
