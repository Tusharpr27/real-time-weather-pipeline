# Real-Time Weather Data Pipeline System - Project Plan

**Project Start Date:** April 2, 2026  
**Tech Stack:** Python Backend | SQL Database | React/Streamlit Dashboard  
**Data Source:** Real-time Weather API

---

## 📋 Project Overview

A comprehensive system that fetches live weather data from a weather API, processes it in real-time, stores it in a SQL database, detects anomalies/trends, and displays interactive insights on a dashboard.

### Key Objectives:
- Fetch real-time weather data from multiple locations
- Process and enrich data (calculations, trend analysis, anomaly detection)
- Store historical data in SQL database
- Display live insights and analytics on a dashboard
- Alert system for weather anomalies

---

## 🎯 Recommended Weather API Options

| API | Free Tier | Update Frequency | Coverage | Best For |
|-----|-----------|------------------|----------|----------|
| **OpenWeatherMap** | ✅ 1000 calls/day | 10 min intervals | Global | Best choice - mature, reliable |
| **WeatherAPI.com** | ✅ 1M calls/month | Real-time | Global | Good alternative, generous free tier |
| **Open-Meteo** | ✅ Unlimited | 15 min intervals | Global | Best for free tier (no key needed) |
| **National Weather Service API** | ✅ Unlimited | 30 min intervals | USA only | If US-only focus |

**Recommendation:** Use **Open-Meteo** for development (unlimited, no API key) → Switch to **OpenWeatherMap** for production.

---

## 📊 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   REAL-TIME DATA PIPELINE                   │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐      ┌──────────────┐     ┌─────────────┐ │
│  │  Weather API │ ────▶│  Data Fetcher│────▶│  Processor  │ │
│  │ (Open-Meteo/ │      │   (async)    │     │ (Analysis)  │ │
│  │ OpenWeather) │      └──────────────┘     └─────────────┘ │
│  └──────────────┘             │                      │       │
│                               │                      │       │
│  ┌──────────────┐            │        ┌──────────────▼──┐   │
│  │   Database   │◀───────────┴────────│   Alert Engine  │   │
│  │   (SQLite/   │           Store      │ (Anomalies/    │   │
│  │  PostgreSQL) │                      │  Thresholds)   │   │
│  └──────────────┘                      └─────────────────┘   │
│         │                                                      │
│         │                                                      │
│  ┌──────▼──────────────────────────────────────────────────┐ │
│  │           Dashboard / REST API                          │ │
│  │  (Streamlit or React + FastAPI/Flask)                 │ │
│  │  - Real-time weather map                              │ │
│  │  - Historical trends & analytics                      │ │
│  │  - Alerts & notifications                             │ │
│  └───────────────────────────────────────────────────────┘  │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 🛠️ PHASE 1: BACKEND SETUP & INFRASTRUCTURE

### **1.1 Project Structure Setup**
- Initialize Git repository
- Create Python virtual environment
- Set up project folder structure
- Configure `.env` for API keys and database credentials
- Create `requirements.txt` with all dependencies

**Deliverables:**
- ✅ Project skeleton ready
- ✅ Virtual environment configured
- ✅ Dependencies documented

**Tech:** Python 3.12, pip, Git

---

### **1.2 Database Layer**
**Objective:** Set up persistent data storage

**Components:**
1. **Database Choice:**
   - Development: SQLite (no setup needed)
   - Production: PostgreSQL (recommended)

2. **Schema Design:**
   - `weather_data` table (raw data)
   - `weather_alerts` table (anomalies detected)
   - `locations` table (cities/coordinates)
   - `processed_metrics` table (aggregated data)

3. **ORM Setup:**
   - Use SQLAlchemy for database abstraction
   - Create database models/schemas
   - Set up migration system (Alembic)

**Tasks:**
- [ ] Design database schema
- [ ] Set up SQLAlchemy models
- [ ] Configure database connection pooling
- [ ] Write database initialization scripts
- [ ] Create seed data for multiple locations

**Deliverables:**
- ✅ Database schema documented
- ✅ All tables created with indexes
- ✅ SQLAlchemy models ready

**Tech:** SQLAlchemy, SQLite/PostgreSQL, Alembic

---

### **1.3 Data Fetcher Module**
**Objective:** Continuously fetch real-time weather data

