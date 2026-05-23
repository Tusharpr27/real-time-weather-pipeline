"""
Alert notification system module
Handles sending alerts via email and other channels
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from enum import Enum

from config import settings
from src.database.database import create_session
from src.database.models import Alert
from src.utils.logger import logger


class NotificationChannel(str, Enum):
    """Notification channel types"""
    EMAIL = "email"
    LOG = "log"
    DASHBOARD = "dashboard"


class NotificationStatus(str, Enum):
    """Notification delivery status"""
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    RETRY = "retry"


class AlertNotificationQueue:
    """Queue for managing pending notifications"""
    
    def __init__(self):
        self.queue: List[Dict] = []
        self.max_retries = 3
        self.retry_delay_seconds = 300  # 5 minutes
    
    def add(self, alert_id: int, channel: NotificationChannel, data: Dict):
        """Add notification to queue"""
        self.queue.append({
            "alert_id": alert_id,
            "channel": channel,
            "data": data,
            "status": NotificationStatus.PENDING,
            "retries": 0,
            "created_at": datetime.utcnow(),
            "next_retry": datetime.utcnow()
        })
    
    def get_pending(self) -> List[Dict]:
        """Get all pending notifications ready to send"""
        now = datetime.utcnow()
        return [
            n for n in self.queue
            if n["status"] in [NotificationStatus.PENDING, NotificationStatus.RETRY]
            and n["next_retry"] <= now
        ]
    
    def mark_sent(self, alert_id: int):
        """Mark notification as sent"""
        for item in self.queue:
            if item["alert_id"] == alert_id:
                item["status"] = NotificationStatus.SENT
                break
    
    def mark_failed(self, alert_id: int):
        """Mark notification as failed and add to retry queue"""
        for item in self.queue:
            if item["alert_id"] == alert_id:
                if item["retries"] < self.max_retries:
                    item["status"] = NotificationStatus.RETRY
                    item["retries"] += 1
                    item["next_retry"] = datetime.utcnow() + timedelta(
                        seconds=self.retry_delay_seconds
                    )
                else:
                    item["status"] = NotificationStatus.FAILED
                break


class EmailNotifier:
    """Sends email notifications"""
    
    def __init__(self):
        self.smtp_server = settings.smtp_server
        self.smtp_port = settings.smtp_port
        self.username = settings.smtp_username
        self.password = settings.smtp_password
        self.enabled = bool(self.username and self.password)
    
    async def send_alert_email(self, 
                               recipient: str,
                               alert_type: str,
                               location: str,
                               description: str,
                               severity: str) -> Tuple[bool, str]:
        """
        Send alert email notification
        
        Returns:
            (success, message)
        """
        if not self.enabled:
            logger.warning("Email notifications disabled - SMTP credentials not configured")
            return False, "Email not configured"
        
        try:
            logger.info(f"📧 Sending {severity} alert email to {recipient}...")
            
            # Create email
            msg = MIMEMultipart("alternative")
            msg["Subject"] = f"⚠️  Weather Alert - {severity.upper()}: {alert_type}"
            msg["From"] = self.username
            msg["To"] = recipient
            
            # Plain text version
            text = f"""
Weather Alert Notification
========================

Type: {alert_type}
Severity: {severity.upper()}
Location: {location}
Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}

Description:
{description}

