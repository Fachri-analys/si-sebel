"""
Database migration utility for Si Sebel Bot.
Handles schema migrations safely for existing SQLite databases.
Adds missing columns, deduplicates data, and creates unique indexes so ON CONFLICT works.
"""

from typing import List
from .schema import ALL_SCHEMAS, MIGRATION_SCHEMA


def run_migrations(db) -> None:
    """
    Run safe migrations on database.

    Args:
        db: DatabaseConnection instance or sqlite3 connection
    """
    conn = db.connect() if hasattr(db, "connect") else db
    cursor = conn.cursor()

    try:
        cursor.executescript(MIGRATION_SCHEMA)
        cursor.execute(
            "INSERT OR IGNORE INTO schema_migrations(version) VALUES (?)",
            (1,),
        )
        # 1. Add missing columns to existing tables
        _migrate_columns(cursor)
        # Create missing tables and indexes after legacy tables have been upgraded.
        for schema in ALL_SCHEMAS:
            cursor.executescript(schema)
        conn.commit()

        # 2. Clean up duplicates so unique indexes can be created
        _deduplicate_data(cursor)
        conn.commit()

        # 3. Create unique indexes to support ON CONFLICT clauses
        _create_unique_indexes(cursor)
        conn.commit()

        cursor.execute(
            "UPDATE schema_migrations SET applied_at = CURRENT_TIMESTAMP WHERE version = 1"
        )
        conn.commit()

    except Exception as e:
        conn.rollback()
        raise Exception(f"Database migration failed: {e}")
    finally:
        cursor.close()


def _get_columns(cursor, table_name: str) -> List[str]:
    """Get list of column names for a table."""
    cursor.execute(f"PRAGMA table_info({table_name})")
    return [col[1] for col in cursor.fetchall()]


def _migrate_columns(cursor) -> None:
    """Check and add missing columns across all tables."""
    tables = [
        "school_info",
        "jurusan",
        "ppdb_info",
        "calendar",
        "contact",
        "facilities",
        "extracurricular",
        "faq",
    ]
    optional_columns = {
        "school_info": {
            "category": "TEXT",
            "description": "TEXT",
        },
        "jurusan": {
            "kode": "TEXT",
            "deskripsi": "TEXT",
            "syarat": "TEXT",
            "prospek": "TEXT",
            "kuota": "INTEGER DEFAULT 0",
        },
        "ppdb_info": {"category": "TEXT", "tahun_ajaran": "TEXT"},
        "calendar": {"tahun_ajaran": "TEXT"},
        "contact": {"phone_number": "TEXT", "email": "TEXT", "description": "TEXT"},
        "facilities": {
            "description": "TEXT",
            "location": "TEXT",
            "capacity": "INTEGER",
        },
        "extracurricular": {
            "description": "TEXT",
            "schedule": "TEXT",
            "requirements": "TEXT",
            "contact_person": "TEXT",
        },
        "faq": {
            "keywords": "TEXT",
            "category": "TEXT",
            "priority": "INTEGER DEFAULT 0",
            "hit_count": "INTEGER DEFAULT 0",
        },
    }

    for table in tables:
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,)
        )
        if not cursor.fetchone():
            continue

        existing_cols = _get_columns(cursor, table)

        for column, definition in optional_columns.get(table, {}).items():
            if column not in existing_cols:
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")
                existing_cols.append(column)

        if "is_active" not in existing_cols:
            cursor.execute(
                f"ALTER TABLE {table} ADD COLUMN is_active BOOLEAN DEFAULT 1"
            )

        if "source" not in existing_cols:
            cursor.execute(
                f"ALTER TABLE {table} ADD COLUMN source TEXT DEFAULT 'Belum terverifikasi'"
            )

        if "verified_at" not in existing_cols:
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN verified_at TIMESTAMP")

        if "updated_at" not in existing_cols:
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN updated_at TIMESTAMP")
            cursor.execute(
                f"UPDATE {table} SET updated_at = CURRENT_TIMESTAMP WHERE updated_at IS NULL"
            )
        cursor.execute(f"UPDATE {table} SET is_active = 1 WHERE is_active IS NULL")
        cursor.execute(
            f"UPDATE {table} SET source = 'Belum terverifikasi' WHERE source IS NULL OR TRIM(source) = ''"
        )


def _deduplicate_data(cursor) -> None:
    """
    Remove duplicate rows in tables that previously lacked UNIQUE constraints.
    Keeps the row with the lowest id.
    """
    cursor.execute("""
        DELETE FROM calendar
        WHERE id NOT IN (
            SELECT MIN(id)
            FROM calendar
            GROUP BY event_name, COALESCE(tahun_ajaran, '')
        )
    """)

    cursor.execute("""
        DELETE FROM contact
        WHERE id NOT IN (
            SELECT MIN(id)
            FROM contact
            GROUP BY name, role
        )
    """)

    cursor.execute("""
        DELETE FROM faq
        WHERE id NOT IN (
            SELECT MIN(id)
            FROM faq
            GROUP BY LOWER(TRIM(question))
        )
    """)

    cursor.execute("""
        DELETE FROM ppdb_info
        WHERE id NOT IN (
            SELECT MIN(id)
            FROM ppdb_info
            GROUP BY key
        )
    """)


def _create_unique_indexes(cursor) -> None:
    """Create unique indexes to ensure ON CONFLICT statements match unique constraints."""
    cursor.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS idx_calendar_unique ON calendar(event_name, tahun_ajaran)"
    )
    cursor.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS idx_contact_unique ON contact(name, role)"
    )
    cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_faq_unique ON faq(question)")
    cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_ppdb_key ON ppdb_info(key)")
    cursor.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS idx_jurusan_nama ON jurusan(nama)"
    )
    cursor.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS idx_facilities_name ON facilities(name)"
    )
    cursor.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS idx_extracurricular_name ON extracurricular(name)"
    )
    cursor.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS idx_school_info_key ON school_info(key)"
    )
