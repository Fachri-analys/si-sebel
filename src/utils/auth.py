"""
Authentication and authorization system for Si Sebel Bot.
Provides secure access control for administrative functions.
"""

import hashlib
import hmac
import secrets
import time
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta

from .logger import Logger
from .exceptions import SiSebelException


class AuthenticationError(SiSebelException):
    """Exception raised for authentication errors."""

    pass


class AuthorizationError(SiSebelException):
    """Exception raised for authorization errors."""

    pass


class PasswordManager:
    """Password management with secure hashing."""

    @staticmethod
    def hash_password(password: str, salt: Optional[str] = None) -> tuple:
        """
        Hash password using PBKDF2.

        Args:
            password: Password to hash
            salt: Salt for hashing (generated if not provided)

        Returns:
            Tuple of (hashed_password, salt)
        """
        if salt is None:
            salt = secrets.token_hex(16)

        # Use PBKDF2 with SHA-256
        hashed = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            100000,  # iterations
        ).hex()

        return hashed, salt

    @staticmethod
    def verify_password(password: str, hashed_password: str, salt: str) -> bool:
        """
        Verify password against hash.

        Args:
            password: Password to verify
            hashed_password: Stored hash
            salt: Salt used for hashing

        Returns:
            True if password matches, False otherwise
        """
        new_hash = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000
        ).hex()

        return hmac.compare_digest(new_hash, hashed_password)


class AdminUser:
    """Admin user model."""

    def __init__(
        self,
        username: str,
        password_hash: str,
        salt: str,
        role: str = "admin",
        created_at: Optional[str] = None,
        last_login: Optional[str] = None,
        is_active: bool = True,
    ):
        """
        Initialize admin user.

        Args:
            username: Username
            password_hash: Hashed password
            salt: Salt used for hashing
            role: User role
            created_at: Creation timestamp
            last_login: Last login timestamp
            is_active: Whether user is active
        """
        self.username = username
        self.password_hash = password_hash
        self.salt = salt
        self.role = role
        self.created_at = created_at or datetime.now().isoformat()
        self.last_login = last_login
        self.is_active = is_active

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary (without sensitive data)."""
        return {
            "username": self.username,
            "role": self.role,
            "created_at": self.created_at,
            "last_login": self.last_login,
            "is_active": self.is_active,
        }


class SessionManager:
    """Session management for admin users."""

    def __init__(self, session_timeout: int = 3600, logger: Optional[Logger] = None):
        """
        Initialize session manager.

        Args:
            session_timeout: Session timeout in seconds
            logger: Logger instance
        """
        self.session_timeout = session_timeout
        self.logger = logger or Logger.get_logger("session_manager")
        self.sessions: Dict[str, Dict[str, Any]] = {}

    def create_session(self, username: str) -> str:
        """
        Create new session for user.

        Args:
            username: Username

        Returns:
            Session token
        """
        session_token = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(seconds=self.session_timeout)

        self.sessions[session_token] = {
            "username": username,
            "created_at": datetime.now().isoformat(),
            "expires_at": expires_at.isoformat(),
            "last_activity": datetime.now().isoformat(),
        }

        self.logger.info(f"Session created for {username}: {session_token[:8]}...")
        return session_token

    def validate_session(self, session_token: str) -> Optional[str]:
        """
        Validate session and return username if valid.

        Args:
            session_token: Session token

        Returns:
            Username if valid, None otherwise
        """
        if session_token not in self.sessions:
            return None

        session = self.sessions[session_token]

        # Check if expired
        expires_at = datetime.fromisoformat(session["expires_at"])
        if datetime.now() > expires_at:
            del self.sessions[session_token]
            self.logger.warning(f"Session expired: {session_token[:8]}...")
            return None

        # Update last activity
        session["last_activity"] = datetime.now().isoformat()

        return session["username"]

    def revoke_session(self, session_token: str) -> bool:
        """
        Revoke session.

        Args:
            session_token: Session token

        Returns:
            True if revoked, False otherwise
        """
        if session_token in self.sessions:
            username = self.sessions[session_token]["username"]
            del self.sessions[session_token]
            self.logger.info(f"Session revoked for {username}: {session_token[:8]}...")
            return True
        return False

    def revoke_all_sessions(self, username: str) -> int:
        """
        Revoke all sessions for a user.

        Args:
            username: Username

        Returns:
            Number of sessions revoked
        """
        count = 0
        to_remove = []

        for token, session in self.sessions.items():
            if session["username"] == username:
                to_remove.append(token)

        for token in to_remove:
            del self.sessions[token]
            count += 1

        if count > 0:
            self.logger.info(f"Revoked {count} sessions for {username}")

        return count

    def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions."""
        count = 0
        to_remove = []

        for token, session in self.sessions.items():
            expires_at = datetime.fromisoformat(session["expires_at"])
            if datetime.now() > expires_at:
                to_remove.append(token)

        for token in to_remove:
            del self.sessions[token]
            count += 1

        if count > 0:
            self.logger.info(f"Cleaned up {count} expired sessions")

        return count


