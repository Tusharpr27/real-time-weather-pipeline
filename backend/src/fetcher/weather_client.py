"""
Weather API client abstraction
Supports multiple weather providers (Open-Meteo, OpenWeatherMap, etc.)
"""
import aiohttp
from typing import Dict, Optional, List
from abc import ABC, abstractmethod
from datetime import datetime

from src.utils.logger import logger


class WeatherClient(ABC):
    """Abstract base class for weather API clients"""

    @abstractmethod
    async def get_current_weather(self, latitude: float, longitude: float) -> Dict:
        """Get current weather data"""
        pass

    @abstractmethod
    async def get_weather_by_location(self, location_name: str) -> Dict:
        """Get weather by location name"""
        pass


class OpenMeteoClient(WeatherClient):
    """Open-Meteo weather API client - Free unlimited tier"""

    def __init__(self):
        self.base_url = "https://api.open-meteo.com/v1"
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()

    async def _ensure_session(self):
        """Ensure session exists"""
        if not self.session:
            self.session = aiohttp.ClientSession()

    async def get_current_weather(self, latitude: float, longitude: float) -> Dict:
        """
        Get current weather from Open-Meteo API
        
        Args:
            latitude: Location latitude
            longitude: Location longitude
            
        Returns:
            Dictionary with weather data
        """
        await self._ensure_session()

        url = f"{self.base_url}/forecast"
        # Request current weather and hourly fields we need (humidity, pressure, cloudcover, precipitation)
        params = {
            "latitude": latitude,
            "longitude": longitude,
            # Open-Meteo expects 'current_weather' as a truthy value in the query string
            "current_weather": "true",
            "hourly": "relativehumidity_2m,pressure_msl,cloudcover,precipitation",
            "timezone": "auto"
        }

        try:
            async with self.session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_response(data)
                else:
                    logger.error(f"API error: {response.status} when calling Open-Meteo")
                    return None
        except Exception as e:
            logger.error(f"Error fetching weather from Open-Meteo: {e}")
            return None

    async def get_weather_by_location(self, location_name: str) -> Dict:
        """
        Get coordinates from location name, then fetch weather
        
        Args:
            location_name: Name of the location
            
        Returns:
            Dictionary with weather data
        """
        # This would require geocoding API
        # For now, using predefined locations
        raise NotImplementedError("Use get_current_weather with known coordinates")

    def _parse_response(self, data: Dict) -> Dict:
        """
        Parse Open-Meteo API response into a standardized dictionary
        """
        if not data:
            return None

        # Current weather block
        current = data.get("current_weather")
        timestamp_str = None
        temperature = None
        wind_speed = None
        wind_direction = None
        weather_code = None

        if current:
            timestamp_str = current.get("time")
            temperature = current.get("temperature")
            wind_speed = current.get("windspeed")
            wind_direction = current.get("winddirection")
            weather_code = current.get("weathercode")

        # Try to get hourly series values (humidity, pressure, clouds, precipitation)
        humidity = None
        pressure = None
        cloud_coverage = None
        precipitation = None

        hourly = data.get("hourly", {})
        times = hourly.get("time", []) if hourly else []

        idx = None
        if timestamp_str and times:
            try:
                idx = times.index(timestamp_str)
            except ValueError:
                # Fallback: pick the most recent index
                idx = len(times) - 1 if times else None
        elif times:
            idx = len(times) - 1

        if idx is not None and idx >= 0:
            rh = hourly.get("relativehumidity_2m", [])
            if rh and idx < len(rh):
                humidity = rh[idx]

            prs = hourly.get("pressure_msl", [])
            if prs and idx < len(prs):
                pressure = prs[idx]

            cloud = hourly.get("cloudcover", [])
            if cloud and idx < len(cloud):
                cloud_coverage = cloud[idx]

            precip = hourly.get("precipitation", [])
            if precip and idx < len(precip):
                precipitation = precip[idx]

        # Convert timestamp string to datetime if possible
        timestamp = None
        if timestamp_str:
            try:
                # handle trailing Z by converting to +00:00
                ts = timestamp_str.replace("Z", "+00:00")
                timestamp = datetime.fromisoformat(ts)
            except Exception:
                timestamp = datetime.utcnow()
        else:
            timestamp = datetime.utcnow()

        weather_condition = self._get_weather_condition(weather_code if weather_code is not None else 0)

        return {
            "temperature": temperature,
            "feels_like": None,
            "temp_min": None,
            "temp_max": None,
            "humidity": humidity,
            "pressure": pressure,
            "wind_speed": wind_speed,
            "wind_direction": wind_direction,
            "wind_gust": None,
            "weather_condition": weather_condition,
            "description": None,
            "cloud_coverage": cloud_coverage,
            "visibility": None,
            "uv_index": None,
            "rainfall": precipitation,
            "snowfall": None,
            "timestamp": timestamp,
            "timezone": data.get("timezone")
        }

    @staticmethod
    def _get_weather_condition(code: int) -> str:
        """
        Convert WMO weather code to condition
        https://www.open-meteo.com/en/docs
        """
        weather_codes = {
            0: "Clear sky",
            1: "Mainly clear",
            2: "Partly cloudy",
            3: "Overcast",
            45: "Fog",
            48: "Depositing rime fog",
            51: "Light drizzle",
            53: "Moderate drizzle",
            55: "Dense drizzle",
            61: "Slight rain",
            63: "Moderate rain",
            65: "Heavy rain",
            71: "Slight snow",
            73: "Moderate snow",
            75: "Heavy snow",
            77: "Snow grains",
            80: "Slight rain showers",
            81: "Moderate rain showers",
            82: "Violent rain showers",
            85: "Slight snow showers",
            86: "Heavy snow showers",
            95: "Thunderstorm",
            96: "Thunderstorm with slight hail",
            99: "Thunderstorm with heavy hail",
        }
        return weather_codes.get(code, "Unknown")


