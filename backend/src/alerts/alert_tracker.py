"""
Alert tracking module
Handles alert acknowledgment, history, and state management
"""
from typing import Dict, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from src.database.database import create_session
from src.database.models import Alert
from src.utils.logger import logger


class AlertTracker:
    """Tracks alert state and history"""
    
    def __init__(self):
        self.db: Optional[Session] = None
        self.acknowledgment_history: Dict[int, Dict] = {}
    
    def start(self):
        """Initialize database session"""
        self.db = create_session()
    
    def finish(self):
        """Close database session"""
        if self.db:
            self.db.close()
            self.db = None
    
    async def acknowledge_alert(self, alert_id: int, user_id: str = "system", 
                                reason: str = "") -> bool:
        """
        Acknowledge an alert
        
        Args:
            alert_id: Alert ID
            user_id: User acknowledging the alert
            reason: Acknowledgment reason
            
        Returns:
            True if successful
        """
        self.start()
        
        try:
            alert = self.db.query(Alert).filter(Alert.id == alert_id).first()
            if not alert:
                logger.error(f"Alert {alert_id} not found")
                return False
            
            # Update alert status
            alert.status = "acknowledged"
            alert.acknowledged_at = datetime.utcnow()
            alert.acknowledged_by = user_id
            
            # Store acknowledgment history
            self.acknowledgment_history[alert_id] = {
                "acknowledged_at": datetime.utcnow(),
                "user_id": user_id,
                "reason": reason,
                "previous_status": "active"
            }
            
            self.db.commit()
            
            logger.info(f"✅ Alert {alert_id} acknowledged by {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error acknowledging alert {alert_id}: {e}")
            self.db.rollback()
            return False
        finally:
            self.finish()
    
    async def resolve_alert(self, alert_id: int, user_id: str = "system",
                           resolution: str = "") -> bool:
        """
        Resolve an alert
        
        Args:
            alert_id: Alert ID
            user_id: User resolving the alert
            resolution: Resolution details
            
        Returns:
            True if successful
        """
        self.start()
        
        try:
            alert = self.db.query(Alert).filter(Alert.id == alert_id).first()
            if not alert:
                logger.error(f"Alert {alert_id} not found")
                return False
            
            alert.status = "resolved"
            alert.resolved_at = datetime.utcnow()
            alert.resolved_by = user_id
            
            self.db.commit()
            
            logger.info(f"✅ Alert {alert_id} resolved by {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error resolving alert {alert_id}: {e}")
            self.db.rollback()
            return False
        finally:
            self.finish()
    
    async def reopen_alert(self, alert_id: int) -> bool:
        """
        Reopen a resolved or acknowledged alert
        
        Args:
            alert_id: Alert ID
            
        Returns:
            True if successful
        """
        self.start()
        
        try:
            alert = self.db.query(Alert).filter(Alert.id == alert_id).first()
            if not alert:
                return False
            
            alert.status = "active"
            alert.acknowledged_at = None
            alert.resolved_at = None
            
            self.db.commit()
            
            logger.info(f"✅ Alert {alert_id} reopened")
            return True
            
        except Exception as e:
            logger.error(f"Error reopening alert {alert_id}: {e}")
            self.db.rollback()
            return False
        finally:
            self.finish()
    
    async def get_alert_history(self, alert_id: int) -> Dict:
        """
        Get complete history of an alert
        
        Args:
            alert_id: Alert ID
            
        Returns:
            Alert history with all status changes
        """
        self.start()
        
        try:
            alert = self.db.query(Alert).filter(Alert.id == alert_id).first()
            if not alert:
                return {"error": "Alert not found"}
            
            history = {
                "alert_id": alert_id,
                "alert_type": alert.alert_type,
                "severity": alert.severity,
                "description": alert.description,
                "current_status": alert.status,
                "created_at": alert.created_at,
                "updated_at": alert.updated_at,
                "status_changes": []
            }
            
            # Add creation event
            history["status_changes"].append({
                "status": "created",
                "timestamp": alert.created_at,
                "description": "Alert created"
            })
            
            # Add acknowledgment event
            if alert.acknowledged_at:
                history["status_changes"].append({
                    "status": "acknowledged",
                    "timestamp": alert.acknowledged_at,
                    "user": getattr(alert, 'acknowledged_by', 'unknown'),
                    "description": "Alert acknowledged"
                })
            
            # Add resolution event
            if alert.resolved_at:
                history["status_changes"].append({
                    "status": "resolved",
                    "timestamp": alert.resolved_at,
                    "user": getattr(alert, 'resolved_by', 'unknown'),
                    "description": "Alert resolved"
                })
            
            # Add from acknowledgment history
            if alert_id in self.acknowledgment_history:
                ack = self.acknowledgment_history[alert_id]
                if ack["reason"]:
                    history["acknowledgment_reason"] = ack["reason"]
            
            return history
            
        except Exception as e:
            logger.error(f"Error getting alert history: {e}")
            return {"error": str(e)}
        finally:
            self.finish()
    
    async def get_unresolved_alerts(self, location_id: int = None) -> List[Dict]:
        """
        Get all unresolved alerts
        
        Args:
            location_id: Filter by location (optional)
            
        Returns:
            List of unresolved alerts
        """
        self.start()
        
        try:
            query = self.db.query(Alert).filter(
                Alert.status.in_(["active", "acknowledged"])
            )
            
            if location_id:
                query = query.filter(Alert.location_id == location_id)
            
            alerts = query.order_by(Alert.created_at.desc()).all()
            
            results = []
            for alert in alerts:
                # Provide both `type` and `alert_type`, and map `message` to `description`
                results.append({
                    "id": alert.id,
                    "type": alert.alert_type,
                    "alert_type": alert.alert_type,
                    "severity": alert.severity,
                    "status": alert.status,
                    "created_at": alert.created_at,
                    "message": getattr(alert, 'message', None),
                    "description": getattr(alert, 'message', None),
                    "location_id": alert.location_id,
                    "location": getattr(getattr(alert, 'location', None), 'name', None)
                })

            return results
            
        except Exception as e:
            logger.error(f"Error getting unresolved alerts: {e}")
            return []
        finally:
            self.finish()
    
    async def get_alert_statistics(self) -> Dict:
        """
        Get alert statistics
        
        Returns:
            Dictionary with alert stats
        """
        self.start()
        
        try:
            all_alerts = self.db.query(Alert).all()
            active_alerts = self.db.query(Alert).filter(Alert.status == "active").all()
            acknowledged_alerts = self.db.query(Alert).filter(Alert.status == "acknowledged").all()
            resolved_alerts = self.db.query(Alert).filter(Alert.status == "resolved").all()
            
            # Count by severity
            low_alerts = self.db.query(Alert).filter(Alert.severity == "LOW").all()
            medium_alerts = self.db.query(Alert).filter(Alert.severity == "MEDIUM").all()
            high_alerts = self.db.query(Alert).filter(Alert.severity == "HIGH").all()
            
            return {
                "total_alerts": len(all_alerts),
                "active": len(active_alerts),
                "acknowledged": len(acknowledged_alerts),
                "resolved": len(resolved_alerts),
                "by_severity": {
                    "LOW": len(low_alerts),
                    "MEDIUM": len(medium_alerts),
                    "HIGH": len(high_alerts)
                },
                "timestamp": datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"Error getting alert statistics: {e}")
            return {}
        finally:
            self.finish()


# Global instance
alert_tracker: Optional[AlertTracker] = None


def get_alert_tracker() -> AlertTracker:
    """Get or create global alert tracker"""
    global alert_tracker
    if alert_tracker is None:
        alert_tracker = AlertTracker()
    return alert_tracker
