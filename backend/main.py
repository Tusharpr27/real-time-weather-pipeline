"""
Main FastAPI application
Entry point for the Real-Time Weather Pipeline backend
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from config import settings
from src.utils.logger import logger
from src.database.init_db import init_database, seed_default_locations
from src.fetcher.scheduler import get_scheduler
from src.fetcher.data_fetcher import get_fetcher
from src.processor.processing_scheduler import get_processing_scheduler
from src.storage.storage_scheduler import get_storage_scheduler
from src.alerts.alert_scheduler import create_alert_scheduler


# Lifespan context manager for startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events"""
    # Startup
    logger.info(f"Starting {settings.app_name} - Environment: {settings.app_env}")
    logger.info(f"Monitoring locations: {settings.location_list}")
    logger.info(f"Data fetch interval: {settings.fetch_interval_minutes} minutes")
    
    # Initialize database
    try:
        logger.info("Initializing database...")
        init_database()
        seed_default_locations()
        logger.info("âœ… Database initialized")
    except Exception as e:
        logger.error(f"âŒ Database initialization error: {e}")
    
    # Initialize fetcher
    try:
        logger.info("Initializing weather fetcher...")
        fetcher = await get_fetcher()
        await fetcher.start()
        logger.info("âœ… Weather fetcher initialized")
    except Exception as e:
        logger.error(f"âŒ Fetcher initialization error: {e}")
    
    # Start scheduler for periodic data fetching
    try:
        logger.info("Starting weather scheduler...")
        scheduler = get_scheduler()
        await scheduler.start()
        logger.info("âœ… Weather scheduler started")
    except Exception as e:
        logger.error(f"âŒ Scheduler start error: {e}")
    
    # Start data processing scheduler
    try:
        logger.info("Starting data processing scheduler...")
        proc_scheduler = get_processing_scheduler()
        await proc_scheduler.start()
        logger.info("âœ… Data processing scheduler started")
    except Exception as e:
        logger.error(f"âŒ Processing scheduler start error: {e}")
    
    # Start storage optimization scheduler
    try:
        logger.info("Starting storage optimization scheduler...")
        storage_scheduler = get_storage_scheduler()
        await storage_scheduler.start()
        logger.info("âœ… Storage scheduler started")
    except Exception as e:
        logger.error(f"âŒ Storage scheduler start error: {e}")
    
    # Start alert system scheduler if enabled in settings
    if settings.alert_system_enabled:
        try:
            logger.info("Starting alert system scheduler...")
            base_scheduler = get_scheduler().scheduler if hasattr(get_scheduler(), 'scheduler') else get_scheduler()
            alert_scheduler = create_alert_scheduler(base_scheduler)
            alert_scheduler.start()
            logger.info("âœ… Alert system scheduler started")
        except Exception as e:
            logger.error(f"âŒ Alert scheduler start error: {e}")
    
    yield
    
    # Shutdown
    logger.info(f"Shutting down {settings.app_name}")
    
    # Stop storage scheduler
    try:
        storage_scheduler = get_storage_scheduler()
        await storage_scheduler.stop()
    except Exception as e:
        logger.error(f"Error stopping storage scheduler: {e}")
    
    # Stop processing scheduler
    try:
        proc_scheduler = get_processing_scheduler()
        await proc_scheduler.stop()
    except Exception as e:
        logger.error(f"Error stopping processing scheduler: {e}")
    
    # Stop scheduler
    try:
        scheduler = get_scheduler()
        await scheduler.stop()
    except Exception as e:
        logger.error(f"Error stopping scheduler: {e}")


# Create FastAPI app instance
app = FastAPI(
    title=settings.app_name,
    description="Real-time weather data collection and analysis pipeline",
    version="0.1.0",
    lifespan=lifespan,
    debug=settings.debug
)

# Add CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure as needed for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/api/health", tags=["System"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app_name": settings.app_name,
        "environment": settings.app_env,
        "version": "0.1.0"
    }


# Root endpoint
@app.get("/", tags=["System"])
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Real-Time Weather Pipeline API",
        "docs": "/docs",
        "version": "0.1.0"
    }


# Include API routes
from src.api import weather_routes, system_routes, stats_routes, storage_routes, webhook_routes, export_routes, realtime_routes, monitoring_routes, auth_routes
from src.alerts import alert_routes
app.include_router(auth_routes.router)
app.include_router(system_routes.router)
app.include_router(weather_routes.router)
app.include_router(stats_routes.router)
app.include_router(storage_routes.router)
app.include_router(alert_routes.router)
app.include_router(webhook_routes.router)
app.include_router(export_routes.router)
app.include_router(realtime_routes.router)
app.include_router(monitoring_routes.router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload
    )

