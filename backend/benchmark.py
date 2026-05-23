"""
Performance Benchmarking Script for Real-Time Weather Pipeline
Load testing with Locust - Run: locust -f benchmark.py
"""

from locust import HttpUser, task, between
import random
from datetime import datetime, timedelta


class WeatherPipelineUser(HttpUser):
    """Simulated user for load testing the Weather Pipeline API"""
    
    wait_time = between(1, 3)  # Wait 1-3 seconds between requests
    
    def on_start(self):
        """Initialize test data"""
        self.locations = ["Delhi", "Mumbai", "Bangalore", "Chennai", "Kolkata"]
        self.start_time = datetime.utcnow()
    
    # =========================================================================
    # Health & Status Endpoints (Low Priority)
    # =========================================================================
    
    @task(1)
    def health_check(self):
        """Check system health"""
        self.client.get("/api/health")
    
    @task(1)
    def system_root(self):
        """Root endpoint"""
        self.client.get("/")
    
    # =========================================================================
    # Weather Data Endpoints (High Priority)
    # =========================================================================
    
    @task(5)
    def get_current_weather(self):
        """Get current weather for random location"""
        location = random.choice(self.locations)
        self.client.get(f"/api/weather/current/{location}")
    
    @task(3)
    def get_weather_history(self):
        """Get historical weather data"""
        location = random.choice(self.locations)
        days = random.choice([7, 14, 30])
        self.client.get(f"/api/weather/history/{location}", params={"days": days})
    
    @task(2)
    def get_weather_stats(self):
        """Get weather statistics"""
        location = random.choice(self.locations)
        self.client.get(f"/api/weather/stats/{location}")
    
    # =========================================================================
    # Alert Endpoints (Medium Priority)
    # =========================================================================
    
    @task(3)
    def get_alerts(self):
        """Get all alerts"""
        self.client.get("/api/weather/alerts", params={"limit": 50})
    
    @task(2)
    def get_location_alerts(self):
        """Get alerts for specific location"""
        location = random.choice(self.locations)
        self.client.get(f"/api/weather/alerts/{location}")
    
    @task(1)
    def acknowledge_alert(self):
        """Acknowledge an alert"""
        alert_id = random.randint(1, 100)
        self.client.put(
            f"/api/weather/alerts/{alert_id}/acknowledge",
            json={"notes": "Acknowledged"}
        )
    
    # =========================================================================
    # Storage Endpoints (Low Priority)
    # =========================================================================
    
    @task(2)
    def get_storage_stats(self):
        """Get storage statistics"""
        self.client.get("/api/storage/stats")
    
    @task(1)
    def get_archives(self):
        """Get list of archives"""
        self.client.get("/api/storage/archives", params={"limit": 10})
    
    # =========================================================================
    # Export Endpoints (Medium Priority)
    # =========================================================================
    
    @task(2)
    def export_alerts(self):
        """Export alerts"""
        export_format = random.choice(["json", "csv", "jsonl"])
        self.client.get(
            "/api/export/alerts",
            params={"format": export_format, "limit": 100}
        )
    
    @task(1)
    def export_weather_data(self):
        """Export weather data"""
        location = random.choice(self.locations)
        export_format = random.choice(["json", "csv"])
        self.client.get(
            "/api/export/weather",
            params={
                "format": export_format,
                "location_id": location,
                "limit": 500
            }
        )
    
    # =========================================================================
    # Monitoring Endpoints (Low Priority - Background Requests)
    # =========================================================================
    
    @task(1)
    def get_metrics_overview(self):
        """Get performance metrics"""
        self.client.get("/api/monitoring/metrics/overview")
    
    @task(1)
    def get_system_health(self):
        """Get comprehensive system health"""
        self.client.get("/api/monitoring/health")
    
    @task(1)
    def get_error_stats(self):
        """Get error statistics"""
        self.client.get("/api/monitoring/errors/overview", params={"window_seconds": 3600})
    
    @task(1)
    def get_dashboard(self):
        """Get monitoring dashboard data"""
        self.client.get("/api/monitoring/dashboard")


class AdminUser(HttpUser):
    """Administrative user with focus on management endpoints"""
    
    wait_time = between(5, 10)  # Less frequent requests
    
    def on_start(self):
        """Initialize admin"""
        self.locations = ["Delhi", "Mumbai", "Bangalore"]
    
    @task(5)
    def monitor_system(self):
        """Monitor system health"""
        self.client.get("/api/monitoring/health")
    
    @task(3)
    def check_metrics(self):
        """Check performance metrics"""
        self.client.get("/api/monitoring/metrics/overview")
    
    @task(2)
    def view_audit_logs(self):
        """View audit logs"""
        self.client.get("/api/monitoring/audit/overview")
    
    @task(1)
    def get_storage_status(self):
        """Check storage status"""
        self.client.get("/api/storage/stats")


