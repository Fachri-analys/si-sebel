"""Container health and readiness checks for Si Sebel."""

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from database import initialize_database  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--database", default="sisebel.db")
    parser.add_argument("--auth-folder", default="piwapp_auth")
    parser.add_argument(
        "--require-auth",
        action="store_true",
        help="Require a persisted WhatsApp auth directory for readiness.",
    )
    args = parser.parse_args()

    database = initialize_database(args.database)
    try:
        if not database.health_check():
            print("database health check failed", file=sys.stderr)
            return 1
        if args.require_auth and not Path(args.auth_folder).is_dir():
            print("WhatsApp auth directory is not ready", file=sys.stderr)
            return 1
    finally:
        database.close()
    print("healthy")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
