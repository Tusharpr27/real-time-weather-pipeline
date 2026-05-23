# Phase 1.7 Quick Reference

## 🚀 Quick Start

### Enable Phase 1.7 Features
```bash
# In .env
WEBHOOKS_ENABLED=True
EXPORT_ENABLED=True
REALTIME_ENABLED=True
FILTERING_ENABLED=True
```

### Restart Application
```bash
# Terminal
python main.py
```

---

## 📡 API Quick Reference

### Webhooks
```bash
# Subscribe to alerts
curl -X POST http://localhost:8000/api/webhooks/subscribe \
  -H "Content-Type: application/json" \
  -d '{"event":"alert.created","url":"https://your-api.com/hook"}'

# List subscriptions
curl http://localhost:8000/api/webhooks/subscriptions

# Get statistics
curl http://localhost:8000/api/webhooks/statistics

# Check retries
curl http://localhost:8000/api/webhooks/retries

# Unsubscribe
curl -X DELETE http://localhost:8000/api/webhooks/unsubscribe/{subscription_id}
```

### Data Export
```bash
# Export alerts as JSON
curl http://localhost:8000/api/export/alerts?format=json&limit=1000

# Export as CSV
curl http://localhost:8000/api/export/alerts?format=csv&limit=1000

# Export weather data
curl "http://localhost:8000/api/export/weather?format=json&location_id=1&start_date=2026-04-01&end_date=2026-04-02"

# Export metrics
curl "http://localhost:8000/api/export/metrics?format=json&metric_type=hourly"

# List formats
curl http://localhost:8000/api/export/formats
```

### Real-time WebSocket
```javascript
// Connect
const ws = new WebSocket("ws://localhost:8000/api/realtime/ws");

// Subscribe to alerts
ws.send(JSON.stringify({
  type: "subscribe",
  event: "alert.new",
  locations: [1, 2, 3]
}));

// Handle messages
ws.onmessage = (event) => {
  const msg = JSON.parse(event.data);
  console.log(msg.event, msg.data);
};

// Get status
fetch("http://localhost:8000/api/realtime/status")
  .then(r => r.json())
  .then(d => console.log(d));
```

---

## 🐍 Python Usage

### Webhook Management
```python
from src.api.webhook_manager import get_webhook_manager, WebhookEvent

mgr = get_webhook_manager()

# Register
sub_id = mgr.register_webhook(
    WebhookEvent.ALERT_CREATED,
    "https://api.example.com/webhook",
    "secret-key"
)

# Trigger
await mgr.trigger_webhook(WebhookEvent.ALERT_CREATED, {
    "alert_id": 1,
    "severity": "HIGH"
})

# Get stats
stats = mgr.get_statistics()
print(f"Subscriptions: {stats['total']}")
```

### Data Export
```python
from src.api.data_exporter import get_data_exporter, ExportFormat

exp = get_data_exporter()

# Export alerts
result = await exp.export_alerts(
    format=ExportFormat.CSV,
    limit=1000
)
print(result['data'])

# Export weather
result = await exp.export_weather_data(
    format=ExportFormat.JSON,
    location_id=1,
    date_range={"start": "2026-04-01", "end": "2026-04-02"}
)
```

### Advanced Filtering
```python
from src.api.advanced_filter import AdvancedFilter, FilterOperator

# Create filter
f = AdvancedFilter()
f.add_condition("severity", FilterOperator.EQ, "HIGH")
f.add_condition("created_at", FilterOperator.BETWEEN, 
                ["2026-04-01", "2026-04-02"])

# Apply to query
from src.database.models import Alert
from src.database.database import create_session

db = create_session()
query = db.query(Alert)
filtered = f.build_query(query, Alert)
results = filtered.all()
```

### Real-time Updates
```python
from src.api.websocket_handler import get_websocket_handler, RealtimeEvent

handler = get_websocket_handler()

# Broadcast event
await handler.broadcast(
    RealtimeEvent.ALERT_NEW,
    {
        "alert_id": 1,
        "severity": "HIGH",
        "location": "Delhi"
    },
    location_id=1
)

# Get stats
stats = handler.get_statistics()
print(f"Connected: {stats['connected_clients']}")
```

---

## 📊 Configuration Options

| Setting | Default | Description |
|---------|---------|-------------|
| WEBHOOKS_ENABLED | True | Enable webhook system |
| WEBHOOK_MAX_RETRIES | 3 | Retry attempts |
| WEBHOOK_RETRY_DELAY_SECONDS | 60 | Retry delay |
| EXPORT_ENABLED | True | Enable export |
| EXPORT_MAX_RECORDS | 50000 | Max records per export |
| REALTIME_ENABLED | True | Enable WebSocket |
| WEBSOCKET_MAX_CONNECTIONS | 1000 | Max connections |
| FILTERING_ENABLED | True | Enable advanced filters |

---

## 🔍 Common Tasks

### Export Monthly Data
```bash
curl "http://localhost:8000/api/export/alerts?format=csv&limit=10000" > alerts_$(date +%Y%m).csv
```

### Subscribe to All High Alerts
```bash
curl -X POST http://localhost:8000/api/webhooks/subscribe \
  -d '{"event":"alert.escalated","url":"https://me.com/alerts"}'
```

### Monitor Real-time Alerts
```javascript
// Client-side monitoring
const ws = new WebSocket("ws://localhost:8000/api/realtime/ws");
ws.send(JSON.stringify({
  type: "subscribe",
  event: "alert.new"
}));
ws.onmessage = (e) => {
  const alert = JSON.parse(e.data).data;
  console.log(`🚨 ${alert.severity}: ${alert.alert_type}`);
};
```

### Export Specific Location
```bash
curl "http://localhost:8000/api/export/weather?format=json&location_id=1&limit=5000" > delhi_weather.json
```

### Filter Complex Queries
```python
# Export HIGH alerts from last 24 hours at specific locations
f = AdvancedFilter()
f.add_condition("severity", FilterOperator.EQ, "HIGH")
f.add_condition("location_id", FilterOperator.IN, [1, 2, 3])

from datetime import datetime, timedelta
yesterday = (datetime.utcnow() - timedelta(days=1)).isoformat()
f.add_condition("created_at", FilterOperator.BETWEEN, 
                [yesterday, datetime.utcnow().isoformat()])
```

---

## 🧪 Test Scenarios

### Scenario 1: Alert via Webhook
1. Subscribe webhook: POST /webhooks/subscribe
2. Create alert (via anomaly detector)
3. Webhook POST received at your URL
4. Verify HMAC signature

### Scenario 2: Export & Download
1. Request: GET /export/alerts?format=csv
2. Parse CSV response
3. Import to Excel/database
4. Analyze data

### Scenario 3: Real-time Dashboard
1. Connect WebSocket
2. Subscribe to events
3. Receive real-time updates
4. Update UI dynamically

---

## 📋 File Locations

| Component | File |
|-----------|------|
| Webhooks | src/api/webhook_manager.py, webhook_routes.py |
| Export | src/api/data_exporter.py, export_routes.py |
| Real-time | src/api/websocket_handler.py, realtime_routes.py |
| Filtering | src/api/advanced_filter.py |

---

## 🔗 Integration

All Phase 1.7 features are:
- ✅ Integrated with FastAPI app
- ✅ Configured via .env
- ✅ Async/await support
- ✅ Error handled
- ✅ Logged comprehensively

---

**Phase 1.7 Status**: ✅ COMPLETE  
**Endpoints Added**: 15+  
**WebSocket Support**: ✅  
**Export Formats**: JSON, CSV, JSONL