# ============================================================================
# Load Testing Configuration
# ============================================================================

"""
LOAD TEST PROFILES:

1. LIGHT LOAD (Development/Testing)
   - 10 users
   - Spawn rate: 1 user/sec
   - Runtime: 5 minutes
   Command: locust -f benchmark.py --users 10 --spawn-rate 1

2. MODERATE LOAD (Staging)
   - 50 users
   - Spawn rate: 5 users/sec
   - Runtime: 15 minutes
   Command: locust -f benchmark.py --users 50 --spawn-rate 5

3. HEAVY LOAD (Production Simulation)
   - 100+ users
   - Spawn rate: 10 users/sec
   - Runtime: 30 minutes
   Command: locust -f benchmark.py --users 100 --spawn-rate 10

4. STRESS TEST (Capacity Planning)
   - 500 users
   - Spawn rate: 25 users/sec
   - Runtime: 60 minutes
   Command: locust -f benchmark.py --users 500 --spawn-rate 25

5. SPIKE TEST (Sudden Traffic)
   - 1000 users
   - Spawn rate: 100 users/sec (rapid increase)
   - Runtime: 10 minutes
   Command: locust -f benchmark.py --users 1000 --spawn-rate 100

HEADLESS MODE (CI/CD):
locust -f benchmark.py --users 100 --spawn-rate 10 --run-time 10m --headless -u <url>

WITH STATS FILE:
locust -f benchmark.py --users 50 --spawn-rate 5 --run-time 5m --csv=results/load_test

WEB UI (Default):
locust -f benchmark.py
Then visit: http://localhost:8089

EXPECTED METRICS:
- Response Time: < 500ms (p95), < 1000ms (p99)
- Error Rate: < 1% on all endpoints
- Throughput: > 100 RPS at moderate load
- Database: < 100ms query time
- Memory: Stable with < 500MB increase under load
"""

# ============================================================================
# Performance Benchmarks (Baseline Targets)
# ============================================================================

PERFORMANCE_TARGETS = {
    "/api/health": {
        "response_time_p95": 50,  # 50ms
        "response_time_p99": 100,  # 100ms
        "error_rate": 0.1,  # 0.1%
    },
    "/api/weather/current/{location}": {
        "response_time_p95": 200,  # 200ms
        "response_time_p99": 500,  # 500ms
        "error_rate": 0.5,  # 0.5%
    },
    "/api/weather/history/{location}": {
        "response_time_p95": 500,  # 500ms
        "response_time_p99": 1000,  # 1 second
        "error_rate": 1.0,  # 1%
    },
    "/api/weather/alerts": {
        "response_time_p95": 300,  # 300ms
        "response_time_p99": 800,  # 800ms
        "error_rate": 0.5,
    },
    "/api/export/alerts": {
        "response_time_p95": 2000,  # 2 seconds
        "response_time_p99": 5000,  # 5 seconds
        "error_rate": 1.0,
    },
    "/api/monitoring/dashboard": {
        "response_time_p95": 1000,  # 1 second
        "response_time_p99": 2000,  # 2 seconds
        "error_rate": 0.1,
    },
}

# ============================================================================
# Post-Test Analysis Script
# ============================================================================

POST_TEST_ANALYSIS = """
#!/bin/bash
# Analyze load test results

RESULTS_FILE=$1
if [ -z "$RESULTS_FILE" ]; then
    echo "Usage: ./analyze_results.sh <results_file.csv>"
    exit 1
fi

echo "=== Load Test Analysis ==="
echo "Results file: $RESULTS_FILE"
echo ""

# Extract metrics
python -c "
import csv
import statistics

response_times = []
with open('$RESULTS_FILE', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row.get('Response Time'):
            response_times.append(float(row['Response Time']))

if response_times:
    print(f'Average Response Time: {statistics.mean(response_times):.2f}ms')
    print(f'Median Response Time: {statistics.median(response_times):.2f}ms')
    print(f'P95 Response Time: {sorted(response_times)[int(len(response_times)*0.95)]:.2f}ms')
    print(f'P99 Response Time: {sorted(response_times)[int(len(response_times)*0.99)]:.2f}ms')
    print(f'Max Response Time: {max(response_times):.2f}ms')
    print(f'Min Response Time: {min(response_times):.2f}ms')
    print(f'Requests Tested: {len(response_times)}')
"
"""
