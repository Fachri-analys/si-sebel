"""
Security utilities for Si Sebel Bot.
Provides input validation, sanitization, and security checks.
"""

import re
import hashlib
import hmac
import os
from typing import Optional, List, Tuple
from .logger import Logger
from .exceptions import SiSebelException


class SecurityError(SiSebelException):
    """Exception raised for security-related errors."""
    pass


class InputValidator:
    """Input validation and sanitization for security."""

    # Blocked patterns for injection prevention
    BLOCKED_PATTERNS = [
        r"<script",           # Script tags
        r"javascript:",       # JavaScript protocol
        r"onerror=",          # Event handlers
        r"onload=",           # Event handlers
        r"onmouseover=",      # Event handlers
        r"__import__",        # Python import
        r"exec\(",            # Python exec
        r"eval\(",            # Python eval
        r"system\(",          # Python system
        r"subprocess\.",      # Python subprocess
        r"os\.system",        # OS system
        r"shell_exec",        # Shell execution
        r"passthru",          # Shell execution
        r";\s*DROP",          # SQL injection
        r";\s*DELETE",        # SQL injection
        r";\s*INSERT",        # SQL injection
        r";\s*UPDATE",        # SQL injection
        r"UNION\s+SELECT",     # SQL injection
        r"--",                 # SQL comment
        r"/\*",               # SQL comment
        r"\\x00",             # Null byte
        r"\\r\\n",            # CRLF injection
    ]

    # Allowed characters for user input
    ALLOWED_CHARS = set(
        "abcdefghijklmnopqrstuvwxyz"
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        "0123456789"
        " .,?!@#$%&*+-_=()[]{}<>\\/|'\"`~:"
        "\n\t"  # Newline and tab for multi-line messages
    )

    def __init__(self, logger: Optional[Logger] = None):
        """
        Initialize input validator.

        Args:
            logger: Logger instance
        """
        self.logger = logger or Logger.get_logger("input_validator")

    def validate_message(self, message: str) -> Tuple[bool, str]:
        """
        Validate and sanitize user message.

        Args:
            message: User message to validate

        Returns:
            Tuple of (is_valid, sanitized_message or error_message)
        """
        if not message:
            return False, "Empty message"

        # Length check (WhatsApp limit is 4096 chars)
        if len(message) > 4096:
            return False, "Message too long (max 4096 characters)"

        # Check for blocked patterns
        for pattern in self.BLOCKED_PATTERNS:
            if re.search(pattern, message, re.IGNORECASE):
                self.logger.warning(f"Blocked pattern detected: {pattern}")
                return False, "Message contains blocked content"

        # Character validation (with unicode support)
        # Allow most unicode characters, but block control characters except \n\t
        for i, char in enumerate(message):
            code = ord(char)
            # Allow printable chars, newlines, tabs, and most unicode
            # Block control characters except \n (10) and \t (9)
            if code < 32 and code not in (9, 10):
                return False, f"Invalid character at position {i}"

        # Sanitize message
        sanitized = self._sanitize_message(message)

        return True, sanitized

    def _sanitize_message(self, message: str) -> str:
        """
        Sanitize message for safe processing.

        Args:
            message: Message to sanitize

        Returns:
            Sanitized message
        """
        # Remove excessive whitespace
        sanitized = " ".join(message.split())
        
        # Remove null bytes
        sanitized = sanitized.replace("\x00", "")
        
        # Remove potentially dangerous unicode control characters
        sanitized = "".join(char for char in sanitized if ord(char) >= 32 or char in "\n\t")
        
        return sanitized

    def validate_phone_number(self, phone: str) -> Tuple[bool, str]:
        """
        Validate phone number format.

        Args:
            phone: Phone number to validate

        Returns:
            Tuple of (is_valid, formatted_phone or error_message)
        """
        if not phone:
            return False, "Empty phone number"

        # Remove all non-digit characters
        cleaned = "".join(filter(str.isdigit, phone))

        # Validate length (Indonesia numbers: 10-13 digits)
        if len(cleaned) < 10 or len(cleaned) > 15:
            return False, "Invalid phone number length"

        # Ensure starts with country code
        if not cleaned.startswith("62"):
            return False, "Phone number must start with country code (62)"

        return True, cleaned

    def validate_jurusan_name(self, name: str) -> Tuple[bool, str]:
        """
        Validate jurusan name.

        Args:
            name: Jurusan name to validate

        Returns:
            Tuple of (is_valid, sanitized_name or error_message)
        """
        if not name:
            return False, "Empty jurusan name"

        if len(name) > 100:
            return False, "Jurusan name too long (max 100 characters)"

        # Check for blocked patterns
        for pattern in self.BLOCKED_PATTERNS:
            if re.search(pattern, name, re.IGNORECASE):
                return False, "Jurusan name contains blocked content"

        sanitized = name.strip()
        return True, sanitized

    def validate_faq_content(self, question: str, answer: str) -> Tuple[bool, str]:
        """
        Validate FAQ content.

        Args:
            question: FAQ question
            answer: FAQ answer

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not question or not answer:
            return False, "Question and answer cannot be empty"

        if len(question) > 500 or len(answer) > 2000:
            return False, "Question or answer too long"

        # Check both question and answer for blocked patterns
        for content in [question, answer]:
            for pattern in self.BLOCKED_PATTERNS:
                if re.search(pattern, content, re.IGNORECASE):
                    return False, "Content contains blocked patterns"

        return True, ""

    def hash_phone_number(self, phone: str) -> str:
        """
        Pseudonymize a phone number with a secret HMAC key.

        Args:
            phone: Phone number to hash

        Returns:
            Hashed phone number
        """
        from config import settings

        key = (
            os.environ.get("PHONE_HASH_KEY")
            or settings.phone_hash_key
            or settings.DEVELOPMENT_PHONE_HASH_KEY
        )
        if not key:
            raise SecurityError("PHONE_HASH_KEY must be configured before hashing phone numbers")
        return hmac.new(
            key.encode("utf-8"),
            phone.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()


class OutputEncoder:
    """Output encoding for injection prevention."""

    @staticmethod
    def encode_for_whatsapp(text: str) -> str:
        """
        Encode text for safe WhatsApp sending.

        Args:
            text: Text to encode

        Returns:
            Encoded text
        """
        # WhatsApp supports markdown, so we need to be careful
        # Escape special markdown characters if needed
        # For now, just sanitize
        return text.strip()

    @staticmethod
    def encode_for_log(text: str) -> str:
        """
        Encode text for safe logging.

        Args:
            text: Text to encode

        Returns:
            Encoded text
        """
        # Remove potential log injection sequences
        text = text.replace("\r", "\\r")
        text = text.replace("\n", "\\n")
        text = text.replace("\x00", "\\x00")
        
        # Truncate if too long
        if len(text) > 500:
            text = text[:500] + "... [truncated]"
        
        return text

    @staticmethod
    def encode_for_database(text: str) -> str:
        """
        Encode text for safe database storage.

        Args:
            text: Text to encode

        Returns:
            Encoded text
        """
        # Truncate if too long
        if len(text) > 10000:
            text = text[:10000] + "... [truncated]"
        
        return text.strip()


class SecurityLogger:
    """Security event logging."""

    SECURITY_EVENTS = [
        "injection_attempt",
        "blocked_pattern",
        "invalid_input",
        "authentication_failure",
        "authorization_failure",
        "data_access_attempt",
        "configuration_change",
        "suspicious_activity"
    ]

    def __init__(self, logger: Optional[Logger] = None):
        """
        Initialize security logger.

        Args:
            logger: Logger instance
        """
        self.logger = logger or Logger.get_logger("security_logger")

    def log_security_event(
        self,
        event_type: str,
        details: dict,
        severity: str = "WARNING"
    ) -> None:
        """
        Log security event.

        Args:
            event_type: Type of security event
            details: Event details
            severity: Event severity (INFO, WARNING, ERROR, CRITICAL)
        """
        if event_type not in self.SECURITY_EVENTS:
            self.logger.warning(f"Unknown security event type: {event_type}")
        
        log_message = f"[SECURITY] {event_type}: {details}"
        
        if severity == "CRITICAL":
            self.logger.critical(log_message)
        elif severity == "ERROR":
            self.logger.error(log_message)
        elif severity == "WARNING":
            self.logger.warning(log_message)
        else:
            self.logger.info(log_message)

    def log_injection_attempt(self, details: dict) -> None:
        """Log injection attempt."""
        self.log_security_event("injection_attempt", details, "CRITICAL")

    def log_blocked_pattern(self, pattern: str, context: str) -> None:
        """Log blocked pattern detection."""
        self.log_security_event(
            "blocked_pattern",
            {"pattern": pattern, "context": context},
            "WARNING"
        )

    def log_invalid_input(self, input_data: str, reason: str) -> None:
        """Log invalid input."""
        self.log_security_event(
            "invalid_input",
            {"input_length": len(input_data), "reason": reason},
            "WARNING"
        )


class RateLimiterSecurity:
    """Security-focused rate limiting with distributed support."""

    def __init__(
        self,
        max_requests: int = 100,
        time_window: int = 60,
        block_duration: int = 300,
        logger: Optional[Logger] = None
    ):
        """
        Initialize security rate limiter.

        Args:
            max_requests: Maximum requests per time window
            time_window: Time window in seconds
            block_duration: Block duration in seconds after limit exceeded
            logger: Logger instance
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.block_duration = block_duration
        self.logger = logger or Logger.get_logger("rate_limiter_security")
        
        self.requests = {}  # {identifier: [(timestamp, blocked)]}
        self.blocked_until = {}  # {identifier: blocked_until_timestamp}

    def is_allowed(self, identifier: str) -> Tuple[bool, Optional[str]]:
        """
        Check if request is allowed with security logging.

        Args:
            identifier: Request identifier (e.g., phone number)

        Returns:
            Tuple of (is_allowed, block_reason)
        """
        import time
        current_time = time.time()

        # Check if blocked
        if identifier in self.blocked_until:
            if current_time < self.blocked_until[identifier]:
                remaining = int(self.blocked_until[identifier] - current_time)
                return False, f"Rate limit exceeded. Try again in {remaining}s"
            else:
                # Block expired
                del self.blocked_until[identifier]

        # Clean old requests
        if identifier in self.requests:
            self.requests[identifier] = [
                (ts, blocked) for ts, blocked in self.requests[identifier]
                if current_time - ts < self.time_window
            ]
        else:
            self.requests[identifier] = []

        # Check rate limit
        recent_requests = [ts for ts, blocked in self.requests[identifier] if not blocked]
        
        if len(recent_requests) >= self.max_requests:
            # Block the identifier
            self.blocked_until[identifier] = current_time + self.block_duration
            self.logger.warning(
                "Rate limit exceeded for sender, blocked for %ss",
                self.block_duration,
            )
            return False, f"Rate limit exceeded. Blocked for {self.block_duration}s"

        # Record request
        self.requests[identifier].append((current_time, False))
        return True, None

    def block_identifier(self, identifier: str, reason: str) -> None:
        """
        Manually block an identifier.

        Args:
            identifier: Identifier to block
            reason: Reason for blocking
        """
        import time
        self.blocked_until[identifier] = time.time() + self.block_duration
        self.logger.warning(f"Manually blocked {identifier}: {reason}")

    def unblock_identifier(self, identifier: str) -> None:
        """
        Unblock an identifier.

        Args:
            identifier: Identifier to unblock
        """
        if identifier in self.blocked_until:
            del self.blocked_until[identifier]
            self.logger.info(f"Unblocked {identifier}")