**Components:**
1. **API Integration:**
   - Create API client wrapper (abstract API calls)
   - Handle authentication (API keys)
   - Implement error handling & retries
   - Rate limiting compliance

2. **Data Collection:**
   - Async data fetching (multiple locations simultaneously)
   - Support multiple weather providers (abstraction layer)
   - Parse API responses
   - Data validation

3. **Scheduling:**
   - Background task scheduler (APScheduler)
   - Run data collection every 10-15 minutes
   - Handle failed requests gracefully

**Tasks:**
- [ ] Create WeatherAPI client wrapper class
- [ ] Implement async data fetching with aiohttp
- [ ] Set up APScheduler for recurring tasks
- [ ] Add comprehensive error handling & logging
- [ ] Create unit tests for API client
- [ ] Test with multiple locations

**Deliverables:**
- ✅ Data fetcher running independently
- ✅ Handles failures gracefully
- ✅ Logs all operations
- ✅ Unit tests pass

**Tech:** aiohttp, APScheduler, requests, logging

---

### **1.4 Data Processing & Analysis Module**
**Objective:** Transform raw data into insights

**Status:** ✅ COMPLETED

**Components:**
1. **Data Validation:**
   - ✅ Remove duplicates, handle missing values
   - ✅ Unit conversions
   - ✅ Range validation (temperature, humidity, pressure, wind)

2. **Calculations:**
   - ✅ Heat Index (Rothfusz formula)
   - ✅ Wind Chill (for T < 10°C)
   - ✅ Dew Point (Magnus formula)
   - ✅ Comfort Index
   - ✅ Statistical analysis (mean, median, std dev)

3. **Aggregations:**
   - ✅ Hourly averages (from 15-min data)
   - ✅ Daily min/max/avg
   - ✅ Weekly trends
   - ✅ Stores in ProcessedMetrics table

4. **Anomaly Detection:**
   - ✅ Z-score statistical method (threshold: 3.0σ)
   - ✅ Rapid change detection (>5°C in 1 hour)
   - ✅ Creates Alert records
   - ✅ Severity levels: LOW, MEDIUM, HIGH

**Deliverables:**
- ✅ validator.py (255 lines)
- ✅ calculator.py (230 lines)
- ✅ aggregator.py (290 lines)
- ✅ anomaly_detector.py (305 lines)
- ✅ pipeline.py (215 lines)
- ✅ processing_scheduler.py (215 lines)
- ✅ stats_routes.py (315 lines)

**Total Code:** 1,815 lines

**Tech:** SQLAlchemy ORM, APScheduler, FastAPI, Pydantic

---

### **1.5 Storage & Persistence**
**Objective:** Save processed data for historical analysis

**Components:**
1. **Data Storage:**
   - Insert raw weather data into database
   - Store processed metrics
   - Log alerts
   - Maintain data retention policies (cleanup old data)

2. **Query Layer:**
   - Efficient data retrieval methods
   - Time-series queries
   - Filtering by location, date range, metrics

3. **Data Export:**
   - Export to CSV for analysis
   - Backup mechanisms

**Tasks:**
- [ ] Implement data insertion functions
- [ ] Create data retention policies
- [ ] Build efficient query functions
- [ ] Add database indexing for performance
- [ ] Implement data export features
**Status:** ⏳ NOT STARTED

**Components:**
1. **Data Storage:**
   - Data retention policies (30-day default)
   - Old data archiving/cleanup
   - Database compression

2. **Data Retention:**
   - Automatic cleanup of old data
   - Archive strategies
   - Backup mechanisms

3. **Performance Optimization:**
   - Database indexing
   - Query optimization
   - Caching strategies

**Tech:** SQLAlchemy ORM, database migrations

---

### **1.6 Alert & Notification System**
**Objective:** Notify users of significant weather events

**Components:**
1. **Alert Rules:**
   - Temperature thresholds (e.g., >35°C or <-10°C)
   - Wind speed alerts (>50 km/h)
   - Unusual weather patterns
   - Configurable rules per location

2. **Notification Channels:**
   - Email notifications (optional)
   - Dashboard alerts
   - Log file entries
   - In-app notifications

3. **Alert State Management:**
   - Track alert status (new, acknowledged, resolved)
   - Prevent duplicate alerts
   - Alert escalation

