# Real-Time Weather Data Pipeline - Backend

A robust Python-based system for fetching, processing, and analyzing real-time weather data.

## Project Structure

```
backend/
├── src/
│   ├── api/                 # FastAPI endpoints
│   ├── database/            # Database models & migrations
│   ├── fetcher/             # Weather API fetcher
│   ├── processor/           # Data processing & analysis
│   ├── alerts/              # Alert system
│   └── utils/               # Helper utilities
├── tests/                   # Unit & integration tests
├── logs/                    # Application logs
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables template
└── main.py                 # Application entry point
```

## Setup Instructions

### 1. Create Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment
```bash
cp .env.example .env
# Edit .env with your configuration
```

### 4. Initialize Database
```bash
python -m alembic upgrade head
```

### 5. Run Application
```bash
python main.py
# or with uvicorn
uvicorn main:app --reload
```

## API Endpoints

### Weather Data
- `GET /api/weather/current/<location>` - Current weather
- `GET /api/weather/history/<location>?days=7` - Historical data
- `GET /api/weather/stats/<location>` - Weather statistics

### Alerts
- `GET /api/weather/alerts` - Get all alerts
- `GET /api/weather/alerts/<location>` - Location-specific alerts

### System
- `GET /api/health` - Health check
- `GET /api/locations` - List monitored locations

## Development

### Run Tests
```bash
pytest tests/ -v
```

### Code Quality
```bash
black .
flake8 .
isort .
```

### Logs
Check `logs/weather_pipeline.log` for application logs

## Technologies Used
- FastAPI - Web framework
- SQLAlchemy - ORM
- APScheduler - Task scheduling
- aiohttp - Async HTTP client
- Pydantic - Data validation
- Streamlit - Dashboard (frontend)

## License
MIT
