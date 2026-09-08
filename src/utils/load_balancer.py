"""
Load balancing preparation for Si Sebel Bot.
Provides infrastructure for horizontal scaling with shared cache.
"""

import os
import socket
from typing import Optional, Dict, Any
from .logger import Logger


class LoadBalancerConfig:
    """Configuration for load balancing setup."""

    def __init__(
        self,
        instance_id: Optional[str] = None,
        max_instances: int = 1,
        health_check_interval: int = 30,
        logger: Optional[Logger] = None,
    ):
        """
        Initialize load balancer configuration.

        Args:
            instance_id: Unique identifier for this instance
            max_instances: Maximum number of bot instances
            health_check_interval: Health check interval in seconds
            logger: Logger instance
        """
        self.instance_id = instance_id or self._generate_instance_id()
        self.max_instances = max_instances
        self.health_check_interval = health_check_interval
        self.logger = logger or Logger.get_logger("load_balancer")

        self.logger.info(
            f"Load balancer config initialized - Instance ID: {self.instance_id}"
        )

    def _generate_instance_id(self) -> str:
        """
        Generate unique instance ID based on hostname and process ID.

        Returns:
            Unique instance identifier
        """
        hostname = socket.gethostname()
        pid = os.getpid()
        return f"{hostname}-{pid}"

    def get_instance_info(self) -> Dict[str, Any]:
        """
        Get instance information for load balancing.

        Returns:
            Dictionary with instance details
        """
        return {
            "instance_id": self.instance_id,
            "hostname": socket.gethostname(),
            "pid": os.getpid(),
            "max_instances": self.max_instances,
            "health_check_interval": self.health_check_interval,
        }


class HealthChecker:
    """Health checker for bot instances."""

    def __init__(self, instance_id: str, logger: Optional[Logger] = None):
        """
        Initialize health checker.

        Args:
            instance_id: Instance identifier
            logger: Logger instance
        """
        self.instance_id = instance_id
        self.logger = logger or Logger.get_logger("health_checker")
        self.is_healthy = True
        self.last_check = None

    def check_health(self) -> Dict[str, Any]:
        """
        Perform health check.

        Returns:
            Health status dictionary
        """
        from datetime import datetime

        self.last_check = datetime.now().isoformat()

        health_status = {
            "instance_id": self.instance_id,
            "status": "healthy" if self.is_healthy else "unhealthy",
            "timestamp": self.last_check,
            "checks": {
                "bot_running": self.is_healthy,
                "cache_connected": True,  # Will be updated by actual cache check
                "database_connected": True,  # Will be updated by actual DB check
            },
        }

        self.logger.debug(f"Health check: {health_status}")
        return health_status

    def set_healthy(self, healthy: bool) -> None:
        """
        Set health status.

        Args:
            healthy: Health status
        """
        self.is_healthy = healthy
        status = "healthy" if healthy else "unhealthy"
        self.logger.info(f"Instance {self.instance_id} marked as {status}")


class ConnectionPool:
    """
    Connection pool for managing multiple bot instances.
    Prepared for future horizontal scaling.
    """

    def __init__(self, max_connections: int = 10, logger: Optional[Logger] = None):
        """
        Initialize connection pool.

        Args:
            max_connections: Maximum number of connections
            logger: Logger instance
        """
        self.max_connections = max_connections
        self.logger = logger or Logger.get_logger("connection_pool")
        self.active_connections = 0
        self.logger.info(
            f"Connection pool initialized with max {max_connections} connections"
        )

    def acquire_connection(self) -> bool:
        """
        Acquire a connection from the pool.

        Returns:
            True if connection acquired, False otherwise
        """
        if self.active_connections < self.max_connections:
            self.active_connections += 1
            self.logger.debug(
                f"Connection acquired. Active: {self.active_connections}/{self.max_connections}"
            )
            return True
        else:
            self.logger.warning(
                f"Connection pool exhausted. Active: {self.active_connections}/{self.max_connections}"
            )
            return False

    def release_connection(self) -> None:
        """Release a connection back to the pool."""
        if self.active_connections > 0:
            self.active_connections -= 1
            self.logger.debug(
                f"Connection released. Active: {self.active_connections}/{self.max_connections}"
            )

    def get_pool_status(self) -> Dict[str, Any]:
        """
        Get connection pool status.

        Returns:
            Pool status dictionary
        """
        return {
            "max_connections": self.max_connections,
            "active_connections": self.active_connections,
            "available_connections": self.max_connections - self.active_connections,
            "utilization_percent": (
                (self.active_connections / self.max_connections) * 100
                if self.max_connections > 0
                else 0
            ),
        }