**Tasks:**
- [ ] Define alert rules/thresholds
- [ ] Create alert database schema
- [ ] Implement alert trigger logic
- [ ] Build notification sender (email)
- [ ] Add alert history tracking
- [ ] Create admin interface for alert configuration

**Deliverables:**
- ✅ Alerts trigger correctly
- ✅ No duplicate alerts
- ✅ Notifications sent successfully
- ✅ Alert history maintained

**Tech:** SMTP (for email), logging

---

### **1.7 REST API Layer (Backend API)**
**Objective:** Expose backend functionality via HTTP API

**Components:**
1. **API Framework:**
   - FastAPI or Flask
   - RESTful endpoints
   - Input validation
   - Error handling

2. **API Endpoints:**
   ```
   GET /api/weather/current/<location>
   GET /api/weather/history/<location>?days=7
   GET /api/weather/alerts
   GET /api/weather/stats/<location>
   GET /api/locations
   POST /api/locations (add new location)
   GET /api/health (health check)
   ```

3. **Authentication:**
   - API key or JWT tokens (optional for demo)
   - Rate limiting

**Tasks:**
- [ ] Choose API framework (FastAPI recommended)
- [ ] Design API endpoints
- [ ] Implement request validation
- [ ] Add error handling
- [ ] Write API tests
- [ ] Create API documentation (Swagger)
- [ ] Implement CORS for frontend

**Deliverables:**
- ✅ API endpoints functional
- ✅ API documentation complete
- ✅ Tests passing
- ✅ Ready for frontend consumption

**Tech:** FastAPI/Flask, Pydantic, pytest

---

### **1.8 Logging & Monitoring**
**Objective:** Track system health and debug issues

**Components:**
1. **Logging System:**
   - Structured logging
   - Log levels (DEBUG, INFO, WARNING, ERROR)
   - Log rotation
   - File and console output

2. **Monitoring:**
   - System health checks
   - Database connection status
   - API availability
   - Data pipeline status

3. **Error Tracking:**
   - Catch and log all errors
   - Error aggregation
   - Alert on critical failures

**Tasks:**
- [ ] Set up logging configuration
- [ ] Implement health check endpoint
- [ ] Add monitoring dashboard info
- [ ] Create error aggregation mechanism

**Deliverables:**
- ✅ All operations logged
- ✅ Health checks working
- ✅ Errors tracked and visible

**Tech:** Python logging, structlog (optional)

---

## 🚀 PHASE 2: FRONTEND DEVELOPMENT

### **2.1 Dashboard Technology Choice**

**Option A: Streamlit (Recommended for Quick Development)**
- ✅ Fastest to build
- ✅ Real-time updates
- ✅ Built-in components
- ❌ Limited customization
- Best for: MVP and rapid prototyping

**Option B: React + FastAPI (More Professional)**
- ✅ Highly customizable
- ✅ Better performance
- ✅ Modern UI/UX
- ❌ More development time
- Best for: Production system

**Recommendation:** Start with **Streamlit** for Phase 2, can upgrade to React later.

---

### **2.2 Dashboard Features (Streamlit)**
- Real-time weather display (current conditions)
- Interactive weather map (city/location selector)
- Historical charts (temperature, humidity trends)
- Alert history and current alerts
- Statistics and insights
- Data export functionality
- Location management (add/remove cities)

---

### **2.3 Data Visualization**
- Temperature trend charts (line graphs)
- Humidity vs Temperature scatter plot
- Wind speed patterns
- Heatmaps for multiple locations
- Gauge charts for current metrics
- Map visualization (optional - Folium/Plotly)

---

## 📦 Technology Stack Summary

### **Backend:**
- **Language:** Python 3.12
- **API:** FastAPI
- **Database:** SQLite (dev) / PostgreSQL (prod)
- **ORM:** SQLAlchemy
- **Async:** aiohttp, asyncio
- **Scheduling:** APScheduler
- **Validation:** Pydantic
- **Testing:** pytest
- **Logging:** Python logging module

### **Frontend:**
- **Dashboard:** Streamlit (Phase 2a) or React (Phase 2b)
- **Visualization:** Plotly, Altair
- **HTTP Client:** axios (React) or requests (Streamlit)