class AuthenticationManager:
    """Main authentication and authorization manager."""

    def __init__(
        self,
        session_timeout: int = 3600,
        max_failed_attempts: int = 5,
        lockout_duration: int = 900,
        logger: Optional[Logger] = None,
    ):
        """
        Initialize authentication manager.

        Args:
            session_timeout: Session timeout in seconds
            max_failed_attempts: Max failed login attempts
            lockout_duration: Lockout duration in seconds
            logger: Logger instance
        """
        self.session_timeout = session_timeout
        self.max_failed_attempts = max_failed_attempts
        self.lockout_duration = lockout_duration
        self.logger = logger or Logger.get_logger("auth_manager")

        self.admin_users: Dict[str, AdminUser] = {}
        self.session_manager = SessionManager(session_timeout, logger)
        self.failed_attempts: Dict[str, int] = {}
        self.locked_until: Dict[str, str] = {}

    def create_admin_user(
        self, username: str, password: str, role: str = "admin"
    ) -> bool:
        """
        Create admin user.

        Args:
            username: Username
            password: Password
            role: User role

        Returns:
            True if successful, False otherwise
        """
        if username in self.admin_users:
            self.logger.warning(f"Admin user {username} already exists")
            return False

        # Validate password strength
        if len(password) < 8:
            self.logger.error("Password must be at least 8 characters")
            return False

        # Hash password
        password_hash, salt = PasswordManager.hash_password(password)

        # Create user
        self.admin_users[username] = AdminUser(
            username=username, password_hash=password_hash, salt=salt, role=role
        )

        self.logger.info(f"Admin user created: {username}")
        return True

    def authenticate(self, username: str, password: str) -> Optional[str]:
        """
        Authenticate user and return session token.

        Args:
            username: Username
            password: Password

        Returns:
            Session token if successful, None otherwise
        """
        # Check if user exists
        if username not in self.admin_users:
            self.logger.warning(f"Authentication failed: User {username} not found")
            return None

        user = self.admin_users[username]

        # Check if user is active
        if not user.is_active:
            self.logger.warning(f"Authentication failed: User {username} is inactive")
            return None

        # Check if locked
        if username in self.locked_until:
            locked_until = datetime.fromisoformat(self.locked_until[username])
            if datetime.now() < locked_until:
                remaining = int((locked_until - datetime.now()).total_seconds())
                self.logger.warning(f"Account {username} locked for {remaining}s")
                return None
            else:
                del self.locked_until[username]
                self.failed_attempts[username] = 0

        # Verify password
        if not PasswordManager.verify_password(password, user.password_hash, user.salt):
            # Increment failed attempts
            self.failed_attempts[username] = self.failed_attempts.get(username, 0) + 1

            self.logger.warning(
                f"Authentication failed for {username} (attempt {self.failed_attempts[username]}/{self.max_failed_attempts})"
            )

            # Lock if max attempts reached
            if self.failed_attempts[username] >= self.max_failed_attempts:
                lock_until = datetime.now() + timedelta(seconds=self.lockout_duration)
                self.locked_until[username] = lock_until.isoformat()
                self.logger.warning(
                    f"Account {username} locked for {self.lockout_duration}s"
                )

            return None

        # Reset failed attempts on success
        self.failed_attempts[username] = 0

        # Update last login
        user.last_login = datetime.now().isoformat()

        # Create session
        session_token = self.session_manager.create_session(username)

        self.logger.info(f"Authentication successful for {username}")
        return session_token

    def logout(self, session_token: str) -> bool:
        """
        Logout user by revoking session.

        Args:
            session_token: Session token

        Returns:
            True if successful, False otherwise
        """
        return self.session_manager.revoke_session(session_token)

    def authorize(self, session_token: str, required_role: str = "admin") -> bool:
        """
        Authorize user based on session token and required role.

        Args:
            session_token: Session token
            required_role: Required role for authorization

        Returns:
            True if authorized, False otherwise
        """
        username = self.session_manager.validate_session(session_token)

        if username is None:
            return False

        if username not in self.admin_users:
            return False

        user = self.admin_users[username]

        # Check role
        if required_role and user.role != required_role:
            self.logger.warning(
                f"Authorization failed: {username} does not have required role {required_role}"
            )
            return False

        # Check if active
        if not user.is_active:
            self.logger.warning(f"Authorization failed: {username} is inactive")
            return False

        return True

    def get_user_info(self, session_token: str) -> Optional[Dict[str, Any]]:
        """
        Get user information from session token.

        Args:
            session_token: Session token

        Returns:
            User information or None
        """
        username = self.session_manager.validate_session(session_token)

        if username is None or username not in self.admin_users:
            return None

        return self.admin_users[username].to_dict()

    def cleanup(self) -> None:
        """Clean up expired sessions."""
        count = self.session_manager.cleanup_expired_sessions()
        if count > 0:
            self.logger.info(f"Session cleanup: {count} expired sessions removed")


# Global authentication manager instance
_auth_manager: Optional[AuthenticationManager] = None


def get_authentication_manager(
    session_timeout: int = 3600,
    max_failed_attempts: int = 5,
    lockout_duration: int = 900,
    logger: Optional[Logger] = None,
) -> AuthenticationManager:
    """
    Get or create authentication manager instance.

    Args:
        session_timeout: Session timeout in seconds
        max_failed_attempts: Max failed login attempts
        lockout_duration: Lockout duration in seconds
        logger: Logger instance

    Returns:
        AuthenticationManager instance
    """
    global _auth_manager
    if _auth_manager is None:
        _auth_manager = AuthenticationManager(
            session_timeout=session_timeout,
            max_failed_attempts=max_failed_attempts,
            lockout_duration=lockout_duration,
            logger=logger,
        )
    return _auth_manager
