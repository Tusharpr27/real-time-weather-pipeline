"""
Health checking module - Monitor system health status of all components.
Performs connectivity checks, dependency verification, and status reporting.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from enum import Enum
import asyncio
import logging

logger = logging.getLogger(__name__)


class ComponentStatus(Enum):
    """Health status of a component."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class ComponentType(Enum):
    """Types of components to monitor."""
    DATABASE = "database"
    CACHE = "cache"
    EXTERNAL_API = "external_api"
    WEBHOOK_DELIVERY = "webhook_delivery"
    WEBSOCKET = "websocket"
    FILE_STORAGE = "file_storage"
    MESSAGE_QUEUE = "message_queue"


@dataclass
class ComponentCheck:
    """Result of a component health check."""
    component_type: ComponentType
    component_name: str
    status: ComponentStatus
    response_time_ms: float
    timestamp: datetime = field(default_factory=datetime.utcnow)
    last_check_time: Optional[datetime] = None
    error_message: Optional[str] = None
    additional_info: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SystemHealthStatus:
    """Overall system health status."""
    overall_status: ComponentStatus
    timestamp: datetime = field(default_factory=datetime.utcnow)
    checks: List[ComponentCheck] = field(default_factory=list)
    healthy_components: int = 0
    degraded_components: int = 0
    unhealthy_components: int = 0
    response_time_ms: float = 0.0


