# Phase 1.7: API Enhancement - Implementation Guide

## Overview
Phase 1.7 adds advanced API capabilities including webhook support, data export, real-time WebSocket updates, and advanced filtering.

**Status**: ✅ COMPLETE  
**Total Lines**: 2,100+ lines across 7 modules  
**New Endpoints**: 15+ new REST endpoints  
**WebSocket Support**: Real-time event streaming  
**Export Formats**: JSON, CSV, JSONL  
**Database Tables**: Uses existing models  

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│              API Enhancement Layer (Phase 1.7)              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────┐  ┌──────────────────┐                │
│  │ Webhook Manager  │  │ Advanced Filter  │                │
│  │ - Subscribe      │  │ - Build queries  │                │
│  │ - Trigger        │  │ - Complex conds  │                │
│  │ - Retry          │  │ - Parse filters  │                │
│  └──────────────────┘  └──────────────────┘                │
│                                                              │
│  ┌──────────────────┐  ┌──────────────────┐                │
│  │ Data Exporter    │  │ WebSocket Handler│                │
│  │ - CSV export     │  │ - Connections    │                │
│  │ - JSON export    │  │ - Subscriptions  │                │
│  │ - Streaming      │  │ - Broadcasting   │                │
│  └──────────────────┘  └──────────────────┘                │
│                                                              │
│  ┌──────────────────────────────────────┐                  │
│  │ API Routes (15+ endpoints)           │                  │
│  │ - Webhooks (7 endpoints)             │                  │
│  │ - Export (4 endpoints)               │                  │
│  │ - Real-time WebSocket (2 endpoints)  │                  │
│  │ - Health checks (2 endpoints)        │                  │
│  └──────────────────────────────────────┘                  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Module Details

### 1. Webhook Manager (`webhook_manager.py`) - 420 lines
**Purpose**: Manage webhook subscriptions and delivery

**Key Classes**:
- `WebhookEvent`: Enum for event types
- `WebhookStatus`: Subscription status
- `WebhookSubscription`: Webhook definition
- `WebhookManager`: Main orchestrator

**Features**:
- ✅ 8 webhook event types (alert, weather, anomaly, metrics, archive)
- ✅ Subscription management with status tracking
- ✅ HMAC-SHA256 signature generation
- ✅ Automatic retry with exponential backoff
- ✅ Max 5 failures before suspension
- ✅ Async HTTP delivery with 10-second timeout
- ✅ Comprehensive statistics and monitoring

**Event Types**:
```
alert.created - New alert triggered
alert.acknowledged - Alert acknowledged
alert.resolved - Alert resolved
alert.escalated - Alert escalation occurred
weather.collected - New weather data
anomaly.detected - Anomaly found
metric.calculated - Metric computed
data.archived - Data archived
```

**Key Methods**:
```python
register_webhook(event, url, secret)     # Subscribe to event
unregister_webhook(subscription_id)      # Unsubscribe
trigger_webhook(event, data)             # Fire webhooks
retry_failed_webhooks()                  # Retry failed deliveries
get_statistics()                         # Get metrics
```

---

### 2. Advanced Filter (`advanced_filter.py`) - 350 lines
**Purpose**: Complex query building with multiple conditions

**Key Classes**:
- `FilterOperator`: 13 comparison operators
- `LogicalOperator`: AND, OR, NOT
- `FilterCondition`: Single condition
- `FilterGroup`: Grouped conditions
- `AdvancedFilter`: Query builder
- `FilterParser`: Parse filter definitions

**Supported Operators**:
```
eq - Equal
neq - Not equal
gt, gte - Greater than / equal
lt, lte - Less than / equal
in, nin - In / not in list
contains - String contains
startswith, endswith - String matching
between - Range check
exists - Field existence
```

**Features**:
- ✅ Nested condition groups
- ✅ Complex boolean logic (AND/OR/NOT)
- ✅ SQLAlchemy query integration
- ✅ Filter serialization/deserialization
- ✅ Field type validation
- ✅ Date range support
- ✅ JSON/dict interchange format

**Example Usage**:
```python
filter_obj = AdvancedFilter()
filter_obj.add_condition("severity", FilterOperator.EQ, "HIGH")
filter_obj.add_condition("created_at", FilterOperator.BETWEEN, 
                         ["2026-04-01", "2026-04-02"])

query = filter_obj.build_query(base_query, Alert)
```

---

### 3. Data Exporter (`data_exporter.py`) - 380 lines
**Purpose**: Export data in multiple formats

**Key Classes**:
- `ExportFormat`: CSV, JSON, JSONL enums
- `DataExporter`: Main exporter

**Features**:
- ✅ Export alerts to CSV/JSON/JSONL
- ✅ Export weather data with date ranges
- ✅ Export metrics by type (hourly/daily/weekly)
- ✅ Field selection and filtering
- ✅ Pagination support (limit up to 50,000)
- ✅ Location-based filtering
- ✅ Date range filtering
- ✅ Streaming for large datasets

