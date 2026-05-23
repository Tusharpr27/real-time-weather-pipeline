import pytest
from src.fetcher.weather_client import OpenMeteoClient

@pytest.fixture
def test_open_meteo_response():
    """Sample API response from Open-Meteo"""
    return {
        "latitude": 52.52,
        "longitude": 13.41,
        "generationtime_ms": 0.25,
        "utc_offset_seconds": 0,
        "timezone": "auto",
        "timezone_abbreviation": "UTC",
        "elevation": 38.0,
        "current_weather": {
            "temperature": 15.0,
            "windspeed": 10.5,
            "winddirection": 200,
            "weathercode": 3,
            "time": "2024-05-18T10:00"
        },
        "hourly": {
            "time": ["2024-05-18T09:00", "2024-05-18T10:00", "2024-05-18T11:00"],
            "relativehumidity_2m": [60, 65, 55],
            "pressure_msl": [1012.0, 1011.5, 1011.0],
            "cloudcover": [10, 20, 30],
            "precipitation": [0.0, 0.5, 1.0]
        }
    }

def test_parse_valid_response(test_open_meteo_response):
    """Test parsing a valid open-meteo response"""
    client = OpenMeteoClient()
    parsed = client._parse_response(test_open_meteo_response)
    
    assert parsed is not None
    assert parsed["temperature"] == 15.0
    assert parsed["wind_speed"] == 10.5
    assert parsed["wind_direction"] == 200
    assert parsed["humidity"] == 65       # From index 1 ("2024-05-18T10:00")
    assert parsed["pressure"] == 1011.5   # From index 1
    assert parsed["cloud_coverage"] == 20 # From index 1
    assert parsed["rainfall"] == 0.5 # From index 1

def test_parse_missing_hourly(test_open_meteo_response):
    """Test parsing when hourly data is mostly missing"""
    test_open_meteo_response["hourly"] = {}
    
    client = OpenMeteoClient()
    parsed = client._parse_response(test_open_meteo_response)
    
    assert parsed is not None
    assert parsed["temperature"] == 15.0
    assert parsed["humidity"] is None
    assert parsed["pressure"] is None

def test_parse_empty_response():
    """Test parsing an empty response"""
    client = OpenMeteoClient()
    parsed = client._parse_response({})
    
    assert parsed is None

def test_parse_response_no_current_weather(test_open_meteo_response):
    """Test parsing when 'current_weather' is missing but hourly exists"""
    del test_open_meteo_response["current_weather"]
    
    client = OpenMeteoClient()
    parsed = client._parse_response(test_open_meteo_response)
    
    # Still parses successfully but with some None values and fallback index logic
    assert parsed is not None
    assert parsed["temperature"] is None
    assert parsed["humidity"] == 55  # Uses last index (len - 1 = 2)
    assert parsed["pressure"] == 1011.0
