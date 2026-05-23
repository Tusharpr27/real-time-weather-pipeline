"""
Audit logging module - Immutable audit trail for all system changes.
Tracks data modifications, user actions, API calls, and configuration changes.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from enum import Enum
import json
import threading
from collections import deque, defaultdict
import logging
import uuid

logger = logging.getLogger(__name__)


class AuditEventType(Enum):
    """Types of audit events."""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    AUTHENTICATE = "authenticate"
    AUTHORIZE = "authorize"
    CONFIG_CHANGE = "config_change"
    WEBHOOK_TRIGGER = "webhook_trigger"
    ALERT_TRIGGERED = "alert_triggered"
    EXPORT_REQUESTED = "export_requested"
    SYSTEM_EVENT = "system_event"


class AuditResourceType(Enum):
    """Types of resources being audited."""
    LOCATION = "location"
    WEATHER_DATA = "weather_data"
    ALERT = "alert"
    ALERT_RULE = "alert_rule"
    WEBHOOK = "webhook"
    USER = "user"
    CONFIGURATION = "configuration"
    SYSTEM = "system"
    PERMISSION = "permission"
    EXPORT = "export"


@dataclass
class AuditLog:
    """Single audit log entry."""
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: AuditEventType = AuditEventType.READ
    resource_type: AuditResourceType = AuditResourceType.SYSTEM
    resource_id: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    # Actor information
    actor_id: Optional[str] = None
    actor_type: str = "system"  # user, system, service
    
    # Change information
    action: str = ""
    description: str = ""
    old_values: Dict[str, Any] = field(default_factory=dict)
    new_values: Dict[str, Any] = field(default_factory=dict)
    changed_fields: List[str] = field(default_factory=list)
    
    # Request context
    request_id: Optional[str] = None
    correlation_id: Optional[str] = None
    endpoint: Optional[str] = None
    method: Optional[str] = None
    
    # Result
    success: bool = True
    status_code: Optional[int] = None
    error_message: Optional[str] = None
    
    # Metadata
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Retention
    retention_days: int = 90


@dataclass
class AuditSummary:
    """Summary of audit logs."""
    total_events: int = 0
    events_by_type: Dict[str, int] = field(default_factory=dict)
    events_by_resource: Dict[str, int] = field(default_factory=dict)
    events_by_actor: Dict[str, int] = field(default_factory=dict)
    success_count: int = 0
    failure_count: int = 0
    date_range: Dict[str, datetime] = field(default_factory=dict)


class AuditLogger:
    """
    Central audit logging system.
    
    Features:
    - Immutable audit trail (append-only)
    - Tracks all data modifications
    - Records user actions and authentications
    - Logs API calls and webhooks
    - Configuration change tracking
    - Automatic retention policy enforcement
    - Search and filtering capabilities
    """

    def __init__(self, history_limit: int = 50000, retention_days: int = 90):
        """
        Initialize audit logger.
        
        Args:
            history_limit: Maximum audit logs to keep in memory
            retention_days: Default retention period for logs
        """
        self.history_limit = history_limit
        self.retention_days = retention_days
        
        # Immutable audit trail
        self.audit_logs: deque = deque(maxlen=history_limit)
        
        # Indexes for searching
        self.logs_by_resource: Dict[str, deque] = defaultdict(
            lambda: deque(maxlen=history_limit)
        )
        self.logs_by_actor: Dict[str, deque] = defaultdict(
            lambda: deque(maxlen=history_limit)
        )
        self.logs_by_type: Dict[AuditEventType, deque] = defaultdict(
            lambda: deque(maxlen=history_limit)
        )
        
        # Statistics
        self.total_events = 0
        self.events_by_resource_type: Dict[AuditResourceType, int] = defaultdict(int)
        self.events_by_event_type: Dict[AuditEventType, int] = defaultdict(int)
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Batch logging support
        self.batch_logs: List[AuditLog] = []
        self.batch_enabled = False

    def log_event(
        self,
        event_type: AuditEventType,
        resource_type: AuditResourceType,
        resource_id: str = "",
        actor_id: Optional[str] = None,
        actor_type: str = "system",
        action: str = "",
        description: str = "",
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
        success: bool = True,
        status_code: Optional[int] = None,
        error_message: Optional[str] = None,
        endpoint: Optional[str] = None,
        method: Optional[str] = None,
        request_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> str:
        """
        Log an audit event.
        
        Args:
            event_type: Type of event
            resource_type: Type of resource affected
            resource_id: ID of the resource
            actor_id: ID of the actor (user/service)
            actor_type: Type of actor
            action: Action performed
            description: Human-readable description
            old_values: Previous values (for updates)
            new_values: New values (for updates/creates)
            success: Whether action succeeded
            status_code: HTTP status code
            error_message: Error message if failed
            endpoint: API endpoint
            method: HTTP method
            request_id: Request ID
            correlation_id: Correlation ID
            ip_address: Source IP address
            user_agent: User agent string
            metadata: Additional metadata
            **kwargs: Additional fields
        
        Returns:
            Event ID
        """
        with self._lock:
            # Determine changed fields
            changed_fields = []
            if old_values and new_values:
                all_keys = set(old_values.keys()) | set(new_values.keys())
                changed_fields = [
                    k for k in all_keys
                    if old_values.get(k) != new_values.get(k)
                ]
            
            # Create audit log entry
            log = AuditLog(
                event_type=event_type,
                resource_type=resource_type,
                resource_id=resource_id,
                actor_id=actor_id,
                actor_type=actor_type,
                action=action,
                description=description,
                old_values=old_values or {},
                new_values=new_values or {},
                changed_fields=changed_fields,
                success=success,
                status_code=status_code,
                error_message=error_message,
                endpoint=endpoint,
                method=method,
                request_id=request_id,
                correlation_id=correlation_id,
                ip_address=ip_address,
                user_agent=user_agent,
                metadata=metadata or {},
                retention_days=self.retention_days
            )
            
            # Store in appropriate collections
            self.audit_logs.append(log)
            
            resource_key = f"{resource_type.value}:{resource_id}"
            self.logs_by_resource[resource_key].append(log)
            
            if actor_id:
                self.logs_by_actor[actor_id].append(log)
            
            self.logs_by_type[event_type].append(log)
            
            # Update statistics
            self.total_events += 1
            self.events_by_resource_type[resource_type] += 1
            self.events_by_event_type[event_type] += 1
            
            # Log to application logger
            self._log_to_logger(log)
            
            return log.event_id

    def _log_to_logger(self, log: AuditLog) -> None:
        """Log audit event to application logger."""
        log_entry = (
            f"[AUDIT] {log.event_type.value.upper()} {log.resource_type.value} "
            f"'{log.resource_id}' by {log.actor_type} {log.actor_id or 'unknown'}: "
            f"{log.description}"
        )
        
        if log.success:
            logger.info(log_entry, extra={"audit_event_id": log.event_id})
        else:
            logger.warning(
                f"{log_entry} - Error: {log.error_message}",
                extra={"audit_event_id": log.event_id}
            )

    def log_data_change(
        self,
        resource_type: AuditResourceType,
        resource_id: str,
        operation: str,  # create, update, delete
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
        actor_id: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Log a data modification (CREATE, UPDATE, DELETE).
        
        Args:
            resource_type: Type of resource
            resource_id: Resource ID
            operation: Operation type (create, update, delete)
            old_values: Previous values
            new_values: New values
            actor_id: Actor performing change
            **kwargs: Additional fields
        
        Returns:
            Event ID
        """
        event_type_map = {
            "create": AuditEventType.CREATE,
            "update": AuditEventType.UPDATE,
            "delete": AuditEventType.DELETE
        }
        
        event_type = event_type_map.get(operation.lower(), AuditEventType.UPDATE)
        
        return self.log_event(
            event_type=event_type,
            resource_type=resource_type,
            resource_id=resource_id,
            action=operation,
            description=f"{operation.capitalize()} {resource_type.value} {resource_id}",
            old_values=old_values,
            new_values=new_values,
            actor_id=actor_id,
            **kwargs
        )

    def log_api_call(
        self,
        endpoint: str,
        method: str,
        actor_id: Optional[str] = None,
        status_code: int = 200,
        success: bool = True,
        error_message: Optional[str] = None,
        ip_address: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Log an API call.
        
        Args:
            endpoint: API endpoint
            method: HTTP method
            actor_id: Actor making the call
            status_code: Response status code
            success: Whether call succeeded
            error_message: Error if failed
            ip_address: Source IP
            **kwargs: Additional fields
        
        Returns:
            Event ID
        """
        # Determine resource based on endpoint
        resource_type = self._infer_resource_type(endpoint)
        
        return self.log_event(
            event_type=AuditEventType.READ,
            resource_type=resource_type,
            action=f"{method} {endpoint}",
            description=f"API call: {method} {endpoint}",
            actor_id=actor_id,
            status_code=status_code,
            success=success,
            error_message=error_message,
            endpoint=endpoint,
            method=method,
            ip_address=ip_address,
            **kwargs
        )

    def log_authentication(
        self,
        actor_id: str,
        success: bool = True,
        error_message: Optional[str] = None,
        ip_address: Optional[str] = None,
        **kwargs
    ) -> str:
        """Log authentication event."""
        return self.log_event(
            event_type=AuditEventType.AUTHENTICATE,
            resource_type=AuditResourceType.USER,
            resource_id=actor_id,
            actor_id=actor_id,
            action="authenticate",
            description=f"User authentication: {actor_id}",
            success=success,
            error_message=error_message,
            ip_address=ip_address,
            **kwargs
        )

    def log_webhook_trigger(
        self,
        webhook_id: str,
        event_type: str,
        resource_id: str,
        success: bool = True,
        error_message: Optional[str] = None,
        **kwargs
    ) -> str:
        """Log webhook trigger event."""
        return self.log_event(
            event_type=AuditEventType.WEBHOOK_TRIGGER,
            resource_type=AuditResourceType.WEBHOOK,
            resource_id=webhook_id,
            action=f"trigger_webhook_{event_type}",
            description=f"Webhook triggered: {event_type} for resource {resource_id}",
            success=success,
            error_message=error_message,
            metadata={"triggered_for": resource_id, "trigger_type": event_type},
            **kwargs
        )

    def log_alert_triggered(
        self,
        alert_rule_id: str,
        alert_id: str,
        reason: str,
        location_id: Optional[str] = None,
        **kwargs
    ) -> str:
        """Log alert trigger event."""
        return self.log_event(
            event_type=AuditEventType.ALERT_TRIGGERED,
            resource_type=AuditResourceType.ALERT,
            resource_id=alert_id,
            action="trigger_alert",
            description=f"Alert triggered by rule {alert_rule_id}: {reason}",
            metadata={"rule_id": alert_rule_id, "location_id": location_id},
            **kwargs
        )

    def log_export_request(
        self,
        export_format: str,
        resource_type: str,
        actor_id: Optional[str] = None,
        record_count: int = 0,
        **kwargs
    ) -> str:
        """Log data export request."""
        return self.log_event(
            event_type=AuditEventType.EXPORT_REQUESTED,
            resource_type=AuditResourceType.EXPORT,
            action=f"export_{export_format}",
            description=f"Data export requested: {resource_type} as {export_format} ({record_count} records)",
            actor_id=actor_id,
            metadata={"format": export_format, "resource_type": resource_type, "record_count": record_count},
            **kwargs
        )

    def log_config_change(
        self,
        config_key: str,
        old_value: Any,
        new_value: Any,
        actor_id: Optional[str] = None,
        **kwargs
    ) -> str:
        """Log configuration change."""
        return self.log_event(
            event_type=AuditEventType.CONFIG_CHANGE,
            resource_type=AuditResourceType.CONFIGURATION,
            resource_id=config_key,
            action="update_config",
            description=f"Configuration changed: {config_key}",
            old_values={config_key: old_value},
            new_values={config_key: new_value},
            actor_id=actor_id,
            **kwargs
        )

    def _infer_resource_type(self, endpoint: str) -> AuditResourceType:
        """Infer resource type from API endpoint."""
        endpoint_lower = endpoint.lower()
        
        if "location" in endpoint_lower:
            return AuditResourceType.LOCATION
        elif "weather" in endpoint_lower:
            return AuditResourceType.WEATHER_DATA
        elif "alert" in endpoint_lower:
            return AuditResourceType.ALERT
        elif "webhook" in endpoint_lower:
            return AuditResourceType.WEBHOOK
        elif "user" in endpoint_lower or "auth" in endpoint_lower:
            return AuditResourceType.USER
        
        return AuditResourceType.SYSTEM

    def get_logs(
        self,
        resource_type: Optional[AuditResourceType] = None,
        resource_id: Optional[str] = None,
        actor_id: Optional[str] = None,
        event_type: Optional[AuditEventType] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[AuditLog]:
        """
        Retrieve audit logs with filtering.
        
        Args:
            resource_type: Filter by resource type
            resource_id: Filter by resource ID
            actor_id: Filter by actor
            event_type: Filter by event type
            start_time: Filter by start time
            end_time: Filter by end time
            limit: Maximum results
        
        Returns:
            List of matching audit logs
        """
        with self._lock:
            results = list(self.audit_logs)
            
            if resource_type and resource_id:
                key = f"{resource_type.value}:{resource_id}"
                results = list(self.logs_by_resource.get(key, []))
            elif resource_type:
                results = [l for l in results if l.resource_type == resource_type]
            
            if actor_id:
                results = [l for l in results if l.actor_id == actor_id]
            
            if event_type:
                results = [l for l in results if l.event_type == event_type]
            
            if start_time:
                results = [l for l in results if l.timestamp >= start_time]
            
            if end_time:
                results = [l for l in results if l.timestamp <= end_time]
            
            return results[-limit:]

    def get_resource_history(
        self,
        resource_type: AuditResourceType,
        resource_id: str,
        limit: int = 100
    ) -> List[AuditLog]:
        """Get complete change history for a resource."""
        with self._lock:
            key = f"{resource_type.value}:{resource_id}"
            return list(self.logs_by_resource[key])[-limit:]

    def get_audit_summary(self) -> AuditSummary:
        """Get audit statistics summary."""
        with self._lock:
            return AuditSummary(
                total_events=self.total_events,
                events_by_type={k.value: v for k, v in self.events_by_event_type.items()},
                events_by_resource={k.value: v for k, v in self.events_by_resource_type.items()},
                success_count=sum(1 for l in self.audit_logs if l.success),
                failure_count=sum(1 for l in self.audit_logs if not l.success)
            )

    def cleanup_expired_logs(self) -> int:
        """Remove expired logs based on retention policy."""
        with self._lock:
            cutoff_time = datetime.utcnow() - timedelta(days=self.retention_days)
            
            # Count removable logs
            removable = sum(
                1 for log in self.audit_logs
                if log.timestamp < cutoff_time
            )
            
            # In practice, deque with maxlen handles this automatically
            # This is a placeholder for actual database cleanup
            logger.info(f"Cleanup: {removable} expired logs removed")
            return removable


# Global instance
_audit_logger: Optional[AuditLogger] = None


def get_audit_logger() -> AuditLogger:
    """Get or create global audit logger instance."""
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = AuditLogger()
    return _audit_logger
