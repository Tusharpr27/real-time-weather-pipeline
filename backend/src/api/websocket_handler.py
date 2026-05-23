"""
WebSocket handler for real-time data updates
Manages connections and broadcasts events
"""
from typing import Dict, List, Set, Optional, Callable
from datetime import datetime
from enum import Enum
import json

from fastapi import WebSocket
from src.utils.logger import logger


class RealtimeEvent(str, Enum):
    """Real-time event types"""
    WEATHER_UPDATE = "weather_update"
    ALERT_NEW = "alert_new"
    ALERT_UPDATED = "alert_updated"
    METRIC_CALCULATED = "metric_calculated"
    ANOMALY_DETECTED = "anomaly_detected"
    CONNECTION = "connection"
    SUBSCRIPTION = "subscription"


class RealtimeSubscription:
    """Represents a real-time subscription"""
    
    def __init__(self, client_id: str, event_type: RealtimeEvent):
        self.client_id = client_id
        self.event_type = event_type
        self.location_filters: Set[int] = set()  # Empty = all locations
        self.created_at = datetime.utcnow()
    
    def matches(self, event_type: RealtimeEvent, location_id: int = None) -> bool:
        """Check if subscription matches event"""
        if self.event_type != event_type:
            return False
        
        if not self.location_filters:
            return True  # All locations
        
        return location_id in self.location_filters if location_id else True


class WebSocketHandler:
    """Handles WebSocket connections and messaging"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.subscriptions: Dict[str, List[RealtimeSubscription]] = {}
        self.message_queue: List[Dict] = []
    
    async def connect(self, client_id: str, websocket: WebSocket):
        """
        Register new WebSocket connection
        
        Args:
            client_id: Unique client identifier
            websocket: WebSocket connection
        """
        await websocket.accept()
        self.active_connections[client_id] = websocket
        self.subscriptions[client_id] = []
        
        logger.info(f"WebSocket client {client_id} connected")
        
        # Send connection confirmation
        await self.send_message(client_id, RealtimeEvent.CONNECTION, {
            "status": "connected",
            "client_id": client_id,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    def disconnect(self, client_id: str):
        """
        Unregister WebSocket connection
        
        Args:
            client_id: Client identifier
        """
        if client_id in self.active_connections:
            del self.active_connections[client_id]
        
        if client_id in self.subscriptions:
            del self.subscriptions[client_id]
        
        logger.info(f"WebSocket client {client_id} disconnected")
    
    def subscribe(self,
                 client_id: str,
                 event_type: RealtimeEvent,
                 location_ids: List[int] = None):
        """
        Subscribe client to event type
        
        Args:
            client_id: Client identifier
            event_type: Event to subscribe to
            location_ids: Optional location filter
        """
        if client_id not in self.subscriptions:
            self.subscriptions[client_id] = []
        
        subscription = RealtimeSubscription(client_id, event_type)
        
        if location_ids:
            subscription.location_filters = set(location_ids)
        
        self.subscriptions[client_id].append(subscription)
        
        logger.debug(f"Client {client_id} subscribed to {event_type}")
    
    def unsubscribe(self, client_id: str, event_type: RealtimeEvent):
        """Unsubscribe from event type"""
        if client_id in self.subscriptions:
            self.subscriptions[client_id] = [
                s for s in self.subscriptions[client_id]
                if s.event_type != event_type
            ]
    
    async def send_message(self,
                          client_id: str,
                          event_type: RealtimeEvent,
                          data: Dict):
        """
        Send message to specific client
        
        Args:
            client_id: Target client
            event_type: Event type
            data: Event payload
        """
        if client_id not in self.active_connections:
            return
        
        try:
            message = {
                "event": event_type,
                "timestamp": datetime.utcnow().isoformat(),
                "data": data
            }
            
            await self.active_connections[client_id].send_json(message)
            
        except Exception as e:
            logger.error(f"Error sending to {client_id}: {e}")
            self.disconnect(client_id)
    
    async def broadcast(self,
                       event_type: RealtimeEvent,
                       data: Dict,
                       location_id: int = None):
        """
        Broadcast event to all subscribed clients
        
        Args:
            event_type: Event type
            data: Event payload
            location_id: Optional location filter
        """
        clients_sent = 0
        
        for client_id, subscriptions in self.subscriptions.items():
            # Check if client has matching subscription
            for sub in subscriptions:
                if sub.matches(event_type, location_id):
                    await self.send_message(client_id, event_type, data)
                    clients_sent += 1
                    break
        
        if clients_sent > 0:
            logger.debug(f"Broadcasted {event_type} to {clients_sent} clients")
    
    async def receive_message(self, client_id: str) -> Optional[Dict]:
        """
        Receive message from client
        
        Args:
            client_id: Client identifier
            
        Returns:
            Parsed message or None
        """
        if client_id not in self.active_connections:
            return None
        
        try:
            data = await self.active_connections[client_id].receive_text()
            message = json.loads(data)
            return message
        except Exception as e:
            logger.error(f"Error receiving from {client_id}: {e}")
            self.disconnect(client_id)
            return None
    
    def get_connected_clients(self) -> int:
        """Get count of connected clients"""
        return len(self.active_connections)
    
    def get_subscriptions(self, client_id: str) -> List[Dict]:
        """Get client subscriptions"""
        if client_id not in self.subscriptions:
            return []
        
        return [
            {
                "event": sub.event_type,
                "location_filters": list(sub.location_filters) if sub.location_filters else "all"
            }
            for sub in self.subscriptions[client_id]
        ]
    
    def get_statistics(self) -> Dict:
        """Get WebSocket statistics"""
        total_subs = sum(len(subs) for subs in self.subscriptions.values())
        
        event_counts = {}
        for subs in self.subscriptions.values():
            for sub in subs:
                if sub.event_type not in event_counts:
                    event_counts[sub.event_type] = 0
                event_counts[sub.event_type] += 1
        
        return {
            "connected_clients": len(self.active_connections),
            "total_subscriptions": total_subs,
            "subscriptions_by_event": event_counts,
            "pending_messages": len(self.message_queue)
        }


# Global instance
websocket_handler: Optional[WebSocketHandler] = None


def get_websocket_handler() -> WebSocketHandler:
    """Get or create global WebSocket handler"""
    global websocket_handler
    if websocket_handler is None:
        websocket_handler = WebSocketHandler()
    return websocket_handler


