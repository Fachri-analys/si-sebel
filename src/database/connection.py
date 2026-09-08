"""
Database connection and initialization for Si Sebel Bot.
Handles SQLite database connection and table creation with retry logic.
"""

import sqlite3
import time
import os
from pathlib import Path
from typing import Optional, List, Dict, Any
from contextlib import contextmanager


class DatabaseConnection:
    """Database connection manager for SQLite with retry logic."""

    def __init__(
        self,
        db_path: str,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        connection_timeout: int = 30,
    ):
        """
        Initialize database connection with retry logic.

        Args:
            db_path: Path to SQLite database file
            max_retries: Maximum number of connection retries
            retry_delay: Initial delay between retries in seconds
            connection_timeout: Connection timeout in seconds
        """
        self.db_path = Path(db_path)
        # Create parent directory if it doesn't exist
        if self.db_path.parent != Path("."):
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.connection: Optional[sqlite3.Connection] = None
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.connection_timeout = connection_timeout

    def connect(self) -> sqlite3.Connection:
        """
        Establish database connection with retry logic.

        Returns:
            SQLite connection object

        Raises:
            Exception: If connection fails after all retries
        """
        for attempt in range(self.max_retries):
            try:
                if self.connection is None:
                    self.connection = sqlite3.connect(
                        str(self.db_path),
                        check_same_thread=False,
                        timeout=self.connection_timeout,
                    )
                    # Enable foreign keys
                    self.connection.execute("PRAGMA foreign_keys = ON")
                    # Set row factory to return dictionaries
                    self.connection.row_factory = sqlite3.Row
                    # Set busy timeout for concurrent access
                    self.connection.execute("PRAGMA busy_timeout = 5000")
                    print(f"Database connection established: {self.db_path}")
                    return self.connection
                return self.connection
            except sqlite3.Error as e:
                if attempt < self.max_retries - 1:
                    wait_time = self.retry_delay * (2**attempt)  # Exponential backoff
                    print(
                        f"Connection attempt {attempt + 1} failed, retrying in {wait_time}s..."
                    )
                    time.sleep(wait_time)
                else:
                    raise Exception(
                        f"Failed to connect to database after {self.max_retries} attempts: {e}"
                    )
        return self.connection

    def close(self) -> None:
        """Close database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None

    def initialize_database(self) -> None:
        """Create all tables and run migrations on the database."""
        from .migration import run_migrations

        run_migrations(self)
        print(f"Database initialized and migrated successfully at {self.db_path}")

    @contextmanager
    def get_cursor(self):
        """
        Context manager for database cursor.

        Yields:
            SQLite cursor object
        """
        connection = self.connect()
        cursor = connection.cursor()
        try:
            yield cursor
            connection.commit()
        except Exception as e:
            connection.rollback()
            raise e
        finally:
            cursor.close()

    def execute_query(
        self,
        query: str,
        params: Optional[tuple] = None,
        fetch: bool = False,
        fetch_all: bool = False,
        retry_on_error: bool = True,
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Execute a SQL query with retry logic.

        Args:
            query: SQL query string
            params: Query parameters
            fetch: Whether to fetch results
            fetch_all: Whether to fetch all results (if True) or one (if False)
            retry_on_error: Whether to retry on database errors

        Returns:
            Query results if fetch or fetch_all is True, None otherwise
        """
        if fetch_all:
            fetch = True

        max_attempts = self.max_retries if retry_on_error else 1

        for attempt in range(max_attempts):
            try:
                with self.get_cursor() as cursor:
                    if params:
                        cursor.execute(query, params)
                    else:
                        cursor.execute(query)

                    if fetch:
                        if fetch_all:
                            rows = cursor.fetchall()
                            return [dict(row) for row in rows]
                        else:
                            row = cursor.fetchone()
                            return dict(row) if row else None
                    return None

            except sqlite3.Error as e:
                if attempt < max_attempts - 1:
                    wait_time = self.retry_delay * (2**attempt)
                    print(
                        f"Query attempt {attempt + 1} failed: {e}, retrying in {wait_time}s..."
                    )
                    time.sleep(wait_time)
                else:
                    raise Exception(f"Query failed after {max_attempts} attempts: {e}")

    def execute_script(self, script: str) -> None:
        """
        Execute a SQL script (multiple statements).

        Args:
            script: SQL script string
        """
        with self.get_cursor() as cursor:
            cursor.executescript(script)

    def table_exists(self, table_name: str) -> bool:
        """
        Check if a table exists in the database.

        Args:
            table_name: Name of the table to check

        Returns:
            True if table exists, False otherwise
        """
        query = """
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name=?
        """
        result = self.execute_query(query, (table_name,), fetch=True)
        return result is not None

    def get_table_info(self, table_name: str) -> List[Dict[str, Any]]:
        """
        Get information about a table's columns.

        Args:
            table_name: Name of the table

        Returns:
            List of column information dictionaries
        """
        query = f"PRAGMA table_info({table_name})"
        return self.execute_query(query, fetch_all=True) or []

    def backup_database(self, backup_path: str) -> None:
        """
        Create a backup of the database.

        Args:
            backup_path: Path for the backup file
        """
        backup_file = Path(backup_path)
        backup_file.parent.mkdir(parents=True, exist_ok=True)

        # Backup using SQLite's backup API
        source = self.connect()
        temporary_path = backup_file.with_suffix(backup_file.suffix + ".tmp")
        dest = sqlite3.connect(str(temporary_path))

        try:
            source.backup(dest)
            integrity = dest.execute("PRAGMA integrity_check").fetchone()
            if not integrity or integrity[0] != "ok":
                raise sqlite3.DatabaseError("Backup integrity check failed")
            dest.close()
            os.replace(temporary_path, backup_file)
            print(f"Database backed up successfully to {backup_file}")
        finally:
            if dest:
                dest.close()
            if temporary_path.exists():
                temporary_path.unlink()

    def health_check(self) -> bool:
        """Return whether SQLite is reachable and the migration table exists."""
        try:
            result = (
                self.connect()
                .execute("SELECT 1 FROM schema_migrations LIMIT 1")
                .fetchone()
            )
            return bool(result and result[0] == 1)
        except sqlite3.Error:
            return False

    def claim_message_id(self, message_id: str) -> bool:
        """Atomically claim a message id for process-wide idempotency."""
        if not message_id:
            return True
        with self.get_cursor() as cursor:
            cursor.execute(
                "INSERT OR IGNORE INTO processed_messages(message_id) VALUES (?)",
                (message_id,),
            )
            return cursor.rowcount == 1

    def prune_processed_messages(self, retention_days: int = 30) -> None:
        """Remove expired idempotency keys."""
        if retention_days < 1:
            raise ValueError("retention_days must be positive")
        with self.get_cursor() as cursor:
            cursor.execute(
                "DELETE FROM processed_messages "
                "WHERE processed_at < datetime('now', ?)",
                (f"-{retention_days} days",),
            )


# Global database instances mapped by normalized path
_db_instances: Dict[str, DatabaseConnection] = {}
_db_instance: Optional[DatabaseConnection] = None


def get_database(db_path: str) -> DatabaseConnection:
    """
    Get or create database instance for the specified path.

    Args:
        db_path: Path to SQLite database file

    Returns:
        DatabaseConnection instance
    """
    global _db_instance
    normalized_path = str(Path(db_path).resolve())
    if normalized_path not in _db_instances:
        _db_instances[normalized_path] = DatabaseConnection(db_path)
    _db_instance = _db_instances[normalized_path]
    return _db_instance


def reset_database_instances() -> None:
    """Close and reset all cached database connections (useful for testing)."""
    global _db_instance
    for conn in list(_db_instances.values()):
        try:
            conn.close()
        except Exception:
            pass
    _db_instances.clear()
    _db_instance = None


def initialize_database(db_path: str) -> DatabaseConnection:
    """
    Initialize database with all tables.

    Args:
        db_path: Path to SQLite database file

    Returns:
        Initialized DatabaseConnection instance
    """
    db = get_database(db_path)
    db.initialize_database()
    return db
