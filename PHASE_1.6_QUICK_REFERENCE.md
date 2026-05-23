# Phase 1.6 Quick Reference Guide

## 🚀 Quick Start

### Enable Alert System
```bash
# In .env
ALERT_SYSTEM_ENABLED=True
ALERT_NOTIFICATION_ENABLED=True
ALERT_ESCALATION_ENABLED=True

# Email configuration
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-specific-password
ALERT_EMAIL_TO=recipient@example.com
```

### Start Application
```bash
cd d:\Real time weather data pipeline system\backend
source venv/Scripts/activate  # Windows: venv\Scripts\activate
python main.py
```

---

## 📡 API Endpoints Quick Reference

### Alert Management
```bash
# Get active alerts
curl http://localhost:8000/api/alerts/active

# Acknowledge alert
curl -X POST http://localhost:8000/api/alerts/acknowledge/1 \
  -d '{"user_id":"john", "reason":"Investigating"}'

# Resolve alert
curl -X POST http://localhost:8000/api/alerts/resolve/1 \
  -d '{"user_id":"john", "resolution":"Issue resolved"}'

# Get alert history
curl http://localhost:8000/api/alerts/1/history

# Get statistics
curl http://localhost:8000/api/alerts/statistics
```

### Escalation
```bash
# Check escalations
curl http://localhost:8000/api/alerts/escalations/check

# Get escalation status
curl http://localhost:8000/api/alerts/escalations/1/status

# Reset escalation
curl -X POST http://localhost:8000/api/alerts/escalations/1/reset
```

### User Preferences
```bash
# Get preferences
curl http://localhost:8000/api/alerts/preferences/john_doe

# Update preferences
curl -X POST http://localhost:8000/api/alerts/preferences/john_doe \
  -d '{"email_enabled":true, "email_address":"john@example.com"}'

# Set quiet hours
curl -X POST http://localhost:8000/api/alerts/preferences/john_doe/quiet-hours \
  -d '{"enabled":true, "start_time":"22:00", "end_time":"08:00"}'

# Check if should notify
curl "http://localhost:8000/api/alerts/preferences/john_doe/should-notify?alert_severity=HIGH"
```

---

## 🐍 Python Usage Examples

### Send Alert Notification
```python
from src.alerts import get_alert_notifier, NotificationChannel

notifier = get_alert_notifier()
result = await notifier.notify_alert(
    alert_id=1,
    channels=[NotificationChannel.EMAIL, NotificationChannel.LOG],
    recipients=["user@example.com"]
)
print(result)
```

### Check & Escalate Alerts
```python
from src.alerts import get_escalation_manager

manager = get_escalation_manager()
escalations = await manager.check_escalations()

for esc in escalations:
    print(f"Escalating alert {esc['alert_id']} to level {esc['next_level']}")
    await manager.escalate_alert(esc["alert_id"])
```

### Track Alert State
```python
from src.alerts import get_alert_tracker

tracker = get_alert_tracker()

# Acknowledge
await tracker.acknowledge_alert(alert_id=1, user_id="john", reason="Investigating")

# Resolve
await tracker.resolve_alert(alert_id=1, user_id="john", resolution="Fixed")

# Get history
history = await tracker.get_alert_history(1)
print(f"Created at: {history['created_at']}")
print(f"Acknowledged at: {history['acknowledged_at']}")
print(f"Resolved at: {history['resolved_at']}")
```

### Manage User Preferences
```python
from src.alerts import get_user_preferences_manager

prefs = get_user_preferences_manager()

# Create preferences
prefs.create_user_preferences(
    user_id="john",
    email_enabled=True,
    email_address="john@example.com",
    alert_severity_filter=["MEDIUM", "HIGH"]
)

# Set quiet hours
prefs.set_quiet_hours("john", enabled=True, start_time="22:00", end_time="08:00")

# Check if should notify
should_notify = prefs.should_notify_alert(
    user_id="john",
    alert_severity="HIGH",
    location_id=1
)
print(f"Should notify: {should_notify}")
```

---

## ⚙️ Configuration Reference

### Alert System Flags
| Setting | Default | Description |
|---------|---------|-------------|
| ALERT_SYSTEM_ENABLED | True | Enable/disable entire system |
| ALERT_NOTIFICATION_ENABLED | True | Enable email notifications |
| ALERT_ESCALATION_ENABLED | True | Enable escalation logic |
| ALERT_BATCH_NOTIFICATIONS | False | Batch vs immediate |
| ALERT_BATCH_INTERVAL_MINUTES | 15 | Batch interval if enabled |

### Escalation Rules
| Severity | Initial Delay | Escalation Interval | Max Escalations |
|----------|---------------|-------------------|-----------------|
| LOW | 24 hours | 48 hours | 0 (none) |
| MEDIUM | 2 hours | 4 hours | 2 |
| HIGH | 0 min | 1 hour | 5 |

### Quiet Hours
| Setting | Default | Description |
|---------|---------|-------------|
| QUIET_HOURS_ENABLED | False | Enable quiet hours |
| QUIET_HOURS_START | 22:00 | Start time (HH:MM) |
| QUIET_HOURS_END | 08:00 | End time (HH:MM) |
| QUIET_HOURS_SKIP_LOW | True | Skip LOW alerts |
| QUIET_HOURS_ALLOW_HIGH | True | Always allow HIGH |