# Global security instances
_input_validator: Optional[InputValidator] = None
_output_encoder: Optional[OutputEncoder] = None
_security_logger: Optional[SecurityLogger] = None
_rate_limiter_security: Optional[RateLimiterSecurity] = None


def get_input_validator(logger: Optional[Logger] = None) -> InputValidator:
    """Get or create input validator instance."""
    global _input_validator
    if _input_validator is None:
        _input_validator = InputValidator(logger)
    return _input_validator


def get_output_encoder() -> OutputEncoder:
    """Get or create output encoder instance."""
    global _output_encoder
    if _output_encoder is None:
        _output_encoder = OutputEncoder()
    return _output_encoder


def get_security_logger(logger: Optional[Logger] = None) -> SecurityLogger:
    """Get or create security logger instance."""
    global _security_logger
    if _security_logger is None:
        _security_logger = SecurityLogger(logger)
    return _security_logger


def get_rate_limiter_security(
    max_requests: int = 100,
    time_window: int = 60,
    block_duration: int = 300,
    logger: Optional[Logger] = None
) -> RateLimiterSecurity:
    """Get or create security rate limiter instance."""
    global _rate_limiter_security
    if _rate_limiter_security is None:
        _rate_limiter_security = RateLimiterSecurity(
            max_requests=max_requests,
            time_window=time_window,
            block_duration=block_duration,
            logger=logger
        )
    return _rate_limiter_security