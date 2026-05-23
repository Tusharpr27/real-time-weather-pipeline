"""
Database initialization and seed data
Creates tables and populates initial data
"""
from src.database.database import create_session
from src.database.models import Base, Location
from src.database.repository import LocationRepository
from src.utils.logger import logger


def init_database():
    """Initialize database schema"""
    from src.database.database import get_engine
    
    engine = get_engine()
    logger.info("Creating database tables...")
    
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created successfully")
    except Exception as e:
        logger.error(f"❌ Failed to create database tables: {e}")
        raise


def seed_default_locations():
    """Seed database with default locations"""
    db = create_session()
    
    default_locations = [
        {"name": "Delhi", "latitude": 28.7041, "longitude": 77.1025, "country": "India"},
        {"name": "Mumbai", "latitude": 19.0760, "longitude": 72.8777, "country": "India"},
        {"name": "Bangalore", "latitude": 12.9716, "longitude": 77.5946, "country": "India"},
        {"name": "Chennai", "latitude": 13.0827, "longitude": 80.2707, "country": "India"},
        {"name": "Kolkata", "latitude": 22.5726, "longitude": 88.3639, "country": "India"},
    ]
    
    try:
        logger.info("Seeding default locations...")
        
        for loc_data in default_locations:
            existing = LocationRepository.get_by_name(db, loc_data["name"])
            if not existing:
                LocationRepository.create(
                    db,
                    name=loc_data["name"],
                    latitude=loc_data["latitude"],
                    longitude=loc_data["longitude"],
                    country=loc_data["country"],
                    timezone="Asia/Kolkata"
                )
                logger.info(f"  ✅ Added location: {loc_data['name']}")
            else:
                logger.info(f"  ℹ️  Location already exists: {loc_data['name']}")
        
        logger.info("✅ Default locations seeded successfully")
    except Exception as e:
        logger.error(f"❌ Failed to seed locations: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    logger.info("Initializing database...")
    init_database()
    seed_default_locations()
    logger.info("✅ Database initialization complete!")
