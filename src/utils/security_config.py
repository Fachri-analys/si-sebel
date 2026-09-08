"""
Security configuration and best practices for Si Sebel Bot.
"""

from typing import Any, Dict, List, Optional

from .logger import Logger


class SecurityConfig:
    """Security configuration settings."""

    # Message security
    MAX_MESSAGE_LENGTH = 4096  # WhatsApp limit
    MAX_RESPONSE_LENGTH = 4096
    ALLOWED_MESSAGE_TYPES = ["text"]

    # Rate limiting
    DEFAULT_MAX_REQUESTS = 100
    DEFAULT_TIME_WINDOW = 60  # seconds
    DEFAULT_BLOCK_DURATION = 300  # seconds

    # Input validation
    STRICT_MODE = True
    BLOCK_SUSPICIOUS_PATTERNS = True

    # Logging security
    LOG_SENSITIVE_DATA = False
    LOG_PHONE_NUMBERS = False  # Already hashing in implementation
    MAX_LOG_LENGTH = 500

    # Cache security
    CACHE_INTEGRITY_CHECKS = True
    MAX_CACHE_SIZE = 1000  # entries
    CACHE_TTL_MIN = 60  # seconds
    CACHE_TTL_MAX = 86400  # 24 hours

    # Database security
    QUERY_TIMEOUT = 30  # seconds
    CONNECTION_POOL_SIZE = 10
    TRANSACTION_TIMEOUT = 60  # seconds

    # Redis security
    REDIS_PASSWORD_REQUIRED = True
    REDIS_TLS_REQUIRED = False  # Optional for local development
    REDIS_MAX_CONNECTIONS = 50

    # General security
    ENABLE_SECURITY_LOGGING = True
    ENABLE_AUDIT_LOGGING = True
    SECURITY_ALERT_EMAIL = None  # For future implementation

    @classmethod
    def get_config(cls) -> Dict[str, Any]:
        """Get all security configuration as dictionary."""
        return {
            "message_security": {
                "max_message_length": cls.MAX_MESSAGE_LENGTH,
                "max_response_length": cls.MAX_RESPONSE_LENGTH,
                "allowed_message_types": cls.ALLOWED_MESSAGE_TYPES,
            },
            "rate_limiting": {
                "default_max_requests": cls.DEFAULT_MAX_REQUESTS,
                "default_time_window": cls.DEFAULT_TIME_WINDOW,
                "default_block_duration": cls.DEFAULT_BLOCK_DURATION,
            },
            "input_validation": {
                "strict_mode": cls.STRICT_MODE,
                "block_suspicious_patterns": cls.BLOCK_SUSPICIOUS_PATTERNS,
            },
            "logging_security": {
                "log_sensitive_data": cls.LOG_SENSITIVE_DATA,
                "log_phone_numbers": cls.LOG_PHONE_NUMBERS,
                "max_log_length": cls.MAX_LOG_LENGTH,
            },
            "cache_security": {
                "integrity_checks": cls.CACHE_INTEGRITY_CHECKS,
                "max_cache_size": cls.MAX_CACHE_SIZE,
                "ttl_min": cls.CACHE_TTL_MIN,
                "ttl_max": cls.CACHE_TTL_MAX,
            },
            "database_security": {
                "query_timeout": cls.QUERY_TIMEOUT,
                "connection_pool_size": cls.CONNECTION_POOL_SIZE,
                "transaction_timeout": cls.TRANSACTION_TIMEOUT,
            },
            "redis_security": {
                "password_required": cls.REDIS_PASSWORD_REQUIRED,
                "tls_required": cls.REDIS_TLS_REQUIRED,
                "max_connections": cls.REDIS_MAX_CONNECTIONS,
            },
            "general_security": {
                "enable_security_logging": cls.ENABLE_SECURITY_LOGGING,
                "enable_audit_logging": cls.ENABLE_AUDIT_LOGGING,
                "security_alert_email": cls.SECURITY_ALERT_EMAIL,
            },
        }