class RateLimiter:
    """
    Rate limiter for API calls and message sending.
    Prevents spam and ensures fair usage.
    """

    def __init__(
        self,
        max_requests: int = 100,
        time_window: int = 60,
        logger: Optional[Logger] = None,
    ):
        """
        Initialize rate limiter.

        Args:
            max_requests: Maximum number of requests allowed
            time_window: Time window in seconds
            logger: Logger instance
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.logger = logger or Logger.get_logger("rate_limiter")

        self.requests = []  # Simple implementation - use Redis for distributed
        self.logger.info(
            f"Rate limiter initialized: {max_requests} requests per {time_window}s"
        )

    def is_allowed(self, identifier: str = "default") -> bool:
        """
        Check if request is allowed under rate limit.

        Args:
            identifier: Unique identifier for the requester (e.g., phone number)

        Returns:
            True if request is allowed, False otherwise
        """
        import time

        current_time = time.time()

        # Remove old requests outside time window
        self.requests = [
            req_time
            for req_time in self.requests
            if current_time - req_time < self.time_window
        ]

        if len(self.requests) < self.max_requests:
            self.requests.append(current_time)
            self.logger.debug(
                f"Request allowed for {identifier}. Count: {len(self.requests)}/{self.max_requests}"
            )
            return True
        else:
            self.logger.warning(f"Rate limit exceeded for {identifier}")
            return False

    def get_remaining_requests(self) -> int:
        """
        Get number of remaining requests in current time window.

        Returns:
            Number of remaining requests
        """
        return max(0, self.max_requests - len(self.requests))

    def reset(self) -> None:
        """Reset rate limiter."""
        self.requests.clear()
        self.logger.info("Rate limiter reset")


class LoadBalancerManager:
    """
    Main load balancer manager.
    Coordinates health checking, connection pooling, and rate limiting.
    """

    def __init__(
        self,
        max_instances: int = 1,
        max_connections: int = 10,
        max_requests: int = 100,
        rate_limit_window: int = 60,
        logger: Optional[Logger] = None,
    ):
        """
        Initialize load balancer manager.

        Args:
            max_instances: Maximum number of bot instances
            max_connections: Maximum connections per instance
            max_requests: Maximum requests per time window
            rate_limit_window: Rate limit time window in seconds
            logger: Logger instance
        """
        self.logger = logger or Logger.get_logger("load_balancer_manager")

        # Initialize components
        self.config = LoadBalancerConfig(
            max_instances=max_instances, logger=self.logger
        )
        self.health_checker = HealthChecker(self.config.instance_id, logger=self.logger)
        self.connection_pool = ConnectionPool(max_connections, logger=self.logger)
        self.rate_limiter = RateLimiter(
            max_requests, rate_limit_window, logger=self.logger
        )

        self.logger.info("Load balancer manager initialized")

    def get_status(self) -> Dict[str, Any]:
        """
        Get comprehensive load balancer status.

        Returns:
            Status dictionary with all components
        """
        return {
            "instance": self.config.get_instance_info(),
            "health": self.health_checker.check_health(),
            "connection_pool": self.connection_pool.get_pool_status(),
            "rate_limiter": {
                "max_requests": self.rate_limiter.max_requests,
                "time_window": self.rate_limiter.time_window,
                "remaining_requests": self.rate_limiter.get_remaining_requests(),
            },
        }

    def is_ready_for_request(self, identifier: str = "default") -> bool:
        """
        Check if system is ready to handle a request.

        Args:
            identifier: Request identifier

        Returns:
            True if ready, False otherwise
        """
        # Check health
        if not self.health_checker.is_healthy:
            self.logger.warning("System not healthy, rejecting request")
            return False

        # Check rate limit
        if not self.rate_limiter.is_allowed(identifier):
            self.logger.warning("Rate limit exceeded, rejecting request")
            return False

        # Check connection pool
        if not self.connection_pool.acquire_connection():
            self.logger.warning("Connection pool exhausted, rejecting request")
            return False

        return True

    def release_resources(self) -> None:
        """Release resources after request completion."""
        self.connection_pool.release_connection()


# Global load balancer instance
_load_balancer_instance: Optional[LoadBalancerManager] = None


def get_load_balancer(
    max_instances: int = 1,
    max_connections: int = 10,
    max_requests: int = 100,
    rate_limit_window: int = 60,
    logger: Optional[Logger] = None,
) -> LoadBalancerManager:
    """
    Get or create load balancer manager instance.

    Args:
        max_instances: Maximum number of bot instances
        max_connections: Maximum connections per instance
        max_requests: Maximum requests per time window
        rate_limit_window: Rate limit time window in seconds
        logger: Logger instance

    Returns:
        LoadBalancerManager instance
    """
    global _load_balancer_instance
    if _load_balancer_instance is None:
        _load_balancer_instance = LoadBalancerManager(
            max_instances=max_instances,
            max_connections=max_connections,
            max_requests=max_requests,
            rate_limit_window=rate_limit_window,
            logger=logger,
        )
    return _load_balancer_instance