class HealthChecker:
    """
    Central health checking system.
    
    Monitors:
    - Database connectivity
    - Cache availability
    - External API dependencies
    - Webhook delivery system
    - WebSocket connections
    - File storage
    - Message queue (if applicable)
    """

    def __init__(self, check_timeout: int = 5):
        """
        Initialize health checker.
        
        Args:
            check_timeout: Timeout for individual checks in seconds
        """
        self.check_timeout = check_timeout
        self.last_checks: Dict[ComponentType, ComponentCheck] = {}
        self.check_history: Dict[str, List[ComponentCheck]] = {}
        self.max_history = 100

    async def check_database(
        self,
        session: Optional[Any] = None,
        query: str = "SELECT 1"
    ) -> ComponentCheck:
        """
        Check database connectivity and responsiveness.
        
        Args:
            session: SQLAlchemy session
            query: Test query to execute
        
        Returns:
            ComponentCheck result
        """
        start_time = datetime.utcnow()
        component_name = "PostgreSQL"
        
        try:
            if not session:
                raise ValueError("Database session not provided")
            
            # Execute test query
            await asyncio.wait_for(
                asyncio.to_thread(lambda: session.execute(query)),
                timeout=self.check_timeout
            )
            
            response_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            check = ComponentCheck(
                component_type=ComponentType.DATABASE,
                component_name=component_name,
                status=ComponentStatus.HEALTHY if response_time < 1000 else ComponentStatus.DEGRADED,
                response_time_ms=response_time,
                last_check_time=start_time,
                additional_info={"query_executed": query}
            )
        except asyncio.TimeoutError:
            check = ComponentCheck(
                component_type=ComponentType.DATABASE,
                component_name=component_name,
                status=ComponentStatus.UNHEALTHY,
                response_time_ms=self.check_timeout * 1000,
                last_check_time=start_time,
                error_message=f"Query timeout after {self.check_timeout}s"
            )
        except Exception as e:
            check = ComponentCheck(
                component_type=ComponentType.DATABASE,
                component_name=component_name,
                status=ComponentStatus.UNHEALTHY,
                response_time_ms=(datetime.utcnow() - start_time).total_seconds() * 1000,
                last_check_time=start_time,
                error_message=str(e)
            )
        
        self._record_check(check)
        return check

    async def check_cache(
        self,
        redis_client: Optional[Any] = None
    ) -> ComponentCheck:
        """
        Check cache (Redis) connectivity.
        
        Args:
            redis_client: Redis client instance
        
        Returns:
            ComponentCheck result
        """
        start_time = datetime.utcnow()
        component_name = "Redis"
        
        try:
            if not redis_client:
                raise ValueError("Redis client not provided")
            
            # Ping cache
            await asyncio.wait_for(
                asyncio.to_thread(redis_client.ping),
                timeout=self.check_timeout
            )
            
            response_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            check = ComponentCheck(
                component_type=ComponentType.CACHE,
                component_name=component_name,
                status=ComponentStatus.HEALTHY if response_time < 500 else ComponentStatus.DEGRADED,
                response_time_ms=response_time,
                last_check_time=start_time
            )
        except asyncio.TimeoutError:
            check = ComponentCheck(
                component_type=ComponentType.CACHE,
                component_name=component_name,
                status=ComponentStatus.UNHEALTHY,
                response_time_ms=self.check_timeout * 1000,
                last_check_time=start_time,
                error_message=f"Ping timeout after {self.check_timeout}s"
            )
        except Exception as e:
            check = ComponentCheck(
                component_type=ComponentType.CACHE,
                component_name=component_name,
                status=ComponentStatus.UNHEALTHY,
                response_time_ms=(datetime.utcnow() - start_time).total_seconds() * 1000,
                last_check_time=start_time,
                error_message=str(e)
            )
        
        self._record_check(check)
        return check

    async def check_external_api(
        self,
        endpoint: str,
        timeout: Optional[int] = None
    ) -> ComponentCheck:
        """
        Check external API endpoint availability.
        
        Args:
            endpoint: API endpoint URL
            timeout: Request timeout in seconds
        
        Returns:
            ComponentCheck result
        """
        start_time = datetime.utcnow()
        component_name = f"External API: {endpoint}"
        
        try:
            import aiohttp
            
            timeout_val = timeout or self.check_timeout
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    endpoint,
                    timeout=aiohttp.ClientTimeout(total=timeout_val)
                ) as response:
                    response_time = (datetime.utcnow() - start_time).total_seconds() * 1000
                    
                    status = ComponentStatus.HEALTHY if response.status < 400 else ComponentStatus.DEGRADED
                    
                    check = ComponentCheck(
                        component_type=ComponentType.EXTERNAL_API,
                        component_name=component_name,
                        status=status,
                        response_time_ms=response_time,
                        last_check_time=start_time,
                        additional_info={"status_code": response.status}
                    )
        except asyncio.TimeoutError:
            check = ComponentCheck(
                component_type=ComponentType.EXTERNAL_API,
                component_name=component_name,
                status=ComponentStatus.UNHEALTHY,
                response_time_ms=timeout_val * 1000 if timeout else self.check_timeout * 1000,
                last_check_time=start_time,
                error_message=f"Request timeout after {timeout_val}s"
            )
        except Exception as e:
            check = ComponentCheck(
                component_type=ComponentType.EXTERNAL_API,
                component_name=component_name,
                status=ComponentStatus.UNHEALTHY,
                response_time_ms=(datetime.utcnow() - start_time).total_seconds() * 1000,
                last_check_time=start_time,
                error_message=str(e)
            )
        
        self._record_check(check)
        return check

    async def check_webhook_delivery(
        self,
        webhook_manager: Optional[Any] = None
    ) -> ComponentCheck:
        """
        Check webhook delivery system health.
        
        Args:
            webhook_manager: Webhook manager instance
        
        Returns:
            ComponentCheck result
        """
        start_time = datetime.utcnow()
        component_name = "Webhook Delivery"
        
        try:
            if not webhook_manager:
                raise ValueError("Webhook manager not provided")
            
            # Get webhook statistics
            stats = webhook_manager.get_statistics()
            
            response_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            # Determine status based on failure rates
            active_webhooks = stats.get("active_subscriptions", 0)
            failed_webhooks = stats.get("failed_subscriptions", 0)
            
            if active_webhooks == 0:
                status = ComponentStatus.UNKNOWN
            elif failed_webhooks / max(active_webhooks, 1) > 0.3:
                status = ComponentStatus.UNHEALTHY
            elif failed_webhooks / max(active_webhooks, 1) > 0.1:
                status = ComponentStatus.DEGRADED
            else:
                status = ComponentStatus.HEALTHY
            
            check = ComponentCheck(
                component_type=ComponentType.WEBHOOK_DELIVERY,
                component_name=component_name,
                status=status,
                response_time_ms=response_time,
                last_check_time=start_time,
                additional_info=stats
            )
        except Exception as e:
            check = ComponentCheck(
                component_type=ComponentType.WEBHOOK_DELIVERY,
                component_name=component_name,
                status=ComponentStatus.UNHEALTHY,
                response_time_ms=(datetime.utcnow() - start_time).total_seconds() * 1000,
                last_check_time=start_time,
                error_message=str(e)
            )
        
        self._record_check(check)
        return check

    async def check_websocket(
        self,
        websocket_handler: Optional[Any] = None
    ) -> ComponentCheck:
        """
        Check WebSocket connection health.
        
        Args:
            websocket_handler: WebSocket handler instance
        
        Returns:
            ComponentCheck result
        """
        start_time = datetime.utcnow()
        component_name = "WebSocket"
        
        try:
            if not websocket_handler:
                raise ValueError("WebSocket handler not provided")
            
            stats = websocket_handler.get_statistics()
            response_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            # Status based on active connections
            active_connections = stats.get("connected_clients", 0)
            status = ComponentStatus.HEALTHY if active_connections >= 0 else ComponentStatus.UNKNOWN
            
            check = ComponentCheck(
                component_type=ComponentType.WEBSOCKET,
                component_name=component_name,
                status=status,
                response_time_ms=response_time,
                last_check_time=start_time,
                additional_info=stats
            )
        except Exception as e:
            check = ComponentCheck(
                component_type=ComponentType.WEBSOCKET,
                component_name=component_name,
                status=ComponentStatus.UNHEALTHY,
                response_time_ms=(datetime.utcnow() - start_time).total_seconds() * 1000,
                last_check_time=start_time,
                error_message=str(e)
            )
        
        self._record_check(check)
        return check

    async def check_file_storage(self, storage_path: str) -> ComponentCheck:
        """
        Check file storage availability.
        
        Args:
            storage_path: Path to storage directory
        
        Returns:
            ComponentCheck result
        """
        start_time = datetime.utcnow()
        component_name = f"File Storage: {storage_path}"
        
        try:
            import os
            import tempfile
            
            # Try to write and read a test file
            await asyncio.to_thread(
                self._test_file_storage,
                storage_path
            )
            
            response_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            check = ComponentCheck(
                component_type=ComponentType.FILE_STORAGE,
                component_name=component_name,
                status=ComponentStatus.HEALTHY,
                response_time_ms=response_time,
                last_check_time=start_time
            )
        except Exception as e:
            check = ComponentCheck(
                component_type=ComponentType.FILE_STORAGE,
                component_name=component_name,
                status=ComponentStatus.UNHEALTHY,
                response_time_ms=(datetime.utcnow() - start_time).total_seconds() * 1000,
                last_check_time=start_time,
                error_message=str(e)
            )
        
        self._record_check(check)
        return check

    def _test_file_storage(self, storage_path: str) -> None:
        """Test file storage by writing and reading a test file."""
        import os
        import tempfile
        
        if not os.path.exists(storage_path):
            raise IOError(f"Storage path does not exist: {storage_path}")
        
        # Try writing to storage
        test_file = os.path.join(storage_path, ".health_check")
        try:
            with open(test_file, "w") as f:
                f.write("health_check")
            
            # Try reading back
            with open(test_file, "r") as f:
                content = f.read()
            
            if content != "health_check":
                raise IOError("Storage read/write mismatch")
            
            os.remove(test_file)
        except Exception as e:
            if os.path.exists(test_file):
                try:
                    os.remove(test_file)
                except:
                    pass
            raise

    def _record_check(self, check: ComponentCheck) -> None:
        """Record a component check."""
        self.last_checks[check.component_type] = check
        
        component_key = f"{check.component_type.value}:{check.component_name}"
        if component_key not in self.check_history:
            self.check_history[component_key] = []
        
        history = self.check_history[component_key]
        history.append(check)
        if len(history) > self.max_history:
            history.pop(0)

    async def check_all(
        self,
        session: Optional[Any] = None,
        redis_client: Optional[Any] = None,
        webhook_manager: Optional[Any] = None,
        websocket_handler: Optional[Any] = None,
        storage_path: Optional[str] = None,
        external_apis: Optional[List[str]] = None
    ) -> SystemHealthStatus:
        """
        Check all components and return overall health status.
        
        Args:
            session: Database session
            redis_client: Redis client
            webhook_manager: Webhook manager instance
            websocket_handler: WebSocket handler instance
            storage_path: File storage path
            external_apis: List of external API endpoints to check
        
        Returns:
            Overall system health status
        """
        start_time = datetime.utcnow()
        checks = []
        
        # Run checks in parallel
        tasks = []
        
        if session:
            tasks.append(self.check_database(session))
        
        if redis_client:
            tasks.append(self.check_cache(redis_client))
        
        if external_apis:
            for api_url in external_apis:
                tasks.append(self.check_external_api(api_url))
        
        if webhook_manager:
            tasks.append(self.check_webhook_delivery(webhook_manager))
        
        if websocket_handler:
            tasks.append(self.check_websocket(websocket_handler))
        
        if storage_path:
            tasks.append(self.check_file_storage(storage_path))
        
        if tasks:
            checks = await asyncio.gather(*tasks, return_exceptions=False)
            checks = [c for c in checks if isinstance(c, ComponentCheck)]
        
        # Calculate overall status
        healthy_count = sum(1 for c in checks if c.status == ComponentStatus.HEALTHY)
        degraded_count = sum(1 for c in checks if c.status == ComponentStatus.DEGRADED)
        unhealthy_count = sum(1 for c in checks if c.status == ComponentStatus.UNHEALTHY)
        
        if unhealthy_count > 0:
            overall_status = ComponentStatus.UNHEALTHY
        elif degraded_count > 0:
            overall_status = ComponentStatus.DEGRADED
        else:
            overall_status = ComponentStatus.HEALTHY if healthy_count > 0 else ComponentStatus.UNKNOWN
        
        response_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        return SystemHealthStatus(
            overall_status=overall_status,
            checks=checks,
            healthy_components=healthy_count,
            degraded_components=degraded_count,
            unhealthy_components=unhealthy_count,
            response_time_ms=response_time
        )

    def get_check_history(
        self,
        component_type: Optional[ComponentType] = None,
        limit: int = 100
    ) -> Dict[str, List[ComponentCheck]]:
        """Get check history for components."""
        if component_type:
            result = {}
            for key, checks in self.check_history.items():
                if key.startswith(component_type.value):
                    result[key] = checks[-limit:]
            return result
        
        return {
            key: checks[-limit:]
            for key, checks in self.check_history.items()
        }


# Global instance
_health_checker: Optional[HealthChecker] = None


def get_health_checker() -> HealthChecker:
    """Get or create global health checker instance."""
    global _health_checker
    if _health_checker is None:
        _health_checker = HealthChecker()
    return _health_checker
