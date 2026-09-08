"""Utility modules for Si Sebel Bot."""

from .logger import Logger, setup_application_logger
from .exceptions import (
    SiSebelException,
    WhatsAppConnectionError,
    DatabaseError,
    MessageProcessingError,
    KnowledgeBaseError,
    ConfigurationError,
)
from .cache import CacheManager, CacheKey, get_cache_manager, CacheError
from .load_balancer import (
    LoadBalancerConfig,
    HealthChecker,
    ConnectionPool,
    RateLimiter,
    LoadBalancerManager,
    get_load_balancer,
)
from .security import (
    InputValidator,
    OutputEncoder,
    SecurityLogger,
    RateLimiterSecurity,
    SecurityError,
    get_input_validator,
    get_output_encoder,
    get_security_logger,
    get_rate_limiter_security,
)
from .security_config import (
    SecurityConfig,
    SecurityBestPractices,
    SecurityHeaders,
    get_security_best_practices,
)
from .auth import (
    AuthenticationManager,
    AdminUser,
    SessionManager,
    PasswordManager,
    AuthenticationError,
    AuthorizationError,
    get_authentication_manager,
)

__all__ = [
    "Logger",
    "setup_application_logger",
    "SiSebelException",
    "WhatsAppConnectionError",
    "DatabaseError",
    "MessageProcessingError",
    "KnowledgeBaseError",
    "ConfigurationError",
    "CacheManager",
    "CacheKey",
    "get_cache_manager",
    "CacheError",
    "LoadBalancerConfig",
    "HealthChecker",
    "ConnectionPool",
    "RateLimiter",
    "LoadBalancerManager",
    "get_load_balancer",
    "InputValidator",
    "OutputEncoder",
    "SecurityLogger",
    "RateLimiterSecurity",
    "SecurityError",
    "get_input_validator",
    "get_output_encoder",
    "get_security_logger",
    "get_rate_limiter_security",
    "SecurityConfig",
    "SecurityBestPractices",
    "SecurityHeaders",
    "get_security_best_practices",
    "AuthenticationManager",
    "AdminUser",
    "SessionManager",
    "PasswordManager",
    "AuthenticationError",
    "AuthorizationError",
    "get_authentication_manager",
]