**Export Formats**:
- **JSON**: Array of objects, pretty-printed
- **JSONL**: One JSON object per line (streaming-friendly)
- **CSV**: Comma-separated with headers

**Key Methods**:
```python
export_alerts(format, filters, fields, limit)
export_weather_data(format, location_id, date_range, fields, limit)
export_metrics(format, metric_type, location_id, date_range, fields, limit)
```

---

### 4. WebSocket Handler (`websocket_handler.py`) - 310 lines
**Purpose**: Real-time event streaming to clients

**Key Classes**:
- `RealtimeEvent`: 8 event types for streaming
- `RealtimeSubscription`: Client subscription model
- `WebSocketHandler`: Connection and message manager

**Features**:
- ✅ Connection management per client
- ✅ Event-based subscriptions
- ✅ Location-based filtering
- ✅ Broadcast to multiple clients
- ✅ Message routing and queuing
- ✅ Client disconnection handling
- ✅ Connection statistics

**Supported Events**:
```
weather.update - Real-time weather
alert.new - New alerts
alert.updated - Alert changes
metric.calculated - New metrics
anomaly.detected - Anomalies
connection - Connection events
subscription - Subscription management
```

**Key Methods**:
```python
connect(client_id, websocket)              # Register connection
disconnect(client_id)                      # Unregister connection
subscribe(client_id, event_type, locations)  # Subscribe to event
broadcast(event_type, data, location_id)   # Send to subscribers
receive_message(client_id)                 # Get client message
```

---

### 5. Webhook Routes (`webhook_routes.py`) - 280 lines
**Purpose**: REST API for webhook management

**7 Webhook Endpoints**:

1. **`POST /api/webhooks/subscribe`**
   - Register new webhook subscription
   - Parameters: event, url, secret
   - Returns: subscription_id

2. **`DELETE /api/webhooks/unsubscribe/{subscription_id}`**
   - Unsubscribe from webhook
   - Parameters: subscription_id

3. **`GET /api/webhooks/subscriptions`**
   - List all subscriptions
   - Query: event (optional filter)
   - Returns: active subscriptions

4. **`GET /api/webhooks/subscriptions/{subscription_id}`**
   - Get specific subscription details

5. **`POST /api/webhooks/subscriptions/{subscription_id}/status`**
   - Update subscription status
   - Values: active, inactive, failed, suspended

6. **`GET /api/webhooks/statistics`**
   - Get webhook statistics and metrics

7. **`GET /api/webhooks/retries`**
   - Get pending retry queue
   - Returns: count and next retry time

**Additional Endpoints**:
- `POST /api/webhooks/retries/process` - Manually trigger retries
- `GET /api/webhooks/health` - System health check

---

### 6. Export Routes (`export_routes.py`) - 250 lines
**Purpose**: REST API for data export

**4 Export Endpoints**:

1. **`GET /api/export/alerts`**
   - Export alerts to CSV/JSON/JSONL
   - Query: format, fields, limit (up to 1000)

2. **`GET /api/export/weather`**
   - Export weather data
   - Query: format, location_id, start_date, end_date, fields, limit

3. **`GET /api/export/metrics`**
   - Export metrics by type
   - Query: format, metric_type (hourly/daily/weekly), location_id, dates, limit

4. **`GET /api/export/formats`**
   - List available export formats
   - Returns: JSON, CSV, JSONL descriptions

---

### 7. Real-time Routes (`realtime_routes.py`) - 200 lines
**Purpose**: WebSocket endpoints for real-time updates

**WebSocket Endpoints**:

1. **`WS /api/realtime/ws`**
   - Main WebSocket connection
   - Supports: subscribe, unsubscribe, ping messages
   - Returns: real-time events

**REST Endpoints**:

2. **`GET /api/realtime/status`**
   - Get real-time system status
   - Returns: connected clients, subscriptions, available events

3. **`GET /api/realtime/connections`**
   - Get connection statistics
   - Returns: connected clients, total subscriptions

---

## Configuration

### Environment Variables (.env)

**Webhook Configuration**:
```
WEBHOOKS_ENABLED=True
WEBHOOK_MAX_RETRIES=3
WEBHOOK_RETRY_DELAY_SECONDS=60
```

**Export Configuration**:
```
EXPORT_ENABLED=True
EXPORT_MAX_RECORDS=50000
EXPORT_FORMATS=json,csv,jsonl
```

**Real-time Configuration**:
```
REALTIME_ENABLED=True
WEBSOCKET_MAX_CONNECTIONS=1000
WEBSOCKET_MESSAGE_QUEUE_SIZE=100
```

**Advanced Filtering**:
```
FILTERING_ENABLED=True
FILTER_MAX_CONDITIONS=50
```

---

## Usage Examples

