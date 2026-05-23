import pytest
from src.processor.anomaly_detector import AnomalyDetector

class MockWeatherData:
    def __init__(self, temperature, humidity, wind_speed):
        self.temperature = temperature
        self.humidity = humidity
        self.wind_speed = wind_speed

def test_detect_temperature_anomaly():
    """Test temperature anomaly detection (Z-score based)"""
    # Create standard normal-ish data (mean ~20, stdev ~2)
    historical_data = [
        MockWeatherData(temp, 50, 10.0) 
        for temp in [18, 19, 20, 21, 22, 18, 19, 20, 21, 22]
    ]
    
    # 20 should naturally not be an anomaly
    is_anomaly, z_score = AnomalyDetector.detect_temperature_anomaly(20.0, historical_data)
    assert not is_anomaly
    assert z_score is not None
    assert z_score < 1.0
    
    # 35 should be way out of the std dev bounds
    is_anomaly, z_score = AnomalyDetector.detect_temperature_anomaly(35.0, historical_data)
    assert is_anomaly
    assert z_score > 3.0

def test_not_enough_data():
    """Test returning False when historical data is too small"""
    historical_data = [MockWeatherData(20, 50, 10.0) for _ in range(5)]
    is_anomaly, z_score = AnomalyDetector.detect_temperature_anomaly(35.0, historical_data)
    assert not is_anomaly
    assert z_score is None

def test_zero_variance():
    """Test handling when historical data is uniform (zero std dev)"""
    historical_data = [MockWeatherData(20, 50, 10.0) for _ in range(10)]
    is_anomaly, z_score = AnomalyDetector.detect_temperature_anomaly(25.0, historical_data)
    assert not is_anomaly
    assert z_score is None

def test_detect_rapid_temperature_change():
    """Test detecting rapid changes > threshold"""
    assert AnomalyDetector.detect_rapid_temperature_change(20.0, 12.0) is True  # diff is 8
    assert AnomalyDetector.detect_rapid_temperature_change(20.0, 18.0) is False # diff is 2
    assert AnomalyDetector.detect_rapid_temperature_change(10.0, 20.0, threshold=15.0) is False # diff 10 < 15
