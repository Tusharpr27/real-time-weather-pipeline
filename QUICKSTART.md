# Quick Start Guide - Real-Time Weather Pipeline

## 🚀 Getting Started in 5 Minutes

### Prerequisites
- Windows 10/11, macOS, or Linux
- Python 3.12+ (already installed)
- 2GB free disk space

### Step 1: Install Dependencies

**Windows:**
```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**Linux/Mac:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Step 2: Configure Environment

The `.env` file is already configured with defaults. If you need to customize:

```bash
# Edit .env file
DATABASE_URL=sqlite:///./weather_pipeline.db
LOCATIONS=Delhi,Mumbai,Bangalore,Chennai,Kolkata
FETCH_INTERVAL_MINUTES=15
```

### Step 3: Run the Application

```bash
python main.py
```

You should see:
```
[INFO] Starting Real-Time Weather Pipeline - Environment: development
[INFO] ✅ Database initialized
[INFO] ✅ Weather fetcher initialized
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 4: Access the API

- **API Documentation:** http://localhost:8000/docs
- **Alternative Docs:** http://localhost:8000/redoc
- **Health Check:** http://localhost:8000/api/health

---

## 📚 API Examples

### Get All Locations
```bash
curl http://localhost:8000/api/weather/locations
```

### Get Current Weather
```bash
curl http://localhost:8000/api/weather/current/Delhi
```

### Get 7-Day History
```bash
curl http://localhost:8000/api/weather/history/Delhi?days=7
```

### Get Weather Summary
```bash
curl http://localhost:8000/api/weather/Delhi/summary
```

### Check System Status
```bash
curl http://localhost:8000/api/system/status
```

---

## 🗂️ Project Structure

```
Real time weather data pipeline system/
├── backend/
│   ├── src/
│   │   ├── api/              # API routes & schemas
│   │   ├── database/         # Database models & repo
│   │   ├── fetcher/          # Data fetcher & scheduler
│   │   ├── processor/        # (Phase 1.4)
│   │   ├── alerts/           # (Phase 1.6)
│   │   └── utils/            # Logger & helpers
│   ├── tests/                # Test files
│   ├── logs/                 # Application logs
│   ├── main.py              # FastAPI entry point
│   ├── config.py            # Configuration
│   ├── requirements.txt      # Dependencies
│   └── .env                 # Environment variables
│
├── frontend/                # (Phase 2 - Streamlit)
├── docs/                    # Documentation
│   ├── SETUP_PROGRESS.md
│   ├── DATABASE_LAYER.md
│   └── DATA_FETCHER.md
│
└── plan.md                  # Complete project plan
```

---

## 🔍 Checking the Logs

Application logs are stored in `backend/logs/weather_pipeline.log`:

```bash
# View recent logs
tail -f backend/logs/weather_pipeline.log

# On Windows PowerShell
Get-Content backend/logs/weather_pipeline.log -Tail 20 -Wait
```

---

## 🛠️ Development Commands

### Run Tests
```bash
pytest tests/ -v
```

### Code Quality
```bash
# Format code
black src/

# Lint
flake8 src/

# Type checking
mypy src/
```

### Database

View SQLite database:
```bash
# Linux/Mac
sqlite3 backend/weather_pipeline.db

# Windows - or use DB Browser for SQLite GUI
```

---

## 📊 What's Happening

### On Startup:
1. ✅ Creates SQLite database
2. ✅ Initializes all tables
3. ✅ Seeds 5 Indian cities
4. ✅ Starts async fetcher
5. ✅ Starts background scheduler

### Every 15 Minutes:
1. 📡 Fetches weather from Open-Meteo API
2. 🔄 Processes and validates data
3. 💾 Stores in database
4. 📊 Logs system metrics

### Available Immediately:
1. 🌐 REST API at http://localhost:8000
2. 📖 Interactive documentation
3. 📊 Current weather data
4. 📈 Historical data queries

---

## 🆘 Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'fastapi'"
**Solution:** Activate virtual environment first
```bash
.\venv\Scripts\Activate.ps1  # Windows
source venv/bin/activate     # Linux/Mac
```

### Issue: "Port 8000 already in use"
**Solution:** Change port in .env
```env
API_PORT=8001
```

### Issue: "No weather data available"
**Solution:** Wait for first fetch cycle (15 min or manually trigger)
```bash
# Wait for scheduler, or restart to trigger immediately
```

### Issue: "Database locked"
**Solution:** Restart the application
```bash
# Stop: Ctrl+C
# Start: python main.py
```

---

## 📈 Next Steps

### Short Term (This Week):
- ✅ Phase 1.4: Data Processing (trend analysis)
- ✅ Phase 1.5: Storage optimization
- ✅ Phase 1.6: Alert system

### Medium Term (2-3 Weeks):
- Phase 1.7: REST API enhancement
- Phase 1.8: Logging & monitoring
- Testing & optimization

### Long Term:
- Phase 2: Streamlit dashboard
- Deployment (Docker, Heroku)
- Production monitoring

---

## 📞 Support

For issues or questions:
1. Check the logs: `backend/logs/weather_pipeline.log`
2. Review documentation in `docs/` folder
3. Check the plan at root: `plan.md`

---

**Version:** 0.1.0  
**Status:** Phase 1.3 Complete ✅  
**Last Updated:** April 2, 2026
