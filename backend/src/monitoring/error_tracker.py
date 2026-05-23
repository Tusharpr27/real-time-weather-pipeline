"""
Error tracking module - Capture, categorize, and analyze application errors.
Provides exception tracking, error trending, correlation IDs, and alerting.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from enum import Enum
import traceback
import uuid
import threading
from collections import defaultdict, deque
import logging

logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """Error severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Categories of errors."""
    DATABASE = "database"
    VALIDATION = "validation"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    EXTERNAL_API = "external_api"
    INTERNAL = "internal"
    TIMEOUT = "timeout"
    RESOURCE = "resource"
    CONFIG = "config"
    UNKNOWN = "unknown"


@dataclass
class ErrorRecord:
    """Single error record."""
    error_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    error_type: str = ""
    message: str = ""
    severity: ErrorSeverity = ErrorSeverity.ERROR
    category: ErrorCategory = ErrorCategory.UNKNOWN
    timestamp: datetime = field(default_factory=datetime.utcnow)
    correlation_id: Optional[str] = None
    endpoint: Optional[str] = None
    method: Optional[str] = None
    status_code: Optional[int] = None
    
    # Stack trace and context
    stack_trace: str = ""
    exception_chain: List[str] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    
    # User and environment
    user_id: Optional[str] = None
    request_id: Optional[str] = None
    environment: str = "production"
    
    # Additional info
    tags: Dict[str, str] = field(default_factory=dict)
    occurred_count: int = 1
    last_occurred: Optional[datetime] = None


@dataclass
class ErrorTrend:
    """Error trend data."""
    error_type: str
    category: ErrorCategory
    count: int
    unique_count: int
    severity_distribution: Dict[ErrorSeverity, int] = field(default_factory=dict)
    first_seen: Optional[datetime] = None
    last_seen: Optional[datetime] = None
    trend: str = "stable"  # increasing, decreasing, stable
    avg_occurrences_per_hour: float = 0.0


class ErrorTracker:
    """
    Central error tracking system.
    
    Features:
    - Exception capture with full context
    - Error categorization and severity assignment
    - Correlation IDs for request tracing
    - Error aggregation and deduplication
    - Trend analysis and spike detection
    - Error history with time-windowed stats
    - Automatic alerting on error rate increases
    """

    def __init__(self, history_limit: int = 10000, window_size: int = 3600):
        """
        Initialize error tracker.
        
        Args:
            history_limit: Maximum error records to keep
            window_size: Time window for aggregate calculations (seconds)
        """
        self.history_limit = history_limit
        self.window_size = window_size
        
        # Error storage
        self.errors: deque = deque(maxlen=history_limit)
        self.errors_by_type: Dict[str, deque] = defaultdict(
            lambda: deque(maxlen=history_limit)
        )
        self.errors_by_endpoint: Dict[str, deque] = defaultdict(
            lambda: deque(maxlen=history_limit)
        )
        
        # Aggregated error signatures
        self.error_signatures: Dict[str, ErrorRecord] = {}  # signature -> latest error
        
        # Tracking
        self.total_errors = 0
        self.errors_by_severity: Dict[ErrorSeverity, int] = defaultdict(int)
        self.errors_by_category: Dict[ErrorCategory, int] = defaultdict(int)
        
        # Spike detection
        self.error_rate_history: deque = deque(maxlen=120)  # 2 hours at 1-min intervals
        self.last_spike_check = datetime.utcnow()
        self.spike_threshold_increase = 2.0  # 2x normal rate
        
        # Thread safety
        self._lock = threading.RLock()

    def record_error(
        self,
        exception: Optional[Exception] = None,
        error_type: Optional[str] = None,
        message: Optional[str] = None,
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        category: ErrorCategory = ErrorCategory.UNKNOWN,
        endpoint: Optional[str] = None,
        method: Optional[str] = None,
        status_code: Optional[int] = None,
        correlation_id: Optional[str] = None,
        user_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        tags: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> str:
        """
        Record an error occurrence.
        
        Args:
            exception: Python exception object
            error_type: Error class name
            message: Error message
            severity: Error severity level
            category: Error category
            endpoint: API endpoint
            method: HTTP method
            status_code: HTTP status code
            correlation_id: Request correlation ID
            user_id: User ID if applicable
            context: Additional context data
            tags: Metadata tags
            **kwargs: Additional fields to store
        
        Returns:
            Error ID
        """
        with self._lock:
            # Derive error type from exception if not provided
            if not error_type and exception:
                error_type = type(exception).__name__
            
            # Get error message
            if not message:
                message = str(exception) if exception else "Unknown error"
            
            # Auto-categorize if needed
            if category == ErrorCategory.UNKNOWN and exception:
                category = self._categorize_error(exception, error_type)
            
            # Get stack trace
            stack_trace = ""
            exception_chain = []
            if exception:
                stack_trace = traceback.format_exc()
                # Extract exception chain
                exception_chain = self._extract_exception_chain(exception)
            
            # Create error record
            error_record = ErrorRecord(
                error_type=error_type or "Unknown",
                message=message,
                severity=severity,
                category=category,
                endpoint=endpoint,
                method=method,
                status_code=status_code,
                correlation_id=correlation_id or self._generate_correlation_id(),
                user_id=user_id,
                stack_trace=stack_trace,
                exception_chain=exception_chain,
                context=context or {},
                tags=tags or {}
            )
            
            # Store error
            self.errors.append(error_record)
            self.errors_by_type[error_type or "Unknown"].append(error_record)
            if endpoint:
                self.errors_by_endpoint[endpoint].append(error_record)
            
            # Update counters
            self.total_errors += 1
            self.errors_by_severity[severity] += 1
            self.errors_by_category[category] += 1
            
            # Try to deduplicate with error signature
            signature = self._get_error_signature(error_record)
            if signature in self.error_signatures:
                existing = self.error_signatures[signature]
                existing.occurred_count += 1
                existing.last_occurred = datetime.utcnow()
            else:
                self.error_signatures[signature] = error_record
            
            # Check for error spike
            self._check_error_spike()
            
            logger.error(
                f"Error recorded: {error_type} - {message}",
                extra={"error_id": error_record.error_id, "correlation_id": error_record.correlation_id}
            )
            
            return error_record.error_id

    def _categorize_error(
        self,
        exception: Exception,
        error_type: Optional[str]
    ) -> ErrorCategory:
        """Automatically categorize an error based on its type."""
        type_name = error_type or type(exception).__name__
        message = str(exception).lower()
        
        # Database errors
        if any(x in type_name for x in ["DatabaseError", "SQLAlchemy", "psycopg2", "Database"]):
            return ErrorCategory.DATABASE
        if any(x in message for x in ["database", "connection refused", "connection timeout"]):
            return ErrorCategory.DATABASE
        
        # Validation errors
        if any(x in type_name for x in ["ValidationError", "ValueError", "TypeError"]):
            return ErrorCategory.VALIDATION
        if any(x in message for x in ["validation", "invalid", "required"]):
            return ErrorCategory.VALIDATION
        
        # Authentication/Authorization
        if any(x in type_name for x in ["AuthenticationError", "PermissionError"]):
            if "permission" in message or "unauthorized" in message:
                return ErrorCategory.AUTHORIZATION
            return ErrorCategory.AUTHENTICATION
        
        # Timeouts
        if any(x in type_name for x in ["TimeoutError", "Timeout"]):
            return ErrorCategory.TIMEOUT
        if "timeout" in message:
            return ErrorCategory.TIMEOUT
        
        # External API errors
        if any(x in type_name for x in ["ConnectionError", "HTTPError"]):
            return ErrorCategory.EXTERNAL_API
        if any(x in message for x in ["api", "external", "http", "request"]):
            return ErrorCategory.EXTERNAL_API
        
        # Resource errors
        if any(x in type_name for x in ["MemoryError", "IOError", "OSError"]):
            return ErrorCategory.RESOURCE
        if any(x in message for x in ["memory", "disk", "resource"]):
            return ErrorCategory.RESOURCE
        
        # Configuration errors
        if any(x in type_name for x in ["ConfigError", "KeyError"]):
            return ErrorCategory.CONFIG
        if "config" in message:
            return ErrorCategory.CONFIG
        
        return ErrorCategory.INTERNAL

    def _extract_exception_chain(self, exception: Exception) -> List[str]:
        """Extract exception chain from a traceback."""
        chain = []
        current = exception
        while current is not None:
            chain.append(f"{type(current).__name__}: {str(current)}")
            current = current.__cause__ or current.__context__
        return chain

    def _get_error_signature(self, error: ErrorRecord) -> str:
        """Generate unique signature for error deduplication."""
        return f"{error.error_type}:{error.endpoint}:{error.status_code}"

    def _generate_correlation_id(self) -> str:
        """Generate unique correlation ID for request tracing."""
        return str(uuid.uuid4())

    def _check_error_spike(self) -> None:
        """Check if error rate has spiked."""
        now = datetime.utcnow()
        
        # Add to rate history every minute
        if (now - self.last_spike_check).total_seconds() >= 60:
            recent_errors = sum(
                1 for e in self.errors
                if (now - e.timestamp).total_seconds() < 60
            )
            self.error_rate_history.append(recent_errors)
            self.last_spike_check = now
            
            # Check for spike
            if len(self.error_rate_history) > 1:
                current_rate = self.error_rate_history[-1]
                avg_rate = sum(self.error_rate_history[:-1]) / max(len(self.error_rate_history) - 1, 1)
                
                if avg_rate > 0 and current_rate > (avg_rate * self.spike_threshold_increase):
                    logger.warning(
                        f"Error rate spike detected! Current: {current_rate}/min, "
                        f"Average: {avg_rate:.1f}/min"
                    )

    def get_error_stats(
        self,
        window_seconds: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get error statistics within a time window.
        
        Args:
            window_seconds: Time window for calculations
        
        Returns:
            Statistics dictionary
        """
        window = window_seconds or self.window_size
        cutoff_time = datetime.utcnow() - timedelta(seconds=window)
        
        with self._lock:
            recent_errors = [e for e in self.errors if e.timestamp >= cutoff_time]
            
            severity_dist = defaultdict(int)
            category_dist = defaultdict(int)
            
            for error in recent_errors:
                severity_dist[error.severity.value] += 1
                category_dist[error.category.value] += 1
            
            return {
                "total_errors": len(recent_errors),
                "unique_errors": len(set(e.error_type for e in recent_errors)),
                "errors_by_severity": dict(severity_dist),
                "errors_by_category": dict(category_dist),
                "error_rate_per_minute": len(recent_errors) / max(window / 60, 1),
                "avg_errors_per_endpoint": len(recent_errors) / max(len(set(e.endpoint for e in recent_errors if e.endpoint)), 1)
            }

    def get_error_trends(self) -> List[ErrorTrend]:
        """Get error trend analysis."""
        with self._lock:
            trends: Dict[str, ErrorTrend] = {}
            
            for error in self.errors:
                key = f"{error.error_type}:{error.category.value}"
                
                if key not in trends:
                    trends[key] = ErrorTrend(
                        error_type=error.error_type,
                        category=error.category,
                        count=0,
                        unique_count=0
                    )
                
                trend = trends[key]
                trend.count += 1
                trend.first_seen = error.timestamp if not trend.first_seen else min(trend.first_seen, error.timestamp)
                trend.last_seen = max(trend.last_seen or datetime.utcnow(), error.timestamp)
                
                # Severity distribution
                severity = error.severity.value
                trend.severity_distribution[severity] = trend.severity_distribution.get(severity, 0) + 1
            
            # Calculate trends
            for trend in trends.values():
                time_span = (trend.last_seen - trend.first_seen).total_seconds() if trend.last_seen and trend.first_seen else 1
                trend.avg_occurrences_per_hour = trend.count / max(time_span / 3600, 1)
            
            return list(trends.values())

    def get_recent_errors(
        self,
        limit: int = 50,
        severity: Optional[ErrorSeverity] = None,
        category: Optional[ErrorCategory] = None,
        endpoint: Optional[str] = None
    ) -> List[ErrorRecord]:
        """Get recent errors with optional filtering."""
        with self._lock:
            errors = list(self.errors)
            
            if severity:
                errors = [e for e in errors if e.severity == severity]
            if category:
                errors = [e for e in errors if e.category == category]
            if endpoint:
                errors = [e for e in errors if e.endpoint == endpoint]
            
            return errors[-limit:]

    def get_error_by_id(self, error_id: str) -> Optional[ErrorRecord]:
        """Retrieve specific error by ID."""
        with self._lock:
            for error in self.errors:
                if error.error_id == error_id:
                    return error
        return None

    def get_errors_by_correlation_id(self, correlation_id: str) -> List[ErrorRecord]:
        """Get all errors in a correlation group."""
        with self._lock:
            return [e for e in self.errors if e.correlation_id == correlation_id]

    def get_endpoint_errors(self, endpoint: str, limit: int = 100) -> List[ErrorRecord]:
        """Get errors for a specific endpoint."""
        with self._lock:
            return list(self.errors_by_endpoint[endpoint])[-limit:]

    def get_critical_errors(self) -> List[ErrorRecord]:
        """Get all critical errors."""
        return self.get_recent_errors(limit=1000, severity=ErrorSeverity.CRITICAL)

    def reset(self) -> None:
        """Reset all error tracking."""
        with self._lock:
            self.errors.clear()
            self.errors_by_type.clear()
            self.errors_by_endpoint.clear()
            self.error_signatures.clear()
            self.total_errors = 0
            self.errors_by_severity.clear()
            self.errors_by_category.clear()


# Global instance
_error_tracker: Optional[ErrorTracker] = None


def get_error_tracker() -> ErrorTracker:
    """Get or create global error tracker instance."""
    global _error_tracker
    if _error_tracker is None:
        _error_tracker = ErrorTracker()
    return _error_tracker
