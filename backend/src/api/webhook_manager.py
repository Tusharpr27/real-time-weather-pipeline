"""
Webhook management module
Handles webhook registration, triggering, and retry logic
"""
from typing import Dict, List, Optional, Callable
from datetime import datetime, timedelta
from enum import Enum
import hashlib
import hmac
import json
import aiohttp
from sqlalchemy.orm import Session

from src.database.database import create_session
from src.utils.logger import logger


class WebhookEvent(str, Enum):
    """Webhook event types"""
    ALERT_CREATED = "alert.created"
    ALERT_ACKNOWLEDGED = "alert.acknowledged"
    ALERT_RESOLVED = "alert.resolved"
    ALERT_ESCALATED = "alert.escalated"
    WEATHER_DATA_COLLECTED = "weather.collected"
    ANOMALY_DETECTED = "anomaly.detected"
    METRIC_CALCULATED = "metric.calculated"
    DATA_ARCHIVED = "data.archived"


class WebhookStatus(str, Enum):
    """Webhook subscription status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    FAILED = "failed"
    SUSPENDED = "suspended"


class WebhookSubscription:
    """Represents a webhook subscription"""
    
    def __init__(self,
                 subscription_id: str,
                 event: WebhookEvent,
                 url: str,
                 secret: str,
                 status: WebhookStatus = WebhookStatus.ACTIVE):
        self.subscription_id = subscription_id
        self.event = event
        self.url = url
        self.secret = secret
        self.status = status
        self.created_at = datetime.utcnow()
        self.last_triggered = None
        self.failure_count = 0
        self.max_failures = 5
    
    def generate_signature(self, payload: str) -> str:
        """Generate HMAC signature for webhook payload"""
        return hmac.new(
            self.secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "subscription_id": self.subscription_id,
            "event": self.event,
            "url": self.url,
            "status": self.status,
            "created_at": self.created_at,
            "last_triggered": self.last_triggered,
            "failure_count": self.failure_count
        }


class WebhookManager:
    """Manages webhook subscriptions and delivery"""
    
    def __init__(self):
        self.subscriptions: Dict[str, WebhookSubscription] = {}
        self.db: Optional[Session] = None
        self.retry_queue: List[Dict] = []
        self.max_retries = 3
        self.retry_delay_seconds = 60
    
    def start(self):
        """Initialize"""
        self.db = create_session()
    
    def finish(self):
        """Cleanup"""
        if self.db:
            self.db.close()
            self.db = None
    
    def register_webhook(self, 
                        event: WebhookEvent,
                        url: str,
                        secret: str = "") -> str:
        """
        Register a new webhook subscription
        
        Args:
            event: Event type to trigger on
            url: Webhook URL to POST to
            secret: Secret for HMAC signature
            
        Returns:
            Subscription ID
        """
        import uuid
        
        subscription_id = str(uuid.uuid4())
        
        if not secret:
            secret = str(uuid.uuid4())
        
        subscription = WebhookSubscription(
            subscription_id=subscription_id,
            event=event,
            url=url,
            secret=secret
        )
        
        self.subscriptions[subscription_id] = subscription
        
        logger.info(f"✅ Registered webhook {subscription_id} for {event}")
        return subscription_id
    
    def unregister_webhook(self, subscription_id: str) -> bool:
        """
        Unregister a webhook subscription
        
        Args:
            subscription_id: Subscription to remove
            
        Returns:
            True if removed, False if not found
        """
        if subscription_id in self.subscriptions:
            event = self.subscriptions[subscription_id].event
            del self.subscriptions[subscription_id]
            logger.info(f"✅ Unregistered webhook {subscription_id} from {event}")
            return True
        
        logger.warning(f"Webhook {subscription_id} not found")
        return False
    
    def update_webhook_status(self, subscription_id: str, 
                             status: WebhookStatus) -> bool:
        """Update webhook subscription status"""
        if subscription_id not in self.subscriptions:
            return False
        
        self.subscriptions[subscription_id].status = status
        logger.info(f"Updated webhook {subscription_id} status to {status}")
        return True
    
    def get_subscriptions(self, event: WebhookEvent = None) -> List[WebhookSubscription]:
        """
        Get subscriptions, optionally filtered by event
        
        Args:
            event: Filter by event type (optional)
            
        Returns:
            List of matching subscriptions
        """
        subs = list(self.subscriptions.values())
        
        if event:
            subs = [s for s in subs if s.event == event]
        
        # Only return active subscriptions
        return [s for s in subs if s.status == WebhookStatus.ACTIVE]
    
    async def trigger_webhook(self, event: WebhookEvent, data: Dict) -> Dict:
        """
        Trigger webhooks for an event
        
        Args:
            event: Event type
            data: Event payload
            
        Returns:
            Dictionary with results
        """
        subscriptions = self.get_subscriptions(event)
        
        if not subscriptions:
            logger.debug(f"No active webhooks for {event}")
            return {"event": event, "triggered": 0}
        
        logger.info(f"🔔 Triggering {len(subscriptions)} webhooks for {event}")
        
        results = {
            "event": event,
            "triggered": 0,
            "failed": 0,
            "details": []
        }
        
        for subscription in subscriptions:
            success = await self._send_webhook(subscription, event, data)
            
            if success:
                results["triggered"] += 1
                subscription.last_triggered = datetime.utcnow()
                subscription.failure_count = 0
            else:
                results["failed"] += 1
                subscription.failure_count += 1
                
                # Suspend if too many failures
                if subscription.failure_count >= subscription.max_failures:
                    subscription.status = WebhookStatus.SUSPENDED
                    logger.warning(f"Suspended webhook {subscription.subscription_id} (too many failures)")
                
                # Add to retry queue
                self.retry_queue.append({
                    "subscription_id": subscription.subscription_id,
                    "event": event,
                    "data": data,
                    "retries": 0,
                    "next_retry": datetime.utcnow() + timedelta(seconds=self.retry_delay_seconds)
                })
            
            results["details"].append({
                "subscription_id": subscription.subscription_id,
                "url": subscription.url,
                "success": success
            })
        
        return results
    
    async def _send_webhook(self, subscription: WebhookSubscription,
                           event: WebhookEvent, data: Dict) -> bool:
        """
        Send webhook to URL
        
        Args:
            subscription: Webhook subscription
            event: Event type
            data: Event payload
            
        Returns:
            True if successful
        """
        try:
            payload = json.dumps({
                "event": event,
                "timestamp": datetime.utcnow().isoformat(),
                "data": data
            })
            
            # Generate signature
            signature = subscription.generate_signature(payload)
            
            headers = {
                "Content-Type": "application/json",
                "X-Webhook-Signature": signature,
                "X-Webhook-Event": event
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    subscription.url,
                    data=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        logger.debug(f"✅ Webhook {subscription.subscription_id} succeeded")
                        return True
                    else:
                        logger.warning(f"❌ Webhook {subscription.subscription_id} returned {response.status}")
                        return False
                        
        except asyncio.TimeoutError:
            logger.error(f"Webhook {subscription.subscription_id} timeout")
            return False
        except Exception as e:
            logger.error(f"Error sending webhook {subscription.subscription_id}: {e}")
            return False
    
    async def retry_failed_webhooks(self) -> Dict:
        """Retry failed webhook deliveries"""
        now = datetime.utcnow()
        retries_performed = 0
        items_to_remove = []
        
        for idx, item in enumerate(self.retry_queue):
            if item["next_retry"] <= now:
                subscription_id = item["subscription_id"]
                
                if subscription_id not in self.subscriptions:
                    items_to_remove.append(idx)
                    continue
                
                subscription = self.subscriptions[subscription_id]
                success = await self._send_webhook(
                    subscription,
                    item["event"],
                    item["data"]
                )
                
                if success:
                    items_to_remove.append(idx)
                    retries_performed += 1
                elif item["retries"] < self.max_retries:
                    item["retries"] += 1
                    item["next_retry"] = now + timedelta(seconds=self.retry_delay_seconds)
                else:
                    logger.error(f"Webhook {subscription_id} max retries exceeded")
                    items_to_remove.append(idx)
        
        # Remove processed items (in reverse to maintain indices)
        for idx in reversed(items_to_remove):
            self.retry_queue.pop(idx)
        
        return {
            "retries_performed": retries_performed,
            "pending": len(self.retry_queue)
        }
    
    def get_statistics(self) -> Dict:
        """Get webhook statistics"""
        active = sum(1 for s in self.subscriptions.values() if s.status == WebhookStatus.ACTIVE)
        failed = sum(1 for s in self.subscriptions.values() if s.status == WebhookStatus.FAILED)
        suspended = sum(1 for s in self.subscriptions.values() if s.status == WebhookStatus.SUSPENDED)
        
        by_event = {}
        for subscription in self.subscriptions.values():
            if subscription.event not in by_event:
                by_event[subscription.event] = 0
            by_event[subscription.event] += 1
        
        return {
            "total": len(self.subscriptions),
            "active": active,
            "failed": failed,
            "suspended": suspended,
            "by_event": by_event,
            "pending_retries": len(self.retry_queue)
        }


# Global instance
webhook_manager: Optional[WebhookManager] = None


def get_webhook_manager() -> WebhookManager:
    """Get or create global webhook manager"""
    global webhook_manager
    if webhook_manager is None:
        webhook_manager = WebhookManager()
    return webhook_manager


# Required import for async
import asyncio