Dashboard: http://localhost:8000/api/weather/current/{location}
            """
            
            # HTML version
            html = f"""
            <html>
              <body style="font-family: Arial, sans-serif;">
                <div style="background-color: #f5f5f5; padding: 20px; border-radius: 5px;">
                  <h2 style="color: #d9534f;">⚠️ Weather Alert</h2>
                  <table style="width: 100%; margin: 20px 0;">
                    <tr>
                      <td style="font-weight: bold;">Type:</td>
                      <td>{alert_type}</td>
                    </tr>
                    <tr>
                      <td style="font-weight: bold;">Severity:</td>
                      <td style="color: #d9534f; font-weight: bold;">{severity.upper()}</td>
                    </tr>
                    <tr>
                      <td style="font-weight: bold;">Location:</td>
                      <td>{location}</td>
                    </tr>
                    <tr>
                      <td style="font-weight: bold;">Time:</td>
                      <td>{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}</td>
                    </tr>
                  </table>
                  <h3>Description:</h3>
                  <p>{description}</p>
                </div>
              </body>
            </html>
            """
            
            part1 = MIMEText(text, "plain")
            part2 = MIMEText(html, "html")
            msg.attach(part1)
            msg.attach(part2)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)
            
            logger.info(f"✅ Alert email sent to {recipient}")
            return True, "Email sent successfully"
            
        except Exception as e:
            logger.error(f"❌ Error sending email to {recipient}: {e}")
            return False, str(e)


class AlertNotifier:
    """Main alert notification system"""
    
    def __init__(self):
        self.email_notifier = EmailNotifier()
        self.notification_queue = AlertNotificationQueue()
        self.db: Optional[Session] = None
    
    def start(self):
        """Initialize"""
        self.db = create_session()
    
    def finish(self):
        """Cleanup"""
        if self.db:
            self.db.close()
            self.db = None
    
    async def notify_alert(self,
                          alert_id: int,
                          channels: List[NotificationChannel] = None,
                          recipients: List[str] = None) -> Dict:
        """
        Send alert notifications through specified channels
        
        Args:
            alert_id: Alert ID to notify about
            channels: Notification channels (default: [EMAIL, LOG])
            recipients: Email recipients (overrides config)
            
        Returns:
            Dictionary with notification results
        """
        if channels is None:
            channels = [NotificationChannel.EMAIL, NotificationChannel.LOG]
        
        if recipients is None:
            recipients = [settings.alert_email_to] if settings.alert_email_to else []
        
        self.start()
        results = {
            "alert_id": alert_id,
            "channels": [],
            "timestamp": datetime.utcnow()
        }
        
        try:
            # Get alert details
            alert = self.db.query(Alert).filter(Alert.id == alert_id).first()
            if not alert:
                logger.error(f"Alert {alert_id} not found")
                return results
            
            # Email notification
            if NotificationChannel.EMAIL in channels:
                for recipient in recipients:
                    success, msg = await self.email_notifier.send_alert_email(
                        recipient=recipient,
                        alert_type=alert.alert_type,
                        location=f"Location {alert.location_id}",
                        description=alert.description,
                        severity=alert.severity
                    )
                    results["channels"].append({
                        "channel": NotificationChannel.EMAIL,
                        "recipient": recipient,
                        "success": success,
                        "message": msg
                    })
            
            # Log notification
            if NotificationChannel.LOG in channels:
                logger.info(f"🔔 ALERT: [{alert.severity}] {alert.alert_type} - {alert.description}")
                results["channels"].append({
                    "channel": NotificationChannel.LOG,
                    "success": True,
                    "message": "Logged"
                })
            
            # Dashboard notification (stored for UI display)
            if NotificationChannel.DASHBOARD in channels:
                # In production, could push to WebSocket or event stream
                results["channels"].append({
                    "channel": NotificationChannel.DASHBOARD,
                    "success": True,
                    "message": "Queued for dashboard"
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Error notifying about alert {alert_id}: {e}")
            return results
        finally:
            self.finish()
    
    async def notify_batch(self, alert_ids: List[int]) -> Dict:
        """
        Notify about multiple alerts
        
        Args:
            alert_ids: List of alert IDs
            
        Returns:
            Dictionary with results for each alert
        """
        results = {
            "total": len(alert_ids),
            "successful": 0,
            "failed": 0,
            "alerts": []
        }
        
        for alert_id in alert_ids:
            result = await self.notify_alert(alert_id)
            results["alerts"].append(result)
            
            if all(c["success"] for c in result.get("channels", [])):
                results["successful"] += 1
            else:
                results["failed"] += 1
        
        return results


# Global instance
alert_notifier: Optional[AlertNotifier] = None


def get_alert_notifier() -> AlertNotifier:
    """Get or create global alert notifier instance"""
    global alert_notifier
    if alert_notifier is None:
        alert_notifier = AlertNotifier()
    return alert_notifier