### Webhook Subscription
```bash
# Subscribe to HIGH alerts
curl -X POST http://localhost:8000/api/webhooks/subscribe \
  -d '{"event":"alert.created","url":"https://your-api.com/webhook","secret":"your-secret"}'

# Response: { "subscription_id": "uuid", ... }
```

### Data Export
```bash
# Export alerts as CSV
curl "http://localhost:8000/api/export/alerts?format=csv&limit=1000"

# Export weather data with date range
curl "http://localhost:8000/api/export/weather?format=json&start_date=2026-04-01&end_date=2026-04-02"
```

### WebSocket Connection
```javascript
// JavaScript example
const ws = new WebSocket("ws://localhost:8000/api/realtime/ws");

ws.onopen = () => {
  // Subscribe to HIGH alerts
  ws.send(JSON.stringify({
    type: "subscribe",
    event: "alert.new",
    locations: [1, 2, 3]  // Optional location filter
  }));
};

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  console.log(`Event: ${message.event}`, message.data);
};
```

### Advanced Filtering
```python
from src.api.advanced_filter import AdvancedFilter, FilterOperator

# Create filter
filter_obj = AdvancedFilter()
filter_obj.add_condition("severity", FilterOperator.EQ, "HIGH")
filter_obj.add_condition("created_at", FilterOperator.BETWEEN, 
                         ["2026-04-01", "2026-04-02"])

# Build query
query = filter_obj.build_query(base_query, Alert)
results = query.all()
```

---

## Webhook Payload Format

All webhooks POST the following JSON payload:

```json
{
  "event": "alert.created",
  "timestamp": "2026-04-02T10:30:00",
  "data": {
    "alert_id": 123,
    "severity": "HIGH",
    "alert_type": "TemperatureAlert",
    "description": "Temperature exceeded threshold"
  }
}
```

**Signature Header**:
```
X-Webhook-Signature: <HMAC-SHA256(payload, secret)>
X-Webhook-Event: alert.created
Content-Type: application/json
```

Verify signature:
```python
import hmac
import hashlib

signature = hmac.new(
    secret.encode(),
    payload.encode(),
    hashlib.sha256
).hexdigest()

assert request.headers['X-Webhook-Signature'] == signature
```

---

## WebSocket Message Format

### Subscribe to Event
```json
{
  "type": "subscribe",
  "event": "alert.new",
  "locations": [1, 2, 3]
}
```

### Unsubscribe from Event
```json
{
  "type": "unsubscribe",
  "event": "alert.new"
}
```

### Ping (Keep-alive)
```json
{
  "type": "ping"
}
```

### Received Messages
```json
{
  "event": "alert.new",
  "timestamp": "2026-04-02T10:30:00",
  "data": {
    "alert_id": 123,
    "severity": "HIGH"
  }
}
```

---

## Data Flow

### Webhook Delivery Flow
```
1. Event triggered (alert, weather, anomaly)
   ↓
2. Webhook Manager checks subscriptions
   ↓
3. For each subscription:
   a) Serialize event data to JSON
   b) Generate HMAC signature
   c) POST to webhook URL
   d) If success: Record delivery
   d) If failure: Add to retry queue
   ↓
4. Background job retries failed (every 10 min)
   ↓
5. Max 3 retries, then mark failed
```

### Export Flow
```
1. Client requests export
   ↓
2. Parse format and filters
   ↓
3. Query database with filters
   ↓
4. Convert to requested format
   ↓
5. Return data with metadata
```

### Real-time Flow
```
1. Client connects via WebSocket
   ↓
2. Send subscription message
   ↓
3. Server registers subscription
   ↓
4. When event occurs:
   a) Check matching subscriptions
   b) Format event data
   c) Send to connected clients
```

---

## Integration Points

### With Phase 1.6 (Alert System)
- Alert events trigger webhooks
- Alert data exported via API
- Real-time alert updates via WebSocket

### With Phase 1.4 (Data Processing)
- Metrics export available
- Anomaly events can trigger webhooks
- Weather data available for export

### With Phase 1.5 (Storage)
- Export respects retention policies
- Archive metadata included in exports

---

## Performance Considerations

1. **Webhook Delivery**: Async with 10-second timeout
2. **Export**: Supports up to 50,000 records
3. **Real-time**: Max 1,000 concurrent connections
4. **Filtering**: Up to 50 condition groups
5. **Retries**: 3 attempts with 60-second intervals

---

## Error Handling

- Invalid event types: Return 400 Bad Request
- Missing subscriptions: Return 404 Not Found
- Export failures: Return 400 with error message
- WebSocket errors: Automatic disconnect and cleanup
- Signature verification: HMAC-SHA256 on client side

---

## Summary

Phase 1.7 completes API enhancements with:
- ✅ Webhook system with retry logic
- ✅ Multi-format data export
- ✅ Real-time WebSocket updates
- ✅ Advanced filtering capabilities
- ✅ 15+ new REST endpoints
- ✅ Event-driven architecture

**Total**: 2,100+ lines of production-ready code
