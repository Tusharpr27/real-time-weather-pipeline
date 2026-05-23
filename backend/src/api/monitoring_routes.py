"""
Monitoring routes - REST API endpoints for metrics, health, errors, and audit logs.
Provides dashboard data, system statistics, and monitoring information.
"""

from fastapi import APIRouter, Query, HTTPException, Request
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from enum import Enum

from src.monitoring.performance_monitor import get_monitor, MetricType, AlertLevel
from src.monitoring.health_checker import get_health_checker, ComponentStatus, ComponentType
from src.monitoring.error_tracker import get_error_tracker, ErrorSeverity, ErrorCategory
from src.monitoring.audit_logger import get_audit_logger, AuditEventType, AuditResourceType

router = APIRouter(prefix="/api/monitoring", tags=["monitoring"])


# ============================================================================
# Performance Metrics Endpoints
# ============================================================================

@router.get("/metrics/overview")
async def get_metrics_overview() -> Dict[str, Any]:
    """Get overall system performance metrics."""
    monitor = get_monitor()
    stats = monitor.get_overall_stats()
    system_stats = monitor.get_system_stats()
    
    return {
        "performance": stats,
        "system": system_stats,
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/metrics/endpoints")
async def get_endpoint_metrics(window_seconds: Optional[int] = Query(None)) -> Dict[str, Any]:
    """Get performance metrics for all tracked endpoints."""
    monitor = get_monitor()
    endpoints = monitor.get_endpoint_metrics()
    
    endpoint_stats = {}
    for endpoint in endpoints:
        endpoint_stats[endpoint] = monitor.get_endpoint_stats(endpoint, window_seconds)
    
    return {
        "endpoints": endpoint_stats,
        "count": len(endpoints),
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/metrics/endpoint/{endpoint_path:path}")
async def get_endpoint_detail(
    endpoint_path: str,
    window_seconds: Optional[int] = Query(None)
) -> Dict[str, Any]:
    """Get detailed metrics for specific endpoint."""
    monitor = get_monitor()
    stats = monitor.get_endpoint_stats(endpoint_path, window_seconds)
    
    return {
        "endpoint": endpoint_path,
        "stats": stats,
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/metrics/alerts")
async def get_performance_alerts(limit: int = Query(50, ge=1, le=500)) -> Dict[str, Any]:
    """Get recent performance alerts."""
    monitor = get_monitor()
    alerts = monitor.get_recent_alerts(limit)
    
    return {
        "alerts": [
            {
                "level": a.level.value,
                "metric_type": a.metric_type.value,
                "message": a.message,
                "value": a.value,
                "threshold": a.threshold,
                "timestamp": a.timestamp.isoformat(),
                "endpoint": a.endpoint
            }
            for a in alerts
        ],
        "count": len(alerts),
        "timestamp": datetime.utcnow().isoformat()
    }


@router.post("/metrics/system-check")
async def trigger_system_check() -> Dict[str, Any]:
    """Manually trigger system resource check."""
    monitor = get_monitor()
    monitor.collect_system_metrics()
    stats = monitor.get_system_stats()
    
    return {
        "system": stats,
        "message": "System check completed",
        "timestamp": datetime.utcnow().isoformat()
    }


# ============================================================================
# Health Check Endpoints
# ============================================================================

@router.get("/health")
async def get_system_health(request: Request) -> Dict[str, Any]:
    """Get overall system health status."""
    health_checker = get_health_checker()
    
    # Prepare components to check
    session = getattr(request.app.state, "db_session", None)
    redis_client = getattr(request.app.state, "redis_client", None)
    webhook_manager = getattr(request.app.state, "webhook_manager", None)
    websocket_handler = getattr(request.app.state, "websocket_handler", None)
    storage_path = getattr(request.app.state, "storage_path", None)
    external_apis = getattr(request.app.state, "external_apis", None)
    
    health_status = await health_checker.check_all(
        session=session,
        redis_client=redis_client,
        webhook_manager=webhook_manager,
        websocket_handler=websocket_handler,
        storage_path=storage_path,
        external_apis=external_apis
    )
    
    return {
        "status": health_status.overall_status.value,
        "checks": [
            {
                "component": c.component_name,
                "type": c.component_type.value,
                "status": c.status.value,
                "response_time_ms": c.response_time_ms,
                "error": c.error_message,
                "info": c.additional_info,
                "timestamp": c.timestamp.isoformat()
            }
            for c in health_status.checks
        ],
        "summary": {
            "healthy": health_status.healthy_components,
            "degraded": health_status.degraded_components,
            "unhealthy": health_status.unhealthy_components
        },
        "response_time_ms": health_status.response_time_ms,
        "timestamp": health_status.timestamp.isoformat()
    }


@router.get("/health/component/{component_type}")
async def get_component_health(component_type: str) -> Dict[str, Any]:
    """Get health status for specific component type."""
    health_checker = get_health_checker()
    
    try:
        comp_type = ComponentType[component_type.upper()]
    except KeyError:
        raise HTTPException(status_code=400, detail=f"Unknown component type: {component_type}")
    
    history = health_checker.get_check_history(comp_type, limit=100)
    
    return {
        "component_type": component_type,
        "history": {
            key: [
                {
                    "status": c.status.value,
                    "response_time_ms": c.response_time_ms,
                    "timestamp": c.timestamp.isoformat(),
                    "error": c.error_message
                }
                for c in checks
            ]
            for key, checks in history.items()
        },
        "timestamp": datetime.utcnow().isoformat()
    }


# ============================================================================
# Error Tracking Endpoints
# ============================================================================

@router.get("/errors/overview")
async def get_error_overview(window_seconds: Optional[int] = Query(3600)) -> Dict[str, Any]:
    """Get error statistics overview."""
    tracker = get_error_tracker()
    stats = tracker.get_error_stats(window_seconds)
    
    return {
        "stats": stats,
        "window_seconds": window_seconds,
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/errors/recent")
async def get_recent_errors(
    limit: int = Query(50, ge=1, le=500),
    severity: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    endpoint: Optional[str] = Query(None)
) -> Dict[str, Any]:
    """Get recent errors with optional filtering."""
    tracker = get_error_tracker()
    
    severity_enum = None
    if severity:
        try:
            severity_enum = ErrorSeverity[severity.upper()]
        except KeyError:
            raise HTTPException(status_code=400, detail=f"Invalid severity: {severity}")
    
    category_enum = None
    if category:
        try:
            category_enum = ErrorCategory[category.upper()]
        except KeyError:
            raise HTTPException(status_code=400, detail=f"Invalid category: {category}")
    
    errors = tracker.get_recent_errors(limit, severity_enum, category_enum, endpoint)
    
    return {
        "errors": [
            {
                "error_id": e.error_id,
                "type": e.error_type,
                "message": e.message,
                "severity": e.severity.value,
                "category": e.category.value,
                "timestamp": e.timestamp.isoformat(),
                "endpoint": e.endpoint,
                "occurred_count": e.occurred_count,
                "correlation_id": e.correlation_id
            }
            for e in errors
        ],
        "count": len(errors),
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/errors/{error_id}")
async def get_error_detail(error_id: str) -> Dict[str, Any]:
    """Get detailed error information."""
    tracker = get_error_tracker()
    error = tracker.get_error_by_id(error_id)
    
    if not error:
        raise HTTPException(status_code=404, detail=f"Error not found: {error_id}")
    
    return {
        "error_id": error.error_id,
        "type": error.error_type,
        "message": error.message,
        "severity": error.severity.value,
        "category": error.category.value,
        "timestamp": error.timestamp.isoformat(),
        "endpoint": error.endpoint,
        "method": error.method,
        "status_code": error.status_code,
        "correlation_id": error.correlation_id,
        "stack_trace": error.stack_trace,
        "exception_chain": error.exception_chain,
        "context": error.context,
        "tags": error.tags
    }


@router.get("/errors/correlation/{correlation_id}")
async def get_correlated_errors(correlation_id: str) -> Dict[str, Any]:
    """Get all errors in a correlation group."""
    tracker = get_error_tracker()
    errors = tracker.get_errors_by_correlation_id(correlation_id)
    
    return {
        "correlation_id": correlation_id,
        "errors": [
            {
                "error_id": e.error_id,
                "type": e.error_type,
                "message": e.message,
                "severity": e.severity.value,
                "timestamp": e.timestamp.isoformat()
            }
            for e in errors
        ],
        "count": len(errors),
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/errors/trends")
async def get_error_trends() -> Dict[str, Any]:
    """Get error trend analysis."""
    tracker = get_error_tracker()
    trends = tracker.get_error_trends()
    
    return {
        "trends": [
            {
                "error_type": t.error_type,
                "category": t.category.value,
                "count": t.count,
                "avg_per_hour": t.avg_occurrences_per_hour,
                "trend": t.trend,
                "severity_distribution": {k: v for k, v in t.severity_distribution.items()},
                "first_seen": t.first_seen.isoformat() if t.first_seen else None,
                "last_seen": t.last_seen.isoformat() if t.last_seen else None
            }
            for t in trends
        ],
        "count": len(trends),
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/errors/critical")
async def get_critical_errors() -> Dict[str, Any]:
    """Get all critical errors."""
    tracker = get_error_tracker()
    errors = tracker.get_critical_errors()
    
    return {
        "critical_errors": [
            {
                "error_id": e.error_id,
                "type": e.error_type,
                "message": e.message,
                "timestamp": e.timestamp.isoformat(),
                "endpoint": e.endpoint,
                "correlation_id": e.correlation_id
            }
            for e in errors
        ],
        "count": len(errors),
        "timestamp": datetime.utcnow().isoformat()
    }


# ============================================================================
# Audit Log Endpoints
# ============================================================================

@router.get("/audit/overview")
async def get_audit_overview() -> Dict[str, Any]:
    """Get audit log summary."""
    audit_logger = get_audit_logger()
    summary = audit_logger.get_audit_summary()
    
    return {
        "total_events": summary.total_events,
        "by_type": summary.events_by_type,
        "by_resource": summary.events_by_resource,
        "success_count": summary.success_count,
        "failure_count": summary.failure_count,
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/audit/logs")
async def get_audit_logs(
    resource_type: Optional[str] = Query(None),
    resource_id: Optional[str] = Query(None),
    actor_id: Optional[str] = Query(None),
    event_type: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    days: int = Query(7, ge=1, le=90)
) -> Dict[str, Any]:
    """Get audit logs with filtering."""
    audit_logger = get_audit_logger()
    
    resource_type_enum = None
    if resource_type:
        try:
            resource_type_enum = AuditResourceType[resource_type.upper()]
        except KeyError:
            raise HTTPException(status_code=400, detail=f"Invalid resource type: {resource_type}")
    
    event_type_enum = None
    if event_type:
        try:
            event_type_enum = AuditEventType[event_type.upper()]
        except KeyError:
            raise HTTPException(status_code=400, detail=f"Invalid event type: {event_type}")
    
    start_time = datetime.utcnow() - timedelta(days=days)
    
    logs = audit_logger.get_logs(
        resource_type=resource_type_enum,
        resource_id=resource_id,
        actor_id=actor_id,
        event_type=event_type_enum,
        start_time=start_time,
        limit=limit
    )
    
    return {
        "logs": [
            {
                "event_id": log.event_id,
                "event_type": log.event_type.value,
                "resource_type": log.resource_type.value,
                "resource_id": log.resource_id,
                "actor_id": log.actor_id,
                "action": log.action,
                "description": log.description,
                "success": log.success,
                "timestamp": log.timestamp.isoformat(),
                "changed_fields": log.changed_fields
            }
            for log in logs
        ],
        "count": len(logs),
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/audit/resource/{resource_type}/{resource_id}")
async def get_resource_history(
    resource_type: str,
    resource_id: str,
    limit: int = Query(100, ge=1, le=1000)
) -> Dict[str, Any]:
    """Get complete audit history for a resource."""
    audit_logger = get_audit_logger()
    
    try:
        resource_type_enum = AuditResourceType[resource_type.upper()]
    except KeyError:
        raise HTTPException(status_code=400, detail=f"Invalid resource type: {resource_type}")
    
    logs = audit_logger.get_resource_history(resource_type_enum, resource_id, limit)
    
    return {
        "resource_type": resource_type,
        "resource_id": resource_id,
        "history": [
            {
                "event_id": log.event_id,
                "event_type": log.event_type.value,
                "action": log.action,
                "actor_id": log.actor_id,
                "timestamp": log.timestamp.isoformat(),
                "old_values": log.old_values,
                "new_values": log.new_values,
                "changed_fields": log.changed_fields
            }
            for log in logs
        ],
        "count": len(logs),
        "timestamp": datetime.utcnow().isoformat()
    }


@router.post("/audit/cleanup")
async def cleanup_expired_audit_logs() -> Dict[str, Any]:
    """Manually trigger audit log cleanup."""
    audit_logger = get_audit_logger()
    removed_count = audit_logger.cleanup_expired_logs()
    
    return {
        "message": "Audit log cleanup completed",
        "removed_count": removed_count,
        "timestamp": datetime.utcnow().isoformat()
    }


# ============================================================================
# Combined Dashboard Endpoint
# ============================================================================

@router.get("/dashboard")
async def get_dashboard_data(request: Request) -> Dict[str, Any]:
    """Get comprehensive dashboard data with all monitoring info."""
    monitor = get_monitor()
    health_checker = get_health_checker()
    error_tracker = get_error_tracker()
    audit_logger = get_audit_logger()
    
    # Get health status
    session = getattr(request.app.state, "db_session", None)
    redis_client = getattr(request.app.state, "redis_client", None)
    webhook_manager = getattr(request.app.state, "webhook_manager", None)
    websocket_handler = getattr(request.app.state, "websocket_handler", None)
    
    health_status = await health_checker.check_all(
        session=session,
        redis_client=redis_client,
        webhook_manager=webhook_manager,
        websocket_handler=websocket_handler
    )
    
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "performance": {
            "overall": monitor.get_overall_stats(),
            "system": monitor.get_system_stats(),
            "recent_alerts": [
                {
                    "level": a.level.value,
                    "metric": a.metric_type.value,
                    "value": a.value,
                    "timestamp": a.timestamp.isoformat()
                }
                for a in monitor.get_recent_alerts(5)
            ]
        },
        "health": {
            "status": health_status.overall_status.value,
            "summary": {
                "healthy": health_status.healthy_components,
                "degraded": health_status.degraded_components,
                "unhealthy": health_status.unhealthy_components
            }
        },
        "errors": {
            "overview": error_tracker.get_error_stats(3600),
            "critical": len(error_tracker.get_critical_errors())
        },
        "audit": {
            "summary": {
                "total_events": audit_logger.total_events,
                "success_count": sum(1 for l in audit_logger.audit_logs if l.success),
                "failure_count": sum(1 for l in audit_logger.audit_logs if not l.success)
            }
        }
    }
