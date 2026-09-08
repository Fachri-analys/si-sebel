"""Custom exceptions for Si Sebel Bot."""


class SiSebelException(Exception):
    """Base exception for Si Sebel Bot."""

    pass


class WhatsAppConnectionError(SiSebelException):
    """Exception raised when WhatsApp connection fails."""

    pass


class DatabaseError(SiSebelException):
    """Exception raised when database operation fails."""

    pass


class MessageProcessingError(SiSebelException):
    """Exception raised when message processing fails."""

    pass


class KnowledgeBaseError(SiSebelException):
    """Exception raised when knowledge base operation fails."""

    pass


class ConfigurationError(SiSebelException):
    """Exception raised when configuration is invalid."""

    pass