---

## 📊 Database Fields

### Alert Table Extensions
```sql
ALTER TABLE alert ADD COLUMN escalation_level INTEGER DEFAULT 0;
ALTER TABLE alert ADD COLUMN escalated_at TIMESTAMP;
ALTER TABLE alert ADD COLUMN acknowledged_at TIMESTAMP;
ALTER TABLE alert ADD COLUMN acknowledged_by VARCHAR(255);
ALTER TABLE alert ADD COLUMN resolved_at TIMESTAMP;
ALTER TABLE alert ADD COLUMN resolved_by VARCHAR(255);
```

---

## 🔍 Debugging

### Check Logs
```bash
# View application logs
tail -f logs/weather_pipeline.log

# Filter alert logs
grep "ALERT\|escalat\|notif" logs/weather_pipeline.log
```

### Test Email Configuration
```python
from config import settings
from src.alerts.alert_notifier import EmailNotifier

notifier = EmailNotifier()
success, msg = await notifier.send_alert_email(
    recipient="test@example.com",
    alert_type="TemperatureAlert",
    location="Delhi",
    description="Test alert",
    severity="HIGH"
)
print(f"Success: {success}, Message: {msg}")
```

### Check Escalation Status
```python
from src.alerts import get_escalation_manager

manager = get_escalation_manager()
status = await manager.get_alert_status(alert_id=1)
print(f"Escalation Level: {status['escalation_level']}")
print(f"Can Escalate: {status['can_escalate']}")
print(f"Age Hours: {status['age_hours']}")
```

---

## 🚨 Common Issues & Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| Email not sending | SMTP credentials missing | Set SMTP_USERNAME & SMTP_PASSWORD in .env |
| Email sending failed | Wrong Gmail app password | Use app-specific password, not Gmail password |
| Alerts not escalating | ALERT_ESCALATION_ENABLED=False | Set to True in .env |
| Quiet hours not working | Timezone issue | Check system timezone |
| No notifications | ALERT_NOTIFICATION_ENABLED=False | Set to True in .env |

---

## 📈 Monitoring

### Health Check
```bash
curl http://localhost:8000/api/alerts/health
```

### Scheduler Status
```python
from src.alerts.alert_scheduler import create_alert_scheduler
from src.fetcher.scheduler import get_scheduler

base_scheduler = get_scheduler()
alert_scheduler = create_alert_scheduler(base_scheduler.scheduler)
status = alert_scheduler.get_status()
print(f"Jobs running: {status['jobs_count']}")
for job in status['jobs']:
    print(f"  {job['name']}: {job['next_run']}")
```

### Alert Statistics
```bash
curl http://localhost:8000/api/alerts/statistics | python -m json.tool
```

---

## 🧪 Test Scenarios

### Scenario 1: New HIGH Severity Alert
```python
# Alert created by anomaly detector
# System should:
# 1. Create alert in database
# 2. Send email immediately (0 delay)
# 3. Check every 5 minutes for escalation
# 4. Escalate after 1 hour if unacknowledged
```

### Scenario 2: User Acknowledges Alert
```python
# POST /api/alerts/acknowledge/1
# System should:
# 1. Update status to "acknowledged"
# 2. Record user and timestamp
# 3. Reset escalation level to 0
# 4. Stop escalations
```

### Scenario 3: Quiet Hours Active
```python
# 23:00 - during quiet hours
# LOW alert triggered
# System should:
# 1. Check user preferences
# 2. Skip notification (LOW + quiet hours)
# 3. Still create alert in database
# 4. Notify when quiet hours end
```

---

## 📚 File Locations

| File | Purpose |
|------|---------|
| `src/alerts/alert_notifier.py` | Email notifications |
| `src/alerts/escalation_manager.py` | Escalation logic |
| `src/alerts/user_preferences.py` | User settings |
| `src/alerts/alert_tracker.py` | Alert tracking |
| `src/alerts/alert_routes.py` | API endpoints |
| `src/alerts/alert_scheduler.py` | Background jobs |
| `config.py` | Configuration |
| `.env` | Environment variables |

---

## 🔗 Related Documentation

- [Phase 1.6 Full Guide](./PHASE_1.6_ALERT_SYSTEM.md)
- [Implementation Summary](./IMPLEMENTATION_SUMMARY_PHASE_1.6.md)
- [Main README](./README.md)

---

## ⏱️ Background Job Schedule

| Job | Frequency | Time |
|-----|-----------|------|
| Escalation Check | Every 5 minutes | 00:00, 00:05, 00:10... |
| Notification Retry | Every 10 minutes | 00:00, 00:10, 00:20... |
| Alert Cleanup | Daily | 03:00 UTC |
| Alert Summary | Every 6 hours | 00:00, 06:00, 12:00, 18:00 UTC |

---

**Quick Reference Version**: 1.0  
**Phase**: 1.6 Alert System  
**Last Updated**: Current Session