### **Database:**
- **Development:** SQLite
- **Production:** PostgreSQL

### **DevOps/Deployment:**
- **Version Control:** Git
- **Environment:** Python venv
- **Containerization:** Docker (optional)
- **Deployment:** Heroku, AWS, or local server

---

## 📅 Implementation Timeline

### **Phase 1: Backend (2-3 weeks)**
- Week 1: Project setup + Database layer + Data fetcher
- Week 2: Processing module + Storage + Alerts
- Week 3: REST API + Logging + Testing

### **Phase 2: Frontend (1-2 weeks)**
- Week 1: Streamlit dashboard + Basic visualizations
- Week 2: Advanced features + Optimization

### **Phase 3: Deployment (1 week)**
- Docker setup
- Production deployment
- Monitoring setup

---

## ❓ Clarification Questions

Before we proceed, please answer:

1. **Scope:** Should this support multiple cities/locations or just one?
   - Single city: Simpler
   - Multiple cities (5-10): More complex but more useful

2. **Historical Data:** How many days of historical data should we keep?
   - 1 week: Lightweight
   - 1 month: Better trends
   - 1 year: Long-term analysis

3. **Dashboard Priority:**
   - Streamlit (faster, simpler) or React (more professional)?

4. **Alerts:** What weather conditions should trigger alerts?
   - Temperature > 35°C / < -10°C?
   - Wind > 50 km/h?
   - Other specific conditions?

5. **Data Update Frequency:**
   - Every 10 minutes (more real-time, more API calls)
   - Every 30 minutes (balanced)
   - Every hour (less frequent)

---

## 🎯 Next Steps

1. Answer clarification questions above
2. Review and approve Phase 1 detailed breakdown
3. Set up project structure
4. Start Phase 1.1: Project Structure Setup
5. Initialize Git repository
6. Create Python virtual environment
7. Install initial dependencies

---

**Status:** ✅ Phase 1.1 Complete - Project Structure Ready  
**Last Updated:** April 2, 2026

---

## 🎯 Phase 1.1 Completed ✅

### What's Ready:
- ✅ Project folder structure created
- ✅ Python 3.12 installed
- ✅ Virtual environment configured (`backend/venv`)
- ✅ All dependencies documented (`requirements.txt`)
- ✅ FastAPI application initialized
- ✅ Configuration management system (config.py)
- ✅ Logging infrastructure setup
- ✅ Environment variables configured (.env)

### How to Get Started:

**Option 1: Automated Setup (Windows)**
```
cd backend
setup.bat
```

**Option 2: Manual Setup**
```
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```

### API Available At:
- **Base URL:** http://localhost:8000
- **Documentation:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/api/health

---

## 🚀 Phase 1.2: Database Layer ✅ Complete

### Implemented:
- ✅ 5 SQLAlchemy models (Location, WeatherData, ProcessedMetrics, Alert, SystemMetric)
- ✅ Repository pattern for all CRUD operations
- ✅ Database connection pooling
- ✅ Proper indexes for performance
- ✅ Data retention policies (30 days)
- ✅ Pydantic schemas for API validation
- ✅ Database initialization with 5 seed locations

---

## 🚀 Phase 1.3: Data Fetcher Module ✅ Complete

### Implemented:
- ✅ Async Weather API Client (Open-Meteo & OpenWeatherMap support)
- ✅ WeatherDataFetcher service (async data collection)
- ✅ APScheduler for periodic fetching (every 15 minutes)
- ✅ 10 REST API endpoints for weather data
- ✅ System routes for health & status
- ✅ Error handling & retry logic
- ✅ System metrics logging

**API Endpoints:**
- GET `/api/weather/locations` - All locations
- GET `/api/weather/current/{name}` - Current weather
- GET `/api/weather/history/{name}?days=7` - Historical data
- GET `/api/weather/stats/{name}` - Aggregated stats
- GET `/api/weather/{name}/summary` - Complete summary
- GET `/api/health` - Health check
- GET `/api/system/status` - System status

---

## 🔄 Next: Phase 1.4 - Data Processing Module

Ready to implement:
- ✅ Data validation & cleaning
- ✅ Temperature/humidity trend calculations
- ✅ Anomaly detection
- ✅ Hourly/daily/weekly aggregations
- ✅ Storage in ProcessedMetrics table
