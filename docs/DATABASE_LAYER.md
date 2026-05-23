# Phase 1.2: Database Layer - Complete Implementation

## ✅ Database Layer Completed

### Components Implemented:

#### 1. **SQLAlchemy Models** (`src/database/models.py`)
   
**Table Structure:**

| Table | Purpose | Key Fields |
|-------|---------|-----------|
| `locations` | Geographic locations | id, name, lat, lon, timezone, is_active |
| `weather_data` | Raw API data | id, location_id, temp, humidity, wind, conditions |
| `processed_metrics` | Aggregated data | id, location_id, avg_temp, min/max, trends |
| `alerts` | Alert records | id, location_id, type, severity, status |
| `system_metrics` | Pipeline health | id, api_calls, errors, response_time |

**Key Features:**
- ✅ Foreign keys with cascade delete
- ✅ Proper indexes for performance
- ✅ DateTime tracking (created_at, updated_at)
- ✅ Relationships defined for ORM queries
- ✅ Constraints and validation

#### 2. **Database Connection** (`src/database/database.py`)

**Features:**
- Connection pooling (StaticPool for SQLite, QueuePool for PostgreSQL)
- Automatic engine initialization
- FastAPI dependency for session management
- Session factory for standalone use

#### 3. **Repository Pattern** (`src/database/repository.py`)

**Classes:**
- `LocationRepository` - Location CRUD operations
- `WeatherDataRepository` - Weather data storage & queries
- `ProcessedMetricsRepository` - Metrics aggregation access
- `AlertRepository` - Alert management
- `SystemMetricRepository` - Pipeline metrics

**Key Methods:**
```python
# Locations
LocationRepository.create()
LocationRepository.get_all(active_only=True)
LocationRepository.get_by_name()

# Weather Data
WeatherDataRepository.create()
WeatherDataRepository.get_latest()
WeatherDataRepository.get_history(days=7)
WeatherDataRepository.get_by_date_range()
WeatherDataRepository.cleanup_old_data()  # Data retention

# Alerts
AlertRepository.create()
AlertRepository.get_active_alerts()
AlertRepository.acknowledge()
AlertRepository.resolve()
```

#### 4. **Database Initialization** (`src/database/init_db.py`)

**Functions:**
- `init_database()` - Creates all tables
- `seed_default_locations()` - Populates 5 Indian cities

**Default Locations:**
- Delhi (28.7041°N, 77.1025°E)
- Mumbai (19.0760°N, 72.8777°E)
- Bangalore (12.9716°N, 77.5946°E)
- Chennai (13.0827°N, 80.2707°E)
- Kolkata (22.5726°N, 88.3639°E)

#### 5. **Pydantic Schemas** (`src/api/schemas.py`)

**Request/Response models:**
- LocationResponse, LocationCreate
- WeatherDataResponse, WeatherDataCreate
- ProcessedMetricsResponse
- AlertResponse
- HealthCheckResponse

---

## 🗄️ Database Schema Details

### Locations Table
```sql
CREATE TABLE locations (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    latitude FLOAT NOT NULL,
    longitude FLOAT NOT NULL,
    country VARCHAR(100),
    timezone VARCHAR(50) DEFAULT 'UTC',
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT UTC,
    updated_at DATETIME DEFAULT UTC
);
```

### Weather Data Table
```sql
CREATE TABLE weather_data (
    id INTEGER PRIMARY KEY,
    location_id INTEGER FOREIGN KEY,
    temperature FLOAT NOT NULL,
    feels_like FLOAT,
    humidity INTEGER (0-100),
    wind_speed FLOAT,
    weather_condition VARCHAR(50),
    recorded_at DATETIME,
    created_at DATETIME DEFAULT UTC,
    
    -- Indexes for queries
    INDEX ix_weather_data_location_created (location_id, created_at),
    INDEX ix_weather_data_location_date (location_id, recorded_at)
);
```

