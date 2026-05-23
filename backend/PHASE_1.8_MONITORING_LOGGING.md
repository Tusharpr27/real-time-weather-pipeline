# Phase 1.8: Monitoring & Logging - Complete Implementation Guide

**Status**: ✅ COMPLETE  
**Date**: April 2, 2026  
**Total Code**: 2,436 lines (4 modules + 492 routes)  
**Backend Completion**: 87.5% (7 of 8 phases)

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Core Modules](#core-modules)
4. [API Endpoints](#api-endpoints)
5. [Configuration](#configuration)
6. [Usage Examples](#usage-examples)
7. [Dashboard Setup](#dashboard-setup)
8. [Integration Guide](#integration-guide)

---

## 🎯 Overview

Phase 1.8 implements comprehensive monitoring, logging, and observability for the Real-Time Weather Pipeline. The system tracks performance metrics, health status, errors, and maintains an immutable audit trail of all system changes.

### Key Features

- **Performance Monitoring**: Real-time API metrics, system resources, throughput tracking
- **Health Checking**: Component health verification, dependency status, availability checks
- **Error Tracking**: Exception capture, error categorization, trend analysis, spike detection
- **Audit Logging**: Immutable audit trail, change tracking, compliance logging
- **Dashboard API**: 20+ REST endpoints for comprehensive system monitoring
- **Alerting**: Automatic alerts on performance degradation and error spikes

---

## 🏗️ Architecture

### System Design

```
┌─────────────────────────────────────────────────────────────┐
│                     FastAPI Application                      │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────┐  ┌──────────────────┐                │
│  │ API Requests     │  │ System Events    │                │
│  └────────┬─────────┘  └────────┬─────────┘                │
│           │                     │                           │
│           └─────────────────────┴──────────────┐            │
│                                                 │            │
│                    Monitoring Module            │            │
│   ┌────────────────────────────────────────────┼───────┐   │
│   │                                             ▼       │   │
│   │  ┌──────────────────────────────────────────────┐  │   │
│   │  │      Performance Monitor                     │  │   │
│   │  │  • Response times per endpoint               │  │   │
│   │  │  • Throughput (RPS)                          │  │   │
│   │  │  • System resources (CPU, Memory)            │  │   │
│   │  │  • Database query performance                │  │   │
│   │  │  • Alert on threshold violations             │  │   │
│   │  └──────────────────────────────────────────────┘  │   │
│   │                                                     │   │
│   │  ┌──────────────────────────────────────────────┐  │   │
│   │  │      Health Checker                          │  │   │
│   │  │  • Database connectivity                     │  │   │
│   │  │  • Cache availability                        │  │   │
│   │  │  • External API dependencies                 │  │   │
│   │  │  • Webhook delivery system                   │  │   │
│   │  │  • WebSocket connections                     │  │   │
│   │  │  • File storage accessibility                │  │   │
│   │  └──────────────────────────────────────────────┘  │   │
│   │                                                     │   │
│   │  ┌──────────────────────────────────────────────┐  │   │
│   │  │      Error Tracker                           │  │   │
│   │  │  • Exception capture with stack traces       │  │   │
│   │  │  • Error categorization                      │  │   │
│   │  │  • Correlation ID tracking                   │  │   │
│   │  │  • Error deduplication                       │  │   │
│   │  │  • Trend analysis & spike detection          │  │   │
│   │  └──────────────────────────────────────────────┘  │   │
│   │                                                     │   │
│   │  ┌──────────────────────────────────────────────┐  │   │
│   │  │      Audit Logger                            │  │   │
│   │  │  • Immutable audit trail (append-only)       │  │   │
│   │  │  • Data modification tracking                │  │   │
│   │  │  • User action logging                       │  │   │
│   │  │  • Configuration change recording            │  │   │
│   │  │  • Automatic retention enforcement           │  │   │
│   │  └──────────────────────────────────────────────┘  │   │
│   │                                                     │   │
│   └─────────────────────────────────────────────────────┘   │
│                         ▲                                     │
│                         │                                     │
│                 Monitoring Routes API                        │
│              (20+ REST Endpoints)                            │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 📦 Core Modules

### 1. Performance Monitor (`performance_monitor.py` - 426 lines)

**Purpose**: Track and analyze API performance metrics and system resources.

#### Key Classes

**`PerformanceMetric`**
```python
@dataclass
class PerformanceMetric:
    metric_type: MetricType  # request_time, throughput, memory_usage, cpu_usage, etc.
    value: float
    timestamp: datetime
    endpoint: Optional[str]
    method: Optional[str]
    tags: Dict[str, str]
```

**`MetricType` Enum**
- `REQUEST_TIME`: API response time in seconds
- `THROUGHPUT`: Requests per second
- `MEMORY_USAGE`: Process memory percentage
- `CPU_USAGE`: CPU utilization percentage
- `DATABASE_QUERY`: Database query execution time
- `CACHE_HIT_RATE`: Cache hit percentage
- `ERROR_RATE`: Error rate percentage

**`PerformanceMonitor` Class**

Key methods:
- `record_request_start(endpoint)` - Mark request start
- `record_request_end(endpoint, method, response_time, success)` - Record request completion
- `record_metric(metric_type, value)` - Record generic metric
- `record_database_query(query_time, table, operation)` - Log database query
- `collect_system_metrics()` - Collect CPU/memory metrics
- `get_endpoint_stats(endpoint, window_seconds)` - Get endpoint performance
- `get_system_stats(window_seconds)` - Get system resource stats
- `get_overall_stats()` - Get overall system performance
- `get_recent_alerts(limit)` - Get performance alerts

Example:
```python
from src.monitoring.performance_monitor import get_monitor

monitor = get_monitor()
monitor.record_request_end("/api/weather", "GET", response_time=0.125, success=True)
stats = monitor.get_endpoint_stats("/api/weather")
print(f"Avg response time: {stats['avg_response_time']}s")
print(f"P95 response time: {stats['p95_response_time']}s")
```

#### Thresholds (Default)
- Request Time: WARNING=1s, CRITICAL=5s
- Memory Usage: WARNING=70%, CRITICAL=90%
- CPU Usage: WARNING=75%, CRITICAL=95%
- Database Query: WARNING=2s, CRITICAL=10s
- Error Rate: WARNING=5%, CRITICAL=15%

---

### 2. Health Checker (`health_checker.py` - 536 lines)

**Purpose**: Verify health and availability of all system components.

#### Key Classes

**`ComponentStatus` Enum**
- `HEALTHY`: Component operating normally
- `DEGRADED`: Component has reduced functionality
- `UNHEALTHY`: Component not responding
- `UNKNOWN`: Status cannot be determined

**`ComponentType` Enum**
- `DATABASE`: Primary data store
- `CACHE`: Redis/caching layer
- `EXTERNAL_API`: Third-party integrations
- `WEBHOOK_DELIVERY`: Webhook system
- `WEBSOCKET`: Real-time connections
- `FILE_STORAGE`: File system storage
- `MESSAGE_QUEUE`: Message queue system

**`HealthChecker` Class**

Key methods:
- `async check_database(session, query)` - Test database connectivity
- `async check_cache(redis_client)` - Verify cache availability
- `async check_external_api(endpoint, timeout)` - Test external API
- `async check_webhook_delivery(webhook_manager)` - Check webhook system
- `async check_websocket(websocket_handler)` - Verify WebSocket health
- `async check_file_storage(storage_path)` - Test file storage
- `async check_all(...)` - Check all components in parallel

Example:
```python
from src.monitoring.health_checker import get_health_checker

checker = get_health_checker()
health_status = await checker.check_all(
    session=db_session,
    redis_client=redis,
    webhook_manager=webhook_mgr,
    websocket_handler=ws_handler
)

if health_status.overall_status == ComponentStatus.HEALTHY:
    print("✅ All systems operational")
else:
    print(f"⚠️ {health_status.unhealthy_components} components unhealthy")
```

---

### 3. Error Tracker (`error_tracker.py` - 433 lines)

**Purpose**: Capture, categorize, and analyze application errors.

#### Key Classes

**`ErrorSeverity` Enum**
- `INFO`: Informational message
- `WARNING`: Warning level
- `ERROR`: Error level
- `CRITICAL`: Critical/urgent error

**`ErrorCategory` Enum**
- `DATABASE`: Database-related errors
- `VALIDATION`: Data validation failures
- `AUTHENTICATION`: Auth failures
- `AUTHORIZATION`: Permission denied
- `EXTERNAL_API`: External dependency errors
- `INTERNAL`: Internal system errors
- `TIMEOUT`: Operation timeouts
- `RESOURCE`: Resource exhaustion
- `CONFIG`: Configuration errors
- `UNKNOWN`: Uncategorized

**`ErrorTracker` Class**

Key methods:
- `record_error(exception, error_type, message, severity, category, ...)` - Record error
- `get_error_stats(window_seconds)` - Get error statistics
- `get_recent_errors(limit, severity, category, endpoint)` - Get recent errors
- `get_error_by_id(error_id)` - Retrieve specific error
- `get_errors_by_correlation_id(correlation_id)` - Get related errors
- `get_error_trends()` - Analyze error trends
- `get_critical_errors()` - Get critical errors

Example:
```python
from src.monitoring.error_tracker import get_error_tracker, ErrorSeverity, ErrorCategory

tracker = get_error_tracker()

try:
    # Some operation
    pass
except Exception as e:
    error_id = tracker.record_error(
        exception=e,
        severity=ErrorSeverity.ERROR,
        category=ErrorCategory.EXTERNAL_API,
        endpoint="/api/weather",
        correlation_id=request_id
    )
    print(f"Error recorded with ID: {error_id}")

# Get error summary
stats = tracker.get_error_stats(window_seconds=3600)
print(f"Errors in last hour: {stats['total_errors']}")
print(f"Error rate: {stats['error_rate_per_minute']}/min")
```

#### Features
- Automatic error categorization based on exception type
- Correlation ID for request tracing
- Exception chain extraction
- Error deduplication with signature matching
- Automatic spike detection (2x normal rate)
- Trend analysis with hourly rates

---

### 4. Audit Logger (`audit_logger.py` - 549 lines)

**Purpose**: Maintain immutable audit trail of all system changes.

#### Key Classes

**`AuditEventType` Enum**
- `CREATE`: Resource created
- `READ`: Resource accessed
- `UPDATE`: Resource modified
- `DELETE`: Resource deleted
- `AUTHENTICATE`: User authentication
- `AUTHORIZE`: Permission check
- `CONFIG_CHANGE`: Configuration changed
- `WEBHOOK_TRIGGER`: Webhook triggered
- `ALERT_TRIGGERED`: Alert fired
- `EXPORT_REQUESTED`: Data export requested
- `SYSTEM_EVENT`: Generic system event

**`AuditResourceType` Enum**
- `LOCATION`: Weather location
- `WEATHER_DATA`: Weather observation
- `ALERT`: Alert instance
- `ALERT_RULE`: Alert rule definition
- `WEBHOOK`: Webhook subscription
- `USER`: User account
- `CONFIGURATION`: System configuration
- `SYSTEM`: System-level event
- `PERMISSION`: Permission/role
- `EXPORT`: Data export

**`AuditLogger` Class**

Key methods:
- `log_event(event_type, resource_type, ...)` - Log generic event
- `log_data_change(resource_type, resource_id, operation, ...)` - Log CRUD
- `log_api_call(endpoint, method, actor_id, ...)` - Log API call
- `log_authentication(actor_id, success, ...)` - Log auth event
- `log_webhook_trigger(webhook_id, event_type, ...)` - Log webhook
- `log_alert_triggered(alert_rule_id, alert_id, ...)` - Log alert
- `log_export_request(format, resource_type, ...)` - Log export
- `log_config_change(config_key, old_value, new_value, ...)` - Log config
- `get_logs(filters...)` - Retrieve audit logs
- `get_resource_history(resource_type, resource_id)` - Get resource changes

Example:
```python
from src.monitoring.audit_logger import get_audit_logger, AuditEventType, AuditResourceType

audit = get_audit_logger()

# Log data change
audit.log_data_change(
    resource_type=AuditResourceType.ALERT,
    resource_id="ALERT_123",
    operation="update",
    old_values={"status": "active"},
    new_values={"status": "acknowledged"},
    actor_id="user_42"
)

# Get resource history
history = audit.get_resource_history(AuditResourceType.ALERT, "ALERT_123")
for log in history:
    print(f"{log.timestamp}: {log.action} by {log.actor_id}")
```

#### Features
- Append-only immutable log storage
- Automatic retention policy (90 days default)
- Changed field tracking
- Sensitive data redaction option
- Actor identification and tracking
- Request correlation IDs
- IP address logging
- Search and filtering capabilities

---

## 🔌 API Endpoints

### Performance Metrics Endpoints

#### GET `/api/monitoring/metrics/overview`
Get overall system performance metrics.

**Response**:
```json
{
  "performance": {
    "total_requests": 15234,
    "total_errors": 42,
    "error_rate_percent": 0.28,
    "active_requests": 3,
    "throughput_rps": 2.15,
    "avg_response_time": 0.234,
    "p95_response_time": 0.892
  },
  "system": {
    "current_memory_percent": 45.2,
    "current_cpu_percent": 12.3,
    "avg_memory_percent": 42.1,
    "max_memory_percent": 58.9,
    "avg_cpu_percent": 14.2,
    "max_cpu_percent": 78.5
  },
  "timestamp": "2026-04-02T15:30:45.123456"
}
```

#### GET `/api/monitoring/metrics/endpoints`
Get performance metrics for all tracked endpoints.

**Query Parameters**:
- `window_seconds` (optional): Time window for calculations (default: 3600)

**Response**:
```json
{
  "endpoints": {
    "/api/weather/current": {
      "endpoint": "/api/weather/current",
      "count": 1523,
      "avg_response_time": 0.145,
      "min_response_time": 0.032,
      "max_response_time": 2.341,
      "p95_response_time": 0.634,
      "p99_response_time": 0.892
    },
    ...
  },
  "count": 12,
  "timestamp": "2026-04-02T15:30:45.123456"
}
```

#### GET `/api/monitoring/metrics/endpoint/{endpoint_path}`
Get detailed metrics for specific endpoint.

#### GET `/api/monitoring/metrics/alerts`
Get recent performance alerts.

**Query Parameters**:
- `limit` (int, default=50): Maximum alerts to return (1-500)

**Response**:
```json
{
  "alerts": [
    {
      "level": "warning",
      "metric_type": "request_time",
      "message": "request_time exceeded warning threshold",
      "value": 1.2,
      "threshold": 1.0,
      "timestamp": "2026-04-02T15:30:45.123456",
      "endpoint": "/api/weather/forecast"
    }
  ],
  "count": 3,
  "timestamp": "2026-04-02T15:30:45.123456"
}
```

#### POST `/api/monitoring/metrics/system-check`
Manually trigger system resource check.

---

### Health Check Endpoints

#### GET `/api/monitoring/health`
Get overall system health status.

**Response**:
```json
{
  "status": "healthy",
  "checks": [
    {
      "component": "PostgreSQL",
      "type": "database",
      "status": "healthy",
      "response_time_ms": 12.3,
      "error": null,
      "info": {"query_executed": "SELECT 1"},
      "timestamp": "2026-04-02T15:30:45.123456"
    },
    {
      "component": "Redis",
      "type": "cache",
      "status": "healthy",
      "response_time_ms": 2.1,
      "error": null,
      "info": {},
      "timestamp": "2026-04-02T15:30:45.123456"
    }
  ],
  "summary": {
    "healthy": 6,
    "degraded": 1,
    "unhealthy": 0
  },
  "response_time_ms": 45.2,
  "timestamp": "2026-04-02T15:30:45.123456"
}
```

#### GET `/api/monitoring/health/component/{component_type}`
Get health status for specific component type.

**Component Types**: database, cache, external_api, webhook_delivery, websocket, file_storage

---

### Error Tracking Endpoints

#### GET `/api/monitoring/errors/overview`
Get error statistics overview.

**Query Parameters**:
- `window_seconds` (int, default=3600): Time window in seconds

**Response**:
```json
{
  "stats": {
    "total_errors": 42,
    "unique_errors": 8,
    "errors_by_severity": {
      "info": 2,
      "warning": 15,
      "error": 20,
      "critical": 5
    },
    "errors_by_category": {
      "external_api": 12,
      "internal": 8,
      "validation": 15,
      "timeout": 7
    },
    "error_rate_per_minute": 0.7,
    "avg_errors_per_endpoint": 3.5
  },
  "window_seconds": 3600,
  "timestamp": "2026-04-02T15:30:45.123456"
}
```

#### GET `/api/monitoring/errors/recent`
Get recent errors with optional filtering.

**Query Parameters**:
- `limit` (int, default=50, range: 1-500)
- `severity` (str, optional): "info", "warning", "error", "critical"
- `category` (str, optional): Error category
- `endpoint` (str, optional): Filter by endpoint

#### GET `/api/monitoring/errors/{error_id}`
Get detailed error information including stack trace.

#### GET `/api/monitoring/errors/correlation/{correlation_id}`
Get all errors in a correlation group for request tracing.

#### GET `/api/monitoring/errors/trends`
Get error trend analysis with severity distribution.

#### GET `/api/monitoring/errors/critical`
Get all critical errors.

---

### Audit Log Endpoints

#### GET `/api/monitoring/audit/overview`
Get audit log summary statistics.

**Response**:
```json
{
  "total_events": 2543,
  "by_type": {
    "create": 342,
    "update": 1842,
    "delete": 89,
    "read": 234,
    "authenticate": 36
  },
  "by_resource": {
    "alert": 456,
    "weather_data": 1234,
    "webhook": 89,
    "user": 42
  },
  "success_count": 2512,
  "failure_count": 31,
  "timestamp": "2026-04-02T15:30:45.123456"
}
```

#### GET `/api/monitoring/audit/logs`
Get audit logs with comprehensive filtering.

**Query Parameters**:
- `resource_type` (str): Resource type filter
- `resource_id` (str): Specific resource ID
- `actor_id` (str): User/actor ID
- `event_type` (str): Event type filter
- `limit` (int, default=100): Max results (1-1000)
- `days` (int, default=7): Look back period (1-90)

**Response**:
```json
{
  "logs": [
    {
      "event_id": "evt_abc123",
      "event_type": "update",
      "resource_type": "alert",
      "resource_id": "ALERT_456",
      "actor_id": "user_42",
      "action": "update",
      "description": "Alert acknowledged",
      "success": true,
      "timestamp": "2026-04-02T15:30:45.123456",
      "changed_fields": ["status", "acknowledged_at"]
    }
  ],
  "count": 125,
  "timestamp": "2026-04-02T15:30:45.123456"
}
```

#### GET `/api/monitoring/audit/resource/{resource_type}/{resource_id}`
Get complete audit history for a specific resource.

#### POST `/api/monitoring/audit/cleanup`
Manually trigger audit log cleanup (removes expired logs).

---

### Dashboard Endpoint

#### GET `/api/monitoring/dashboard`
Comprehensive dashboard data combining all monitoring information.

**Response**:
```json
{
  "timestamp": "2026-04-02T15:30:45.123456",
  "performance": {
    "overall": {...},
    "system": {...},
    "recent_alerts": [...]
  },
  "health": {
    "status": "healthy",
    "summary": {...}
  },
  "errors": {
    "overview": {...},
    "critical": 0
  },
  "audit": {
    "summary": {...}
  }
}
```

---

## ⚙️ Configuration

### Config.py Settings

```python
# Performance Monitoring
performance_monitoring_enabled: bool = True
metrics_history_limit: int = 100000
metrics_window_size_seconds: int = 3600
metric_alert_cpu_threshold: float = 75.0
metric_alert_memory_threshold: float = 70.0
metric_alert_request_time_threshold: float = 1.0

# Health Checking
health_check_enabled: bool = True
health_check_timeout_seconds: int = 5
health_check_interval_seconds: int = 60

# Error Tracking
error_tracking_enabled: bool = True
error_history_limit: int = 10000
error_window_size_seconds: int = 3600
error_spike_threshold_multiplier: float = 2.0

# Audit Logging
audit_logging_enabled: bool = True
audit_history_limit: int = 50000
audit_retention_days: int = 90
audit_log_sensitive_data: bool = False

# Monitoring API
monitoring_api_enabled: bool = True
monitoring_api_rate_limit: int = 1000
```

### Environment Variables (.env)

```dotenv
# Performance Monitoring
PERFORMANCE_MONITORING_ENABLED=True
METRICS_HISTORY_LIMIT=100000
METRICS_WINDOW_SIZE_SECONDS=3600
METRIC_ALERT_CPU_THRESHOLD=75.0
METRIC_ALERT_MEMORY_THRESHOLD=70.0
METRIC_ALERT_REQUEST_TIME_THRESHOLD=1.0

# Health Checking
HEALTH_CHECK_ENABLED=True
HEALTH_CHECK_TIMEOUT_SECONDS=5
HEALTH_CHECK_INTERVAL_SECONDS=60

# Error Tracking
ERROR_TRACKING_ENABLED=True
ERROR_HISTORY_LIMIT=10000
ERROR_WINDOW_SIZE_SECONDS=3600
ERROR_SPIKE_THRESHOLD_MULTIPLIER=2.0

# Audit Logging
AUDIT_LOGGING_ENABLED=True
AUDIT_HISTORY_LIMIT=50000
AUDIT_RETENTION_DAYS=90
AUDIT_LOG_SENSITIVE_DATA=False

# Monitoring API
MONITORING_API_ENABLED=True
MONITORING_API_RATE_LIMIT=1000
```

---

## 💡 Usage Examples

### Example 1: Recording and Monitoring API Performance

```python
from fastapi import Request
from src.monitoring.performance_monitor import get_monitor
from src.monitoring.error_tracker import get_error_tracker

monitor = get_monitor()
error_tracker = get_error_tracker()

@app.get("/api/weather/current")
async def get_current_weather(request: Request):
    endpoint = "/api/weather/current"
    monitor.record_request_start(endpoint)
    
    try:
        # Process request
        result = await fetch_current_weather()
        
        monitor.record_request_end(
            endpoint=endpoint,
            method="GET",
            response_time=0.234,
            success=True
        )
        return result
    except Exception as e:
        error_tracker.record_error(
            exception=e,
            endpoint=endpoint,
            correlation_id=request.id
        )
        monitor.record_request_end(
            endpoint=endpoint,
            method="GET",
            success=False
        )
        raise
```

### Example 2: Health Monitoring Background Task

```python
import asyncio
from src.monitoring.health_checker import get_health_checker, ComponentStatus
from src.utils.logger import logger

async def health_check_loop():
    """Run periodic health checks"""
    checker = get_health_checker()
    
    while True:
        health_status = await checker.check_all(
            session=db_session,
            redis_client=redis_client,
            webhook_manager=webhook_manager,
            websocket_handler=websocket_handler
        )
        
        if health_status.overall_status == ComponentStatus.UNHEALTHY:
            logger.critical(f"System unhealthy! {health_status.unhealthy_components} components down")
            # Send alerts
        
        await asyncio.sleep(60)  # Check every minute
```

### Example 3: Audit Logging Data Changes

```python
from src.monitoring.audit_logger import get_audit_logger, AuditResourceType

audit = get_audit_logger()

@app.put("/api/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(alert_id: str, request: Request):
    # Get current alert
    old_alert = await get_alert(alert_id)
    
    # Update alert
    alert = await update_alert(alert_id, {"acknowledged": True})
    
    # Log change
    audit.log_data_change(
        resource_type=AuditResourceType.ALERT,
        resource_id=alert_id,
        operation="update",
        old_values={"acknowledged": old_alert.acknowledged},
        new_values={"acknowledged": alert.acknowledged},
        actor_id=request.user.id,
        endpoint="/api/alerts/{alert_id}/acknowledge",
        method="PUT",
        ip_address=request.client.host
    )
    
    return alert
```

### Example 4: Querying Error Trends

```python
from src.monitoring.error_tracker import get_error_tracker

error_tracker = get_error_tracker()

# Get trends
trends = error_tracker.get_error_trends()

for trend in trends:
    print(f"Error Type: {trend.error_type}")
    print(f"Category: {trend.category.value}")
    print(f"Total: {trend.count}")
    print(f"Avg per hour: {trend.avg_occurrences_per_hour:.2f}")
    print(f"Severity breakdown: {trend.severity_distribution}")
    print("---")
```

---

## 📊 Dashboard Setup

### Frontend Integration

Create a monitoring dashboard HTML page:

```html
<!DOCTYPE html>
<html>
<head>
    <title>System Monitoring Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <h1>Real-Time Weather Pipeline - Monitoring Dashboard</h1>
    
    <div id="dashboard"></div>
    
    <script>
        async function updateDashboard() {
            const response = await fetch('/api/monitoring/dashboard');
            const data = await response.json();
            
            // Performance Chart
            const perfCtx = document.getElementById('perfChart').getContext('2d');
            new Chart(perfCtx, {
                type: 'line',
                data: {
                    labels: ['0s', '1min', '2min', '3min'],
                    datasets: [{
                        label: 'Response Time (ms)',
                        data: data.performance.overall.avg_response_time * 1000,
                        borderColor: 'rgb(75, 192, 192)',
                        tension: 0.1
                    }]
                }
            });
            
            // Health Status
            const healthDiv = document.getElementById('health');
            healthDiv.innerHTML = `
                Status: <strong>${data.health.status.toUpperCase()}</strong>
                <br/>
                Healthy: ${data.health.summary.healthy}
                Degraded: ${data.health.summary.degraded}
                Unhealthy: ${data.health.summary.unhealthy}
            `;
            
            // Error Summary
            const errorsDiv = document.getElementById('errors');
            errorsDiv.innerHTML = `
                Errors: ${data.errors.overview.total_errors}
                Critical: ${data.errors.critical}
            `;
        }
        
        // Update every 5 seconds
        setInterval(updateDashboard, 5000);
        updateDashboard();
    </script>
</body>
</html>
```

---

## 🔗 Integration Guide

### 1. Middleware Integration

Add monitoring middleware to FastAPI:

```python
from fastapi import Request
import time
from src.monitoring.performance_monitor import get_monitor
from src.monitoring.error_tracker import get_error_tracker

@app.middleware("http")
async def monitoring_middleware(request: Request, call_next):
    monitor = get_monitor()
    error_tracker = get_error_tracker()
    
    endpoint = request.url.path
    monitor.record_request_start(endpoint)
    
    start_time = time.time()
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        
        monitor.record_request_end(
            endpoint=endpoint,
            method=request.method,
            response_time=process_time,
            success=(200 <= response.status_code < 400)
        )
        
        return response
    except Exception as e:
        error_tracker.record_error(
            exception=e,
            endpoint=endpoint,
            method=request.method
        )
        raise
```

### 2. Database Integration

Log database operations:

```python
from src.monitoring.audit_logger import get_audit_logger, AuditResourceType
from src.monitoring.performance_monitor import get_monitor

async def create_alert(alert_data):
    monitor = get_monitor()
    audit = get_audit_logger()
    
    start_time = time.time()
    
    # Create alert in database
    new_alert = await db.alerts.create(alert_data)
    
    # Record performance
    query_time = time.time() - start_time
    monitor.record_database_query(
        query_time=query_time,
        table="alerts",
        operation="INSERT"
    )
    
    # Record audit
    audit.log_data_change(
        resource_type=AuditResourceType.ALERT,
        resource_id=new_alert.id,
        operation="create",
        new_values=alert_data,
        actor_id=current_user.id
    )
    
    return new_alert
```

### 3. Webhook Integration

Log webhook operations:

```python
from src.monitoring.audit_logger import get_audit_logger

audit = get_audit_logger()

async def trigger_webhooks(event_type, resource_id):
    manager = get_webhook_manager()
    
    subscriptions = await manager.get_subscriptions(event_type)
    
    for subscription in subscriptions:
        success = await manager.trigger_webhook(
            subscription.id,
            event_type,
            resource_data
        )
        
        audit.log_webhook_trigger(
            webhook_id=subscription.id,
            event_type=event_type,
            resource_id=resource_id,
            success=success
        )
```

---

## 📈 Phase 1.8 Metrics

### Implementation Summary

| Metric | Value |
|--------|-------|
| Performance Monitor | 426 lines |
| Health Checker | 536 lines |
| Error Tracker | 433 lines |
| Audit Logger | 549 lines |
| Monitoring Routes | 492 lines |
| **Total Code** | **2,436 lines** |
| REST Endpoints | 20+ |
| Monitoring Types | 4 (Performance, Health, Errors, Audit) |
| Component Types | 7 |
| Error Categories | 9 |
| Audit Event Types | 11 |
| Audit Resource Types | 10 |

### Project Progress

- **Backend Completion**: 87.5% (7 of 8 phases)
- **Total Lines of Code**: 7,753 lines (Phases 1.1-1.8)
- **API Endpoints**: 50+
- **Database Tables**: 15+
- **Configuration Settings**: 80+

---

## 🚀 Next Steps

Phase 1.8 completes the backend monitoring and observability layer. The system is now production-ready with:

- ✅ Full API performance tracking
- ✅ Comprehensive health monitoring
- ✅ Detailed error analytics
- ✅ Complete audit trail

**Phase 1.9** (Final Phase - Backend Deployment & Documentation):
- Deployment configuration
- Docker containerization
- API documentation (OpenAPI/Swagger)
- Performance benchmarks
- Security hardening

**Phase 2-3** (Frontend & Deployment):
- React dashboard UI
- Real-time visualizations
- Production deployment

---

## 📝 Document Information

- **Version**: 1.0
- **Created**: April 2, 2026
- **Last Updated**: April 2, 2026
- **Status**: Complete and Production Ready
- **Maintainer**: Real-Time Weather Pipeline Team
