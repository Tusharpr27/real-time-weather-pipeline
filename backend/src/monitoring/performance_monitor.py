"""
Performance monitoring module - Track API performance metrics, system resources, and alerting.
Collects response times, throughput, memory/CPU usage, and generates performance alerts.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from enum import Enum
import time
import psutil
import threading
from collections import defaultdict, deque
import statistics
import logging

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of metrics to track."""
    REQUEST_TIME = "request_time"
    THROUGHPUT = "throughput"
    MEMORY_USAGE = "memory_usage"
    CPU_USAGE = "cpu_usage"
    DATABASE_QUERY = "database_query"
    CACHE_HIT_RATE = "cache_hit_rate"
    ERROR_RATE = "error_rate"


class AlertLevel(Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class PerformanceMetric:
    """Single performance metric data point."""
    metric_type: MetricType
    value: float
    timestamp: datetime = field(default_factory=datetime.utcnow)
    endpoint: Optional[str] = None
    method: Optional[str] = None
    tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class MetricThreshold:
    """Alert threshold for a metric."""
    metric_type: MetricType
    warning_threshold: float
    critical_threshold: float
    check_window_seconds: int = 60
    min_samples: int = 5


@dataclass
class PerformanceAlert:
    """Performance alert."""
    level: AlertLevel
    metric_type: MetricType
    message: str
    value: float
    threshold: float
    timestamp: datetime = field(default_factory=datetime.utcnow)
    endpoint: Optional[str] = None


class PerformanceMonitor:
    """
    Central performance monitoring system.
    
    Tracks:
    - Request response times (by endpoint, method)
    - API throughput (requests per second)
    - System resources (memory, CPU)
    - Database query performance
    - Cache hit rates
    - Error rates
    """

    def __init__(self, window_size: int = 3600, history_limit: int = 100000):
        """
        Initialize performance monitor.
        
        Args:
            window_size: Time window for aggregate calculations (seconds)
            history_limit: Maximum historical metrics to keep
        """
        self.window_size = window_size
        self.history_limit = history_limit
        
        # Metric storage
        self.metrics: deque = deque(maxlen=history_limit)
        self.metrics_by_endpoint: Dict[str, deque] = defaultdict(
            lambda: deque(maxlen=history_limit)
        )
        
        # Alerts
        self.alerts: deque = deque(maxlen=1000)
        self.thresholds: Dict[MetricType, MetricThreshold] = {}
        
        # Statistics
        self.request_count = 0
        self.error_count = 0
        self.active_requests: Dict[str, float] = {}  # endpoint -> start_time
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Initialize default thresholds
        self._init_default_thresholds()
        
        # Process monitoring
        self.process = psutil.Process()
        self.last_cpu_times = self.process.cpu_times()
        self.last_cpu_check = time.time()

    def _init_default_thresholds(self) -> None:
        """Initialize default metric thresholds."""
        self.thresholds = {
            MetricType.REQUEST_TIME: MetricThreshold(
                metric_type=MetricType.REQUEST_TIME,
                warning_threshold=1.0,  # 1 second
                critical_threshold=5.0,  # 5 seconds
                check_window_seconds=300
            ),
            MetricType.MEMORY_USAGE: MetricThreshold(
                metric_type=MetricType.MEMORY_USAGE,
                warning_threshold=70.0,  # 70%
                critical_threshold=90.0,  # 90%
                check_window_seconds=60
            ),
            MetricType.CPU_USAGE: MetricThreshold(
                metric_type=MetricType.CPU_USAGE,
                warning_threshold=75.0,  # 75%
                critical_threshold=95.0,  # 95%
                check_window_seconds=60
            ),
            MetricType.DATABASE_QUERY: MetricThreshold(
                metric_type=MetricType.DATABASE_QUERY,
                warning_threshold=2.0,  # 2 seconds
                critical_threshold=10.0,  # 10 seconds
                check_window_seconds=300
            ),
            MetricType.ERROR_RATE: MetricThreshold(
                metric_type=MetricType.ERROR_RATE,
                warning_threshold=5.0,  # 5%
                critical_threshold=15.0,  # 15%
                check_window_seconds=300
            ),
        }

    def record_request_start(self, endpoint: str) -> None:
        """Record the start of a request."""
        with self._lock:
            self.active_requests[endpoint] = time.time()

    def record_request_end(
        self,
        endpoint: str,
        method: str = "GET",
        response_time: float = 0.0,
        success: bool = True,
        **tags
    ) -> None:
        """
        Record the end of a request.
        
        Args:
            endpoint: API endpoint path
            method: HTTP method
            response_time: Time taken in seconds
            success: Whether request was successful
            **tags: Additional metadata tags
        """
        with self._lock:
            # Clean up active request
            if endpoint in self.active_requests:
                if response_time == 0.0:
                    response_time = time.time() - self.active_requests[endpoint]
                del self.active_requests[endpoint]
            
            # Record metric
            metric = PerformanceMetric(
                metric_type=MetricType.REQUEST_TIME,
                value=response_time,
                endpoint=endpoint,
                method=method,
                tags=tags
            )
            self.metrics.append(metric)
            self.metrics_by_endpoint[endpoint].append(metric)
            
            # Update counters
            self.request_count += 1
            if not success:
                self.error_count += 1
            
            # Check thresholds
            self._check_threshold(MetricType.REQUEST_TIME, response_time, endpoint)

    def record_metric(
        self,
        metric_type: MetricType,
        value: float,
        endpoint: Optional[str] = None,
        **tags
    ) -> None:
        """
        Record a generic performance metric.
        
        Args:
            metric_type: Type of metric
            value: Metric value
            endpoint: Optional endpoint name
            **tags: Additional metadata
        """
        with self._lock:
            metric = PerformanceMetric(
                metric_type=metric_type,
                value=value,
                endpoint=endpoint,
                tags=tags
            )
            self.metrics.append(metric)
            if endpoint:
                self.metrics_by_endpoint[endpoint].append(metric)
            
            # Check thresholds
            self._check_threshold(metric_type, value, endpoint)

    def record_database_query(
        self,
        query_time: float,
        table: str = "",
        operation: str = "QUERY",
        success: bool = True
    ) -> None:
        """Record database query performance."""
        self.record_metric(
            MetricType.DATABASE_QUERY,
            query_time,
            table=table,
            operation=operation,
            success=success
        )

    def record_error(self, endpoint: str = "", error_type: str = "") -> None:
        """Record an error occurrence."""
        with self._lock:
            self.error_count += 1
            # Recalculate error rate and check threshold
            if self.request_count > 0:
                error_rate = (self.error_count / self.request_count) * 100
                self._check_threshold(MetricType.ERROR_RATE, error_rate)

    def collect_system_metrics(self) -> None:
        """Collect current system resource metrics."""
        try:
            with self._lock:
                # Memory usage
                mem_info = self.process.memory_info()
                memory_percent = self.process.memory_percent()
                self.record_metric(MetricType.MEMORY_USAGE, memory_percent)
                
                # CPU usage
                cpu_percent = self.process.cpu_percent(interval=0.1)
                self.record_metric(MetricType.CPU_USAGE, cpu_percent)
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")

    def _check_threshold(
        self,
        metric_type: MetricType,
        value: float,
        endpoint: Optional[str] = None
    ) -> None:
        """Check if metric exceeds threshold and create alert if needed."""
        if metric_type not in self.thresholds:
            return
        
        threshold = self.thresholds[metric_type]
        
        if value >= threshold.critical_threshold:
            level = AlertLevel.CRITICAL
            limit = threshold.critical_threshold
        elif value >= threshold.warning_threshold:
            level = AlertLevel.WARNING
            limit = threshold.warning_threshold
        else:
            return  # No alert needed
        
        alert = PerformanceAlert(
            level=level,
            metric_type=metric_type,
            message=f"{metric_type.value} exceeded {level.value} threshold",
            value=value,
            threshold=limit,
            endpoint=endpoint
        )
        self.alerts.append(alert)
        logger.warning(f"Performance alert: {alert.message} (value: {value}, threshold: {limit})")

    def get_endpoint_stats(
        self,
        endpoint: str,
        window_seconds: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get performance statistics for an endpoint.
        
        Args:
            endpoint: Endpoint path
            window_seconds: Time window for calculations (uses default if None)
        
        Returns:
            Statistics dictionary
        """
        window = window_seconds or self.window_size
        cutoff_time = datetime.utcnow() - timedelta(seconds=window)
        
        with self._lock:
            metrics = [
                m for m in self.metrics_by_endpoint.get(endpoint, [])
                if m.timestamp >= cutoff_time
            ]
        
        if not metrics:
            return {
                "endpoint": endpoint,
                "count": 0,
                "avg_response_time": 0,
                "min_response_time": 0,
                "max_response_time": 0,
                "p95_response_time": 0,
                "p99_response_time": 0
            }
        
        response_times = [m.value for m in metrics if m.metric_type == MetricType.REQUEST_TIME]
        
        if response_times:
            sorted_times = sorted(response_times)
            return {
                "endpoint": endpoint,
                "count": len(response_times),
                "avg_response_time": statistics.mean(response_times),
                "min_response_time": min(response_times),
                "max_response_time": max(response_times),
                "stdev": statistics.stdev(response_times) if len(response_times) > 1 else 0,
                "p95_response_time": sorted_times[int(len(sorted_times) * 0.95)],
                "p99_response_time": sorted_times[int(len(sorted_times) * 0.99)],
            }
        
        return {
            "endpoint": endpoint,
            "count": 0,
            "avg_response_time": 0,
            "min_response_time": 0,
            "max_response_time": 0,
            "p95_response_time": 0,
            "p99_response_time": 0
        }

    def get_system_stats(self, window_seconds: Optional[int] = None) -> Dict[str, Any]:
        """Get system resource statistics."""
        window = window_seconds or self.window_size
        cutoff_time = datetime.utcnow() - timedelta(seconds=window)
        
        with self._lock:
            mem_metrics = [
                m.value for m in self.metrics
                if m.metric_type == MetricType.MEMORY_USAGE and m.timestamp >= cutoff_time
            ]
            cpu_metrics = [
                m.value for m in self.metrics
                if m.metric_type == MetricType.CPU_USAGE and m.timestamp >= cutoff_time
            ]
        
        result = {
            "current_memory_percent": psutil.virtual_memory().percent,
            "current_cpu_percent": psutil.cpu_percent(interval=0.1),
        }
        
        if mem_metrics:
            result["avg_memory_percent"] = statistics.mean(mem_metrics)
            result["max_memory_percent"] = max(mem_metrics)
        
        if cpu_metrics:
            result["avg_cpu_percent"] = statistics.mean(cpu_metrics)
            result["max_cpu_percent"] = max(cpu_metrics)
        
        return result

    def get_overall_stats(self) -> Dict[str, Any]:
        """Get overall performance statistics."""
        with self._lock:
            error_rate = (self.error_count / self.request_count * 100) if self.request_count > 0 else 0
            
            all_request_times = [
                m.value for m in self.metrics
                if m.metric_type == MetricType.REQUEST_TIME
            ]
            
            stats = {
                "total_requests": self.request_count,
                "total_errors": self.error_count,
                "error_rate_percent": error_rate,
                "active_requests": len(self.active_requests),
                "metrics_stored": len(self.metrics),
                "throughput_rps": self._calculate_throughput()
            }
            
            if all_request_times:
                stats["avg_response_time"] = statistics.mean(all_request_times)
                stats["p95_response_time"] = sorted(all_request_times)[int(len(all_request_times) * 0.95)]
            
            return stats

    def _calculate_throughput(self) -> float:
        """Calculate requests per second over the last minute."""
        cutoff_time = datetime.utcnow() - timedelta(seconds=60)
        recent_metrics = [m for m in self.metrics if m.timestamp >= cutoff_time]
        if recent_metrics:
            return len(recent_metrics) / 60.0
        return 0.0

    def get_recent_alerts(self, limit: int = 50) -> List[PerformanceAlert]:
        """Get recent performance alerts."""
        with self._lock:
            return list(self.alerts)[-limit:]

    def get_endpoint_metrics(self) -> List[str]:
        """Get list of all tracked endpoints."""
        with self._lock:
            return list(self.metrics_by_endpoint.keys())

    def reset(self) -> None:
        """Reset all metrics and counters."""
        with self._lock:
            self.metrics.clear()
            self.metrics_by_endpoint.clear()
            self.alerts.clear()
            self.request_count = 0
            self.error_count = 0
            self.active_requests.clear()


# Global instance
_monitor: Optional[PerformanceMonitor] = None


def get_monitor() -> PerformanceMonitor:
    """Get or create global performance monitor instance."""
    global _monitor
    if _monitor is None:
        _monitor = PerformanceMonitor()
    return _monitor