### Processed Metrics Table
```sql
CREATE TABLE processed_metrics (
    id INTEGER PRIMARY KEY,
    location_id INTEGER FOREIGN KEY,
    metric_type VARCHAR(20),  -- hourly, daily, weekly
    period_start DATETIME,
    period_end DATETIME,
    avg_temperature FLOAT,
    min_temperature FLOAT,
    max_temperature FLOAT,
    avg_humidity FLOAT,
    avg_wind_speed FLOAT,
    data_points_count INTEGER,
    
    INDEX ix_processed_metrics_location_type (location_id, metric_type)
);
```

### Alerts Table
```sql
CREATE TABLE alerts (
    id INTEGER PRIMARY KEY,
    location_id INTEGER FOREIGN KEY,
    alert_type VARCHAR(50),      -- temp_high, wind_high, etc
    severity VARCHAR(20),         -- low, medium, high, critical
    message VARCHAR(500),
    metric_value FLOAT,
    threshold_value FLOAT,
    status VARCHAR(20),           -- new, acknowledged, resolved
    triggered_at DATETIME,
    
    INDEX ix_alerts_location_status (location_id, status),
    INDEX ix_alerts_triggered (triggered_at)
);
```

---

## 🔧 Usage Examples

### Initialize Database
```python
from src.database.init_db import init_database, seed_default_locations

# Initialize tables
init_database()

# Seed default locations
seed_default_locations()
```

### Using Repositories
```python
from src.database.database import create_session
from src.database.repository import (
    LocationRepository,
    WeatherDataRepository,
    AlertRepository
)

db = create_session()

# Get all active locations
locations = LocationRepository.get_all(db, active_only=True)

# Get latest weather data
weather = WeatherDataRepository.get_latest(db, location_id=1)

# Get 7 days of history
history = WeatherDataRepository.get_history(db, location_id=1, days=7)

# Create an alert
alert = AlertRepository.create(
    db,
    location_id=1,
    alert_type="temp_high",
    severity="high",
    message="Temperature exceeds 40°C",
    metric_name="temperature",
    metric_value=42.5,
    threshold_value=40.0
)

# Acknowledge alert
AlertRepository.acknowledge(db, alert_id=alert.id)

db.close()
```

### With FastAPI Dependency
```python
from fastapi import Depends
from sqlalchemy.orm import Session
from src.database.database import get_db
from src.database.repository import LocationRepository

@app.get("/api/locations")
async def get_locations(db: Session = Depends(get_db)):
    locations = LocationRepository.get_all(db, active_only=True)
    return locations
```

---

## 📊 Data Retention Policy

**Default:** 30 days (configurable via `DATA_RETENTION_DAYS` env var)

```python
# Cleanup old weather data
WeatherDataRepository.cleanup_old_data(db, days_to_keep=30)
```

This removes weather data older than 30 days while keeping processed metrics.

---

## 🔍 Performance Considerations

**Indexes Created:**
1. `weather_data` - (location_id, created_at)
2. `weather_data` - (location_id, recorded_at)
3. `processed_metrics` - (location_id, metric_type)
4. `processed_metrics` - (period_start, period_end)
5. `alerts` - (location_id, status)
6. `alerts` - (triggered_at)

**Connection Pooling:**
- SQLite: StaticPool (development)
- PostgreSQL: QueuePool with 10 connections + 20 overflow

**Query Optimization:**
- All repositories use efficient queries
- Proper filtering and ordering
- Date range queries optimized

---

## 📝 Next Steps: Phase 1.3 - Data Fetcher Module

The database layer is now ready to store data. Next phase will implement:

1. **Weather API Client**
   - Open-Meteo API integration
   - Async data fetching
   - Error handling & retries

2. **Background Task Scheduling**
   - APScheduler for periodic data collection
   - Configurable intervals (default: 15 minutes)

3. **Data Pipeline**
   - Fetch → Validate → Store
   - Error logging and recovery

---

**Status:** ✅ Phase 1.2 Complete - Database Layer Ready  
**Last Updated:** April 2, 2026
