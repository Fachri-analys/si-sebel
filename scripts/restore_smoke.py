"""Create, verify, and reopen a database backup as a restore smoke test."""

import argparse
import sqlite3
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from database import initialize_database  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--database", default="sisebel.db")
    parser.add_argument("--backup", default="backups/restore-smoke.db")
    args = parser.parse_args()

    database = initialize_database(args.database)
    try:
        database.backup_database(args.backup)
    finally:
        database.close()

    with sqlite3.connect(args.backup) as connection:
        integrity = connection.execute("PRAGMA integrity_check").fetchone()
        migrations = connection.execute(
            "SELECT COUNT(*) FROM schema_migrations"
        ).fetchone()
    if not integrity or integrity[0] != "ok" or not migrations or migrations[0] < 1:
        raise RuntimeError("Restore smoke test failed")
    print(f"Restore smoke test passed: {Path(args.backup)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
