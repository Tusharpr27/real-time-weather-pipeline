"""
Real-time WebSocket routes
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from typing import Optional
import uuid

from src.api.websocket_handler import get_websocket_handler, RealtimeEvent
from src.utils.logger import logger

router = APIRouter(prefix="/api/realtime", tags=["realtime"])


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Main WebSocket endpoint for real-time updates"""
    client_id = str(uuid.uuid4())
    handler = get_websocket_handler()
    
    try:
        await handler.connect(client_id, websocket)
        
        while True:
            # Receive message from client
            message = await handler.receive_message(client_id)
            
            if not message:
                break
            
            # Handle subscription messages
            msg_type = message.get("type")
            
            if msg_type == "subscribe":
                event = message.get("event")
                location_ids = message.get("locations")
                
                try:
                    event_enum = RealtimeEvent(event)
                    handler.subscribe(client_id, event_enum, location_ids)
                    
                    await handler.send_message(client_id, RealtimeEvent.SUBSCRIPTION, {
                        "status": "subscribed",
                        "event": event,
                        "locations": location_ids or "all"
                    })
                except ValueError:
                    await handler.send_message(client_id, RealtimeEvent.SUBSCRIPTION, {
                        "status": "error",
                        "message": f"Invalid event: {event}"
                    })
            
            elif msg_type == "unsubscribe":
                event = message.get("event")
                
                try:
                    event_enum = RealtimeEvent(event)
                    handler.unsubscribe(client_id, event_enum)
                    
                    await handler.send_message(client_id, RealtimeEvent.SUBSCRIPTION, {
                        "status": "unsubscribed",
                        "event": event
                    })
                except ValueError:
                    pass
            
            elif msg_type == "ping":
                await handler.send_message(client_id, RealtimeEvent.CONNECTION, {
                    "status": "pong"
                })
    
    except WebSocketDisconnect:
        handler.disconnect(client_id)
    except Exception as e:
        logger.error(f"WebSocket error for {client_id}: {e}")
        handler.disconnect(client_id)


@router.get("/status")
async def get_realtime_status():
    """Get real-time system status"""
    try:
        handler = get_websocket_handler()
        stats = handler.get_statistics()
        
        return {
            "status": "operational",
            "statistics": stats,
            "events": [event.value for event in RealtimeEvent]
        }
    except Exception as e:
        logger.error(f"Error getting realtime status: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


@router.get("/connections")
async def get_connections():
    """Get connected clients"""
    try:
        handler = get_websocket_handler()
        
        return {
            "status": "success",
            "connected_clients": handler.get_connected_clients(),
            "total_subscriptions": sum(len(subs) for subs in handler.subscriptions.values())
        }
    except Exception as e:
        logger.error(f"Error getting connections: {e}")
        raise
