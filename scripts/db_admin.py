"""Operational database commands for backup verification and retention."""

import argparse
import hashlib
import sqlite3
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from config import settings  # noqa: E402
from database import initialize_database  # noqa: E402


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify(path: Path) -> None:
    with sqlite3.connect(path) as connection:
        result = connection.execute("PRAGMA integrity_check").fetchone()
    if not result or result[0] != "ok":
        raise RuntimeError(f"Database integrity check failed: {path}")
    print(f"OK {path} sha256={sha256(path)}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("backup", "verify", "prune"))
    parser.add_argument("--path", default=settings.database_path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--retention-days", type=int, default=30)
    args = parser.parse_args()

    database = None
    if args.command == "verify":
        verify(Path(args.path))
    elif args.command == "backup":
        database = initialize_database(args.path)
        output = args.output or Path("backups") / "sisebel.db"
        database.backup_database(str(output))
        verify(output)
    else:
        database = initialize_database(args.path)
        database.prune_processed_messages(args.retention_days)
        print("Processed message retention cleanup completed")
    if database:
        database.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