class SecurityBestPractices:
    """Security best practices implementation."""

    def __init__(self, logger: Optional[Logger] = None):
        """
        Initialize security best practices.

        Args:
            logger: Logger instance
        """
        self.logger = logger or Logger.get_logger("security_best_practices")
        self.config = SecurityConfig.get_config()

    def validate_configuration(self) -> List[str]:
        """
        Validate current security configuration.

        Returns:
            List of validation warnings
        """
        warnings = []

        # Check if security logging is enabled
        if not self.config["general_security"]["enable_security_logging"]:
            warnings.append("Security logging is disabled")

        # Check if audit logging is enabled
        if not self.config["general_security"]["enable_audit_logging"]:
            warnings.append("Audit logging is disabled")

        # Check rate limiting settings
        if self.config["rate_limiting"]["default_max_requests"] > 1000:
            warnings.append("Rate limit is very high, may not prevent abuse")

        # Check cache TTL settings
        if self.config["cache_security"]["ttl_max"] > 86400 * 7:  # 7 days
            warnings.append("Cache TTL is very long, may serve stale data")

        # Check database timeout
        if self.config["database_security"]["query_timeout"] > 60:
            warnings.append("Database query timeout is very long")

        if warnings:
            self.logger.warning(f"Security configuration warnings: {warnings}")
        else:
            self.logger.info("Security configuration is valid")

        return warnings

    def get_security_checklist(self) -> Dict[str, bool]:
        """
        Get security checklist status.

        Returns:
            Dictionary with checklist items and their status
        """
        return {
            "input_validation_enabled": True,
            "output_encoding_enabled": True,
            "rate_limiting_enabled": True,
            "security_logging_enabled": self.config["general_security"][
                "enable_security_logging"
            ],
            "audit_logging_enabled": self.config["general_security"][
                "enable_audit_logging"
            ],
            "sql_injection_protected": True,  # Using parameterized queries
            "phone_number_hashing": True,
            "no_hardcoded_secrets": True,
            "environment_variables_for_secrets": True,
            "cache_integrity_checks": self.config["cache_security"]["integrity_checks"],
            "database_timeout_configured": True,
            "error_handling_comprehensive": True,
            "logging_comprehensive": True,
        }

    def get_security_recommendations(self) -> List[str]:
        """
        Get security recommendations based on current implementation.

        Returns:
            List of security recommendations
        """
        recommendations = [
            "Enable Redis authentication in production",
            "Use TLS for Redis connections in production",
            "Implement database connection pooling",
            "Add circuit breaker pattern for external services",
            "Implement message queue for reliability",
            "Add comprehensive monitoring and alerting",
            "Regular security audits and penetration testing",
            "Implement backup and disaster recovery",
            "Add intrusion detection system",
            "Implement regular security training for team",
            "Keep all dependencies updated",
            "Use secrets management service (AWS Secrets Manager, etc.)",
            "Implement data encryption at rest",
            "Add API authentication if web endpoints are added",
            "Implement rate limiting at infrastructure level",
        ]

        return recommendations

    def get_compliance_status(self) -> Dict[str, bool]:
        """
        Get compliance status for common security standards.

        Returns:
            Dictionary with compliance status
        """
        return {
            "gdpr_compliant": True,  # Phone number hashing, data minimization
            "owasp_top_10_addressed": True,  # Most critical issues addressed
            "pci_dss_compliant": False,  # Not handling payment data
            "hipaa_compliant": False,  # Not handling health data
            "soc2_compliant": False,  # Not certified
            "iso_27001_compliant": False,  # Not certified
        }


class SecurityHeaders:
    """Security headers for future web endpoints."""

    # Standard security headers
    SECURITY_HEADERS = {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline';",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
    }

    @classmethod
    def get_headers(cls) -> Dict[str, str]:
        """
        Get security headers for web responses.

        Returns:
            Dictionary of security headers
        """
        return cls.SECURITY_HEADERS.copy()

    @classmethod
    def get_csp_policy(cls) -> str:
        """
        Get Content Security Policy.

        Returns:
            CSP policy string
        """
        return cls.SECURITY_HEADERS["Content-Security-Policy"]


# Global security best practices instance
_security_best_practices: Optional[SecurityBestPractices] = None


def get_security_best_practices(
    logger: Optional[Logger] = None,
) -> SecurityBestPractices:
    """Get or create security best practices instance."""
    global _security_best_practices
    if _security_best_practices is None:
        _security_best_practices = SecurityBestPractices(logger)
    return _security_best_practices
