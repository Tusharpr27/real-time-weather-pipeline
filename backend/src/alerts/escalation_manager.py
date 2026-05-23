"""
Alert escalation manager module
Handles alert escalation based on severity, age, and unacknowledged status
"""
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from src.database.database import create_session
from src.database.models import Alert
from src.database.repository import AlertRepository
from src.utils.logger import logger


class EscalationRule:
    """Defines escalation behavior"""
    
    def __init__(self,
                 severity: str,
                 initial_delay_hours: int = 1,
                 escalation_delay_hours: int = 2,
                 max_escalations: int = 3):
        """
        Args:
            severity: Alert severity level
            initial_delay_hours: Hours before first escalation
            escalation_delay_hours: Hours between escalations
            max_escalations: Maximum number of escalations
        """
        self.severity = severity
        self.initial_delay_hours = initial_delay_hours
        self.escalation_delay_hours = escalation_delay_hours
        self.max_escalations = max_escalations


class EscalationManager:
    """Manages alert escalation"""
    
    def __init__(self):
        self.db: Optional[Session] = None
        self.escalation_rules = self._default_escalation_rules()
    
    def _default_escalation_rules(self) -> Dict[str, EscalationRule]:
        """Get default escalation rules"""
        return {
            "LOW": EscalationRule("LOW", initial_delay_hours=24, escalation_delay_hours=48, max_escalations=0),
            "MEDIUM": EscalationRule("MEDIUM", initial_delay_hours=2, escalation_delay_hours=4, max_escalations=2),
            "HIGH": EscalationRule("HIGH", initial_delay_hours=0.5, escalation_delay_hours=1, max_escalations=5),
        }
    
    def start(self):
        """Initialize database session"""
        self.db = create_session()
    
    def finish(self):
        """Close database session"""
        if self.db:
            self.db.close()
            self.db = None
    
    def set_escalation_rule(self, rule: EscalationRule):
        """Update escalation rule for a severity level"""
        self.escalation_rules[rule.severity] = rule
        logger.info(f"Updated escalation rule for {rule.severity}")
    
    async def check_escalations(self) -> List[Dict]:
        """
        Check for alerts that need escalation
        
        Returns:
            List of alerts needing escalation
        """
        self.start()
        escalations = []
        
        try:
            # Get active alerts
            active_alerts = self.db.query(Alert).filter(
                Alert.status != "resolved"
            ).all()
            
            now = datetime.utcnow()
            
            for alert in active_alerts:
                rule = self.escalation_rules.get(alert.severity)
                if not rule:
                    continue
                
                # Calculate time since creation
                age = now - alert.created_at
                age_hours = age.total_seconds() / 3600
                
                # Determine current escalation level
                current_escalation = getattr(alert, 'escalation_level', 0)
                
                # Calculate when next escalation should occur
                if current_escalation == 0:
                    # First escalation
                    if age_hours >= rule.initial_delay_hours:
                        escalations.append({
                            "alert_id": alert.id,
                            "severity": alert.severity,
                            "age_hours": age_hours,
                            "current_level": 0,
                            "next_level": 1,
                            "reason": f"Initial escalation after {age_hours:.1f} hours"
                        })
                else:
                    # Subsequent escalations
                    if current_escalation < rule.max_escalations:
                        time_since_last_escalation = age_hours - (
                            rule.initial_delay_hours + 
                            (current_escalation - 1) * rule.escalation_delay_hours
                        )
                        
                        if time_since_last_escalation >= rule.escalation_delay_hours:
                            escalations.append({
                                "alert_id": alert.id,
                                "severity": alert.severity,
                                "age_hours": age_hours,
                                "current_level": current_escalation,
                                "next_level": current_escalation + 1,
                                "reason": f"Escalation level {current_escalation + 1}"
                            })
            
            logger.info(f"Found {len(escalations)} alerts needing escalation")
            return escalations
            
        except Exception as e:
            logger.error(f"Error checking escalations: {e}")
            return []
        finally:
            self.finish()
    
    async def escalate_alert(self, alert_id: int, new_level: int = None) -> bool:
        """
        Escalate an alert to the next level
        
        Args:
            alert_id: Alert to escalate
            new_level: Specific level to escalate to
            
        Returns:
            True if escalation successful
        """
        self.start()
        
        try:
            alert = self.db.query(Alert).filter(Alert.id == alert_id).first()
            if not alert:
                logger.error(f"Alert {alert_id} not found")
                return False
            
            current_level = getattr(alert, 'escalation_level', 0)
            next_level = new_level if new_level else current_level + 1
            
            # Update escalation level
            alert.escalation_level = next_level
            alert.escalated_at = datetime.utcnow()
            
            self.db.commit()
            
            logger.info(f"✅ Escalated alert {alert_id} from level {current_level} to {next_level}")
            return True
            
        except Exception as e:
            logger.error(f"Error escalating alert {alert_id}: {e}")
            self.db.rollback()
            return False
        finally:
            self.finish()
    
    async def get_alert_status(self, alert_id: int) -> Dict:
        """
        Get current escalation status of an alert
        
        Args:
            alert_id: Alert ID
            
        Returns:
            Dictionary with escalation info
        """
        self.start()
        
        try:
            alert = self.db.query(Alert).filter(Alert.id == alert_id).first()
            if not alert:
                return {"error": "Alert not found"}
            
            rule = self.escalation_rules.get(alert.severity)
            current_level = getattr(alert, 'escalation_level', 0)
            age = datetime.utcnow() - alert.created_at
            age_hours = age.total_seconds() / 3600
            
            status = {
                "alert_id": alert_id,
                "severity": alert.severity,
                "status": alert.status,
                "age_hours": round(age_hours, 2),
                "escalation_level": current_level,
                "created_at": alert.created_at,
                "escalated_at": getattr(alert, 'escalated_at', None)
            }
            
            if rule:
                status["max_escalations"] = rule.max_escalations
                status["can_escalate"] = current_level < rule.max_escalations
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting alert status: {e}")
            return {"error": str(e)}
        finally:
            self.finish()
    
    async def reset_escalation(self, alert_id: int) -> bool:
        """
        Reset escalation level (when alert is acknowledged or resolved)
        
        Args:
            alert_id: Alert ID
            
        Returns:
            True if reset successful
        """
        self.start()
        
        try:
            alert = self.db.query(Alert).filter(Alert.id == alert_id).first()
            if not alert:
                return False
            
            alert.escalation_level = 0
            alert.escalated_at = None
            
            self.db.commit()
            
            logger.info(f"✅ Reset escalation for alert {alert_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error resetting escalation: {e}")
            self.db.rollback()
            return False
        finally:
            self.finish()


# Global instance
escalation_manager: Optional[EscalationManager] = None


def get_escalation_manager() -> EscalationManager:
    """Get or create global escalation manager"""
    global escalation_manager
    if escalation_manager is None:
        escalation_manager = EscalationManager()
    return escalation_manager
