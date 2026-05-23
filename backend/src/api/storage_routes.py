"""
Storage management API routes
Provides endpoints for storage stats, cleanup, and optimization
"""
from fastapi import APIRouter, HTTPException, Query
from datetime import datetime

from src.storage.data_cleanup import get_data_cleanup
from src.storage.archive_manager import get_archive_manager
from src.storage.db_optimizer import get_db_optimizer
from src.storage.retention_policy import get_retention_policy_manager
from src.utils.logger import logger


router = APIRouter(prefix="/api/storage", tags=["Storage Management"])


@router.get("/stats", summary="Get storage statistics")
async def get_storage_stats():
    """Get database and archive statistics"""
    try:
        optimizer = get_db_optimizer()
        archive_mgr = get_archive_manager()
        cleanup = get_data_cleanup()
        
        # Get database stats
        db_stats = await optimizer.get_database_stats()
        table_sizes = await optimizer.get_table_sizes()
        
        # Get archive stats
        archive_stats = await archive_mgr.get_archive_stats()
        
        # Get data size info
        data_info = await cleanup.get_data_size_info()
        
        return {
            "timestamp": datetime.utcnow(),
            "database": {
                "stats": db_stats,
                "table_sizes": table_sizes
            },
            "archives": archive_stats,
            "data_info": data_info
        }
        
    except Exception as e:
        logger.error(f"Error getting storage stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/retention-policy", summary="Get data retention policy")
async def get_retention_policy():
    """Get current data retention policy"""
    try:
        policy_mgr = get_retention_policy_manager()
        return {
            "policy": policy_mgr.get_policy_dict(),
            "valid": policy_mgr.validate_policy(),
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Error getting retention policy: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cleanup", summary="Run data cleanup")
async def run_cleanup(
    weather_days: int = Query(30, ge=1, le=365),
    metrics_days: int = Query(90, ge=1, le=365),
    alerts_days: int = Query(60, ge=1, le=365)
):
    """
    Run data cleanup on demand
    
    Args:
        weather_days: Keep weather data for N days
        metrics_days: Keep metrics for N days
        alerts_days: Keep alerts for N days
    """
    try:
        logger.info(f"🧹 Running on-demand cleanup...")
        
        cleanup = get_data_cleanup()
        stats = await cleanup.cleanup_all(
            weather_retention=weather_days,
            metrics_retention=metrics_days,
            alerts_retention=alerts_days
        )
        
        return {
            "status": "success",
            "statistics": stats,
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Error running cleanup: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/optimize", summary="Run database optimization")
async def run_optimization():
    """Run database optimization on demand"""
    try:
        logger.info("🔧 Running on-demand database optimization...")
        
        optimizer = get_db_optimizer()
        results = await optimizer.optimize_all()
        
        return {
            "status": "success",
            "results": results,
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Error running optimization: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/archive", summary="Archive metrics")
async def archive_metrics(
    days: int = Query(30, ge=1, le=365),
    compress: bool = Query(True)
):
    """
    Archive metrics to file
    
    Args:
        days: Archive metrics from last N days
        compress: Whether to compress archives
    """
    try:
        logger.info(f"📦 Archiving metrics from last {days} days...")
        
        archive_mgr = get_archive_manager()
        file_path = await archive_mgr.export_weekly_metrics(compress=compress)
        
        return {
            "status": "success",
            "archive_file": file_path,
            "compressed": compress,
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Error archiving metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/archives", summary="Get archive information")
async def get_archives():
    """Get list and statistics of archived files"""
    try:
        archive_mgr = get_archive_manager()
        stats = await archive_mgr.get_archive_stats()
        
        return {
            "archives": stats["archives"],
            "total_count": stats["archive_count"],
            "total_size_mb": stats["total_size_mb"],
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Error getting archives: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/archives/cleanup", summary="Clean old archives")
async def cleanup_old_archives(
    retention_days: int = Query(90, ge=1, le=365)
):
    """
    Delete archived files older than retention period
    
    Args:
        retention_days: Keep archives for N days
    """
    try:
        logger.info(f"🗑️  Cleaning archives older than {retention_days} days...")
        
        archive_mgr = get_archive_manager()
        deleted = await archive_mgr.cleanup_old_archives(retention_days)
        
        return {
            "status": "success",
            "archives_deleted": deleted,
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Error cleaning archives: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/archives/rotate", summary="Rotate archives")
async def rotate_archives(
    max_count: int = Query(12, ge=1, le=50)
):
    """
    Keep only the most recent N archives
    
    Args:
        max_count: Maximum number of archives to keep
    """
    try:
        logger.info(f"🔄 Rotating archives - keeping last {max_count}...")
        
        archive_mgr = get_archive_manager()
        deleted = await archive_mgr.rotate_archives(max_count)
        
        return {
            "status": "success",
            "archives_deleted": deleted,
            "max_kept": max_count,
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Error rotating archives: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health", summary="Storage system health")
async def storage_health():
    """Get storage system health status"""
    try:
        optimizer = get_db_optimizer()
        db_stats = await optimizer.get_database_stats()
        archive_mgr = get_archive_manager()
        archive_stats = await archive_mgr.get_archive_stats()
        
        # Determine health based on stats
        total_rows = sum(t["row_count"] for t in db_stats.get("tables", []))
        total_size_mb = archive_stats.get("total_size_mb", 0)
        
        health_status = "healthy"
        if total_rows > 1000000:
            health_status = "warning"  # Database getting large
        if total_size_mb > 500:
            health_status = "warning"  # Archives getting large
        
        return {
            "status": health_status,
            "total_database_rows": total_rows,
            "total_archive_size_mb": total_size_mb,
            "table_count": len(db_stats.get("tables", [])),
            "archive_count": archive_stats.get("archive_count", 0),
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Error getting storage health: {e}")
        return {"status": "error", "detail": str(e)}