class OpenWeatherMapClient(WeatherClient):
    """OpenWeatherMap API client"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.openweathermap.org/data/2.5"
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()

    async def _ensure_session(self):
        """Ensure session exists"""
        if not self.session:
            self.session = aiohttp.ClientSession()

    async def get_current_weather(self, latitude: float, longitude: float) -> Dict:
        """Get current weather from OpenWeatherMap"""
        await self._ensure_session()

        url = f"{self.base_url}/weather"
        params = {
            "lat": latitude,
            "lon": longitude,
            "appid": self.api_key,
            "units": "metric"
        }

        try:
            async with self.session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_response(data)
                else:
                    logger.error(f"API error: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Error fetching weather: {e}")
            return None

    async def get_weather_by_location(self, location_name: str) -> Dict:
        """Get weather by location name"""
        raise NotImplementedError("Use get_current_weather with known coordinates")

    def _parse_response(self, data: Dict) -> Dict:
        """Parse OpenWeatherMap response"""
        if not data:
            return None

        main = data.get("main", {})
        wind = data.get("wind", {})
        clouds = data.get("clouds", {})
        weather_info = data.get("weather", [{}])[0]

        return {
            "temperature": main.get("temp"),
            "feels_like": main.get("feels_like"),
            "temp_min": main.get("temp_min"),
            "temp_max": main.get("temp_max"),
            "humidity": main.get("humidity"),
            "pressure": main.get("pressure"),
            "wind_speed": wind.get("speed"),
            "wind_direction": wind.get("deg"),
            "wind_gust": wind.get("gust"),
            "weather_condition": weather_info.get("main", "Unknown"),
            "description": weather_info.get("description"),
            "cloud_coverage": clouds.get("all"),
            "visibility": data.get("visibility"),
            "timestamp": datetime.now()
        }


async def get_weather_client(provider: str = "open-meteo", api_key: str = "") -> WeatherClient:
    """
    Factory function to get weather client
    
    Args:
        provider: Weather API provider name
        api_key: API key (if required)
        
    Returns:
        Configured weather client
    """
    if provider.lower() == "open-meteo":
        return OpenMeteoClient()
    elif provider.lower() == "openweathermap":
        return OpenWeatherMapClient(api_key)
    else:
        raise ValueError(f"Unknown weather provider: {provider}")
