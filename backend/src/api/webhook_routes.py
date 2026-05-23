"""
Webhook management REST API routes
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime

from src.api.webhook_manager import get_webhook_manager, WebhookEvent, WebhookStatus
from src.utils.logger import logger

router = APIRouter(prefix="/api/webhooks", tags=["webhooks"])


@router.post("/subscribe")
async def subscribe_webhook(event: str, url: str, secret: str = None):
    """Subscribe to webhook event"""
    try:
        manager = get_webhook_manager()
        
        try:
            event_enum = WebhookEvent(event)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid event: {event}")
        
        subscription_id = manager.register_webhook(event_enum, url, secret or "")
        
        return {
            "status": "success",
            "subscription_id": subscription_id,
            "event": event,
            "url": url,
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        logger.error(f"Error subscribing webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/unsubscribe/{subscription_id}")
async def unsubscribe_webhook(subscription_id: str):
    """Unsubscribe from webhook"""
    try:
        manager = get_webhook_manager()
        success = manager.unregister_webhook(subscription_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Subscription not found")
        
        return {
            "status": "success",
            "message": "Unsubscribed",
            "subscription_id": subscription_id
        }
    except Exception as e:
        logger.error(f"Error unsubscribing webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/subscriptions")
async def get_webhooks(event: str = Query(None, description="Filter by event")):
    """Get webhook subscriptions"""
    try:
        manager = get_webhook_manager()
        
        event_filter = None
        if event:
            try:
                event_filter = WebhookEvent(event)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid event: {event}")
        
        subscriptions = manager.get_subscriptions(event_filter)
        
        return {
            "status": "success",
            "count": len(subscriptions),
            "subscriptions": [sub.to_dict() for sub in subscriptions]
        }
    except Exception as e:
        logger.error(f"Error getting webhooks: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/subscriptions/{subscription_id}")
async def get_webhook(subscription_id: str):
    """Get specific webhook subscription"""
    try:
        manager = get_webhook_manager()
        
        if subscription_id not in manager.subscriptions:
            raise HTTPException(status_code=404, detail="Subscription not found")
        
        subscription = manager.subscriptions[subscription_id]
        
        return {
            "status": "success",
            "subscription": subscription.to_dict()
        }
    except Exception as e:
        logger.error(f"Error getting webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/subscriptions/{subscription_id}/status")
async def update_webhook_status(subscription_id: str, status: str):
    """Update webhook subscription status"""
    try:
        manager = get_webhook_manager()
        
        try:
            status_enum = WebhookStatus(status)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid status: {status}")
        
        success = manager.update_webhook_status(subscription_id, status_enum)
        
        if not success:
            raise HTTPException(status_code=404, detail="Subscription not found")
        
        return {
            "status": "success",
            "message": f"Updated to {status}",
            "subscription_id": subscription_id
        }
    except Exception as e:
        logger.error(f"Error updating webhook status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statistics")
async def get_webhook_stats():
    """Get webhook statistics"""
    try:
        manager = get_webhook_manager()
        stats = manager.get_statistics()
        
        return {
            "status": "success",
            "data": stats
        }
    except Exception as e:
        logger.error(f"Error getting webhook stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/retries")
async def get_pending_retries():
    """Get pending webhook retries"""
    try:
        manager = get_webhook_manager()
        
        return {
            "status": "success",
            "pending": len(manager.retry_queue),
            "next_retry_time": manager.retry_queue[0]["next_retry"] if manager.retry_queue else None
        }
    except Exception as e:
        logger.error(f"Error getting retries: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/retries/process")
async def process_retries():
    """Manually trigger retry processing"""
    try:
        manager = get_webhook_manager()
        results = await manager.retry_failed_webhooks()
        
        return {
            "status": "success",
            "data": results
        }
    except Exception as e:
        logger.error(f"Error processing retries: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def webhook_health():
    """Webhook system health"""
    try:
        manager = get_webhook_manager()
        stats = manager.get_statistics()
        
        return {
            "status": "healthy",
            "components": {
                "subscriptions": "operational",
                "delivery": "operational",
                "retry": "operational"
            },
            "statistics": stats,
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        logger.error(f"Webhook health check failed: {e}")
        return {
            "status": "degraded",
            "error": str(e),
            "timestamp": datetime.utcnow()
        }
