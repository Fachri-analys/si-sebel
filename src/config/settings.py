"""
Configuration management for Si Sebel Bot.
Uses pydantic-settings for type-safe configuration management.
"""

from typing import ClassVar

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    DEVELOPMENT_PHONE_HASH_KEY: ClassVar[str] = "development-only-not-for-production"

    # WhatsApp Configuration
    whatsapp_phone_number: str = Field(
        default="",
        description="WhatsApp phone number for the bot (format: 628xxxxxxxxxx)",
    )
    phone_hash_key: str = Field(
        default="", description="Secret key used to pseudonymize phone numbers"
    )

    # Bot Configuration
    bot_name: str = Field(default="Si Sebel", description="Name of the bot")
    bot_response_delay: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Delay in seconds before sending response (to avoid spam detection)",
    )

    # Database Configuration
    database_path: str = Field(
        default="sisebel.db", description="Path to SQLite database file"
    )

    # Logging Configuration
    log_level: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
    )
    log_file: str = Field(default="logs/sisebel.log", description="Path to log file")

    # Environment
    environment: str = Field(
        default="development", description="Environment mode (development, production)"
    )

    # Security Configuration
    security_mode: str = Field(
        default="strict", description="Security mode (strict, permissive)"
    )
    enable_security_logging: bool = Field(
        default=True, description="Enable security event logging"
    )
    enable_audit_logging: bool = Field(default=True, description="Enable audit logging")
    max_message_length: int = Field(
        default=4096, description="Maximum message length (WhatsApp limit)"
    )
    max_log_length: int = Field(default=500, description="Maximum log entry length")

    # Redis Configuration
    redis_host: str = Field(default="localhost", description="Redis server host")
    redis_port: int = Field(default=6379, description="Redis server port")
    redis_db: int = Field(default=0, description="Redis database number")
    redis_password: str = Field(
        default="", description="Redis password (leave empty if no password)"
    )
    cache_ttl: int = Field(default=3600, description="Cache time-to-live in seconds")
    enable_cache: bool = Field(default=True, description="Enable or disable caching")

    # Load Balancing Configuration
    max_instances: int = Field(default=1, description="Maximum number of bot instances")
    max_connections: int = Field(
        default=50, description="Maximum concurrent connections per instance"
    )
    max_requests: int = Field(
        default=100, description="Maximum requests per time window (rate limiting)"
    )
    rate_limit_window: int = Field(
        default=60, description="Rate limit time window in seconds"
    )

    model_config = SettingsConfigDict(
        env_file="config/.env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @model_validator(mode="after")
    def validate_runtime_configuration(self) -> "Settings":
        if self.environment not in {"development", "staging", "production"}:
            raise ValueError("ENVIRONMENT must be development, staging, or production")
        if self.log_level.upper() not in {
            "DEBUG",
            "INFO",
            "WARNING",
            "ERROR",
            "CRITICAL",
        }:
            raise ValueError("LOG_LEVEL is invalid")
        if self.environment == "production":
            missing = [
                name
                for name, value in {
                    "WHATSAPP_PHONE_NUMBER": self.whatsapp_phone_number,
                    "PHONE_HASH_KEY": (
                        self.phone_hash_key
                        if self.phone_hash_key != self.DEVELOPMENT_PHONE_HASH_KEY
                        else ""
                    ),
                }.items()
                if not value
            ]
            if missing:
                raise ValueError(
                    f"Production configuration is missing required values: {', '.join(missing)}"
                )
        return self

    def get_whatsapp_phone_formatted(self) -> str:
        """Get WhatsApp phone number in proper format."""
        if not self.whatsapp_phone_number:
            raise ValueError("WhatsApp phone number not configured")

        # Remove any non-digit characters
        phone = "".join(filter(str.isdigit, self.whatsapp_phone_number))

        # Ensure it starts with country code (62 for Indonesia)
        if phone.startswith("0"):
            phone = "62" + phone[1:]

        return phone


# Global settings instance
settings = Settings()
