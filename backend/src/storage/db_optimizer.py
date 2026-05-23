"""
Database optimizer module
Handles database maintenance, optimization, and query tuning
"""
from sqlalchemy import text, inspect
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Dict, List

from src.database.database import get_database_engine, create_session
from src.utils.logger import logger


class DatabaseOptimizer:
    """Manages database optimization and maintenance"""

    def __init__(self):
        self.engine = get_database_engine()
        self.db: Session = None
        self.optimization_stats = {}

    def start(self):
        """Initialize database session"""
        self.db = create_session()

    def finish(self):
        """Close database session"""
        if self.db:
            self.db.close()
            self.db = None

    async def vacuum_database(self) -> bool:
        """
        Run database VACUUM to reclaim space
        Works for SQLite only
        
        Returns:
            True if successful
        """
        self.start()

        try:
            logger.info("🧹 Running VACUUM on database...")
            
            # Check if using SQLite
            if "sqlite" in str(self.engine.url):
                self.db.execute(text("VACUUM"))
                self.db.commit()
                logger.info("✅ VACUUM completed successfully")
                return True
            else:
                logger.warning("⚠️  VACUUM not supported for non-SQLite databases")
                return False

        except Exception as e:
            logger.error(f"Error during VACUUM: {e}")
            return False
        finally:
            self.finish()

    async def analyze_database(self) -> bool:
        """
        Run ANALYZE to update query optimizer statistics
        
        Returns:
            True if successful
        """
        self.start()

        try:
            logger.info("📊 Running ANALYZE on database...")
            
            if "sqlite" in str(self.engine.url):
                self.db.execute(text("ANALYZE"))
                self.db.commit()
                logger.info("✅ ANALYZE completed successfully")
            elif "postgresql" in str(self.engine.url):
                self.db.execute(text("ANALYZE"))
                self.db.commit()
                logger.info("✅ ANALYZE completed successfully (PostgreSQL)")
            else:
                logger.warning("⚠️  ANALYZE not supported for this database")
                return False
            
            return True

        except Exception as e:
            logger.error(f"Error during ANALYZE: {e}")
            return False
        finally:
            self.finish()

    async def reindex_database(self) -> bool:
        """
        Rebuild all indexes in database
        
        Returns:
            True if successful
        """
        self.start()

        try:
            logger.info("🔧 Rebuilding all indexes...")
            
            # Get all tables
            inspector = inspect(self.engine)
            tables = inspector.get_table_names()
            
            reindexed_count = 0
            
            if "sqlite" in str(self.engine.url):
                self.db.execute(text("REINDEX"))
                self.db.commit()
                logger.info(f"✅ All indexes rebuilt (SQLite)")
                reindexed_count = len(tables)
            else:
                logger.warning("⚠️  Manual index rebuild not supported for this database type")
            
            return True

        except Exception as e:
            logger.error(f"Error rebuilding indexes: {e}")
            return False
        finally:
            self.finish()

    async def get_database_stats(self) -> Dict:
        """
        Get database statistics and health information
        
        Returns:
            Dictionary with database statistics
        """
        self.start()

        try:
            logger.info("📈 Gathering database statistics...")
            
            inspector = inspect(self.engine)
            stats = {
                "tables": [],
                "total_rows": 0,
                "timestamp": datetime.utcnow()
            }
            
            table_names = inspector.get_table_names()
            
            for table_name in table_names:
                try:
                    result = self.db.execute(
                        text(f"SELECT COUNT(*) as row_count FROM {table_name}")
                    )
                    row_count = result.scalar()
                    
                    # Get indexes
                    indexes = inspector.get_indexes(table_name)
                    columns = inspector.get_columns(table_name)
                    
                    stats["tables"].append({
                        "name": table_name,
                        "row_count": row_count,
                        "column_count": len(columns),
                        "index_count": len(indexes),
                        "columns": [c["name"] for c in columns]
                    })
                    
                    stats["total_rows"] += row_count
                    
                except Exception as e:
                    logger.warning(f"Could not get stats for table {table_name}: {e}")
            
            return stats

        except Exception as e:
            logger.error(f"Error gathering database stats: {e}")
            return {}
        finally:
            self.finish()

    async def optimize_all(self) -> Dict:
        """
        Run complete database optimization cycle
        
        Returns:
            Dictionary with optimization results
        """
        results = {
            "vacuum": False,
            "analyze": False,
            "reindex": False,
            "timestamp": datetime.utcnow()
        }
        
        logger.info("🚀 Starting full database optimization...")
        
        # Run VACUUM
        results["vacuum"] = await self.vacuum_database()
        
        # Run ANALYZE
        results["analyze"] = await self.analyze_database()
        
        # Run REINDEX
        results["reindex"] = await self.reindex_database()
        
        logger.info(f"✅ Database optimization complete: {results}")
        return results

    async def get_table_sizes(self) -> Dict:
        """
        Get approximate sizes of all tables
        
        Returns:
            Dictionary with table sizes
        """
        self.start()

        try:
            sizes = {}
            
            inspector = inspect(self.engine)
            table_names = inspector.get_table_names()
            
            for table_name in table_names:
                try:
                    if "sqlite" in str(self.engine.url):
                        # SQLite page size query
                        result = self.db.execute(
                            text(f"""
                                SELECT COUNT(*) as page_count 
                                FROM (SELECT 1 FROM {table_name})
                            """)
                        )
                        row_count = result.scalar()
                    else:
                        result = self.db.execute(
                            text(f"SELECT COUNT(*) FROM {table_name}")
                        )
                        row_count = result.scalar()
                    
                    # Rough estimate: ~500 bytes per row (varies by data)
                    estimated_size_mb = round((row_count * 500) / (1024 * 1024), 2)
                    
                    sizes[table_name] = {
                        "rows": row_count,
                        "estimated_size_mb": estimated_size_mb
                    }
                    
                except Exception as e:
                    logger.warning(f"Could not get size for table {table_name}: {e}")
            
            return sizes

        except Exception as e:
            logger.error(f"Error getting table sizes: {e}")
            return {}
        finally:
            self.finish()


# Global instance
db_optimizer: DatabaseOptimizer = None


def get_db_optimizer() -> DatabaseOptimizer:
    """Get or create global database optimizer instance"""
    global db_optimizer
    if db_optimizer is None:
        db_optimizer = DatabaseOptimizer()
    return db_optimizer
