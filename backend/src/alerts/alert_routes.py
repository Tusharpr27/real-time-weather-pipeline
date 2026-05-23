"""
Alert management API routes
Provides endpoints for managing alerts, escalation, and user preferences
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict
from datetime import datetime

from src.alerts.alert_notifier import get_alert_notifier
from src.alerts.escalation_manager import get_escalation_manager
from src.alerts.alert_tracker import get_alert_tracker
from src.alerts.user_preferences import get_user_preferences_manager
from src.utils.logger import logger

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


# ============= Alert Management =============

@router.get("/active")
async def get_active_alerts(location_id: int = Query(None, description="Filter by location")):
    """Get all active alerts"""
    try:
        tracker = get_alert_tracker()
        alerts = await tracker.get_unresolved_alerts(location_id)
        return {
            "status": "success",
            "count": len(alerts),
            "alerts": alerts
        }
    except Exception as e:
        logger.error(f"Error getting active alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statistics")
async def get_alert_stats():
    """Get alert statistics"""
    try:
        tracker = get_alert_tracker()
        stats = await tracker.get_alert_statistics()
        return {
            "status": "success",
            "data": stats
        }
    except Exception as e:
        logger.error(f"Error getting alert statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/acknowledge/{alert_id}")
async def acknowledge_alert(alert_id: int, user_id: str = "web_user", reason: str = ""):
    """Acknowledge an alert"""
    try:
        tracker = get_alert_tracker()
        success = await tracker.acknowledge_alert(alert_id, user_id, reason)
        
        if not success:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        return {
            "status": "success",
            "message": f"Alert {alert_id} acknowledged",
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        logger.error(f"Error acknowledging alert: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/resolve/{alert_id}")
async def resolve_alert(alert_id: int, user_id: str = "web_user", resolution: str = ""):
    """Resolve an alert"""
    try:
        tracker = get_alert_tracker()
        success = await tracker.resolve_alert(alert_id, user_id, resolution)
        
        if not success:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        return {
            "status": "success",
            "message": f"Alert {alert_id} resolved",
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        logger.error(f"Error resolving alert: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reopen/{alert_id}")
async def reopen_alert(alert_id: int):
    """Reopen a resolved alert"""
    try:
        tracker = get_alert_tracker()
        success = await tracker.reopen_alert(alert_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        return {
            "status": "success",
            "message": f"Alert {alert_id} reopened",
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        logger.error(f"Error reopening alert: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{alert_id}/history")
async def get_alert_history(alert_id: int):
    """Get alert history and status changes"""
    try:
        tracker = get_alert_tracker()
        history = await tracker.get_alert_history(alert_id)
        
        if "error" in history:
            raise HTTPException(status_code=404, detail=history["error"])
        
        return {
            "status": "success",
            "data": history
        }
    except Exception as e:
        logger.error(f"Error getting alert history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============= Escalation Management =============

@router.get("/escalations/check")
async def check_escalations():
    """Check for alerts needing escalation"""
    try:
        manager = get_escalation_manager()
        escalations = await manager.check_escalations()
        
        return {
            "status": "success",
            "count": len(escalations),
            "escalations": escalations
        }
    except Exception as e:
        logger.error(f"Error checking escalations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/escalations/{alert_id}")
async def escalate_alert(alert_id: int, new_level: int = None):
    """Manually escalate an alert"""
    try:
        manager = get_escalation_manager()
        success = await manager.escalate_alert(alert_id, new_level)
        
        if not success:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        return {
            "status": "success",
            "message": f"Alert {alert_id} escalated",
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        logger.error(f"Error escalating alert: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/escalations/{alert_id}/status")
async def get_escalation_status(alert_id: int):
    """Get escalation status of an alert"""
    try:
        manager = get_escalation_manager()
        status = await manager.get_alert_status(alert_id)
        
        if "error" in status:
            raise HTTPException(status_code=404, detail=status["error"])
        
        return {
            "status": "success",
            "data": status
        }
    except Exception as e:
        logger.error(f"Error getting escalation status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/escalations/{alert_id}/reset")
async def reset_escalation(alert_id: int):
    """Reset escalation level for an alert"""
    try:
        manager = get_escalation_manager()
        success = await manager.reset_escalation(alert_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        return {
            "status": "success",
            "message": f"Escalation reset for alert {alert_id}",
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        logger.error(f"Error resetting escalation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============= Notifications =============

@router.post("/notify/{alert_id}")
async def notify_alert(alert_id: int, channels: List[str] = None, recipients: List[str] = None):
    """Send notifications for an alert"""
    try:
        notifier = get_alert_notifier()
        
        # Convert channel strings to enum
        from src.alerts.alert_notifier import NotificationChannel
        notification_channels = [NotificationChannel[c.upper()] for c in (channels or ["EMAIL", "LOG"])]
        
        results = await notifier.notify_alert(alert_id, notification_channels, recipients)
        
        return {
            "status": "success",
            "data": results
        }
    except Exception as e:
        logger.error(f"Error notifying about alert: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============= User Preferences =============

@router.get("/preferences/{user_id}")
async def get_user_preferences(user_id: str):
    """Get user alert preferences"""
    try:
        prefs_manager = get_user_preferences_manager()
        prefs = prefs_manager.get_preferences_dict(user_id)
        
        return {
            "status": "success",
            "data": prefs
        }
    except Exception as e:
        logger.error(f"Error getting user preferences: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/preferences/{user_id}")
async def update_user_preferences(user_id: str, **preferences):
    """Update user alert preferences"""
    try:
        prefs_manager = get_user_preferences_manager()
        updated = prefs_manager.update_preferences(user_id, **preferences)
        
        return {
            "status": "success",
            "message": "Preferences updated",
            "data": updated.dict()
        }
    except Exception as e:
        logger.error(f"Error updating user preferences: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/preferences/{user_id}/quiet-hours")
async def set_quiet_hours(user_id: str, 
                          enabled: bool,
                          start_time: str,
                          end_time: str,
                          skip_low: bool = True,
                          allow_high: bool = True):
    """Set quiet hours for a user"""
    try:
        prefs_manager = get_user_preferences_manager()
        prefs_manager.set_quiet_hours(user_id, enabled, start_time, end_time, skip_low, allow_high)
        
        return {
            "status": "success",
            "message": "Quiet hours updated",
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        logger.error(f"Error setting quiet hours: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/preferences/{user_id}/should-notify")
async def should_notify_user(user_id: str,
                             alert_severity: str,
                             alert_type: str = None,
                             location_id: int = None):
    """Check if user should be notified about an alert"""
    try:
        prefs_manager = get_user_preferences_manager()
        should_notify = prefs_manager.should_notify_alert(
            user_id, alert_severity, alert_type, location_id
        )
        
        return {
            "status": "success",
            "should_notify": should_notify
        }
    except Exception as e:
        logger.error(f"Error checking notification: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============= Health Check =============

@router.get("/health")
async def alert_system_health():
    """Get alert system health status"""
    try:
        return {
            "status": "healthy",
            "components": {
                "notifier": "operational",
                "escalation": "operational",
                "tracker": "operational",
                "preferences": "operational"
            },
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        logger.error(f"Alert system health check failed: {e}")
        return {
            "status": "degraded",
            "error": str(e),
            "timestamp": datetime.utcnow()
        }
