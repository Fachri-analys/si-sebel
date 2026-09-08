"""Validate that every direct dependency has an exact lock entry."""

import re
import sys
from pathlib import Path


def package_name(line: str) -> str:
    return re.split(r"[<>=!~]", line.strip(), maxsplit=1)[0].strip().lower()


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    requirements = root / "requirements.txt"
    lockfile = root / "requirements.lock"
    direct = {
        package_name(line)
        for line in requirements.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }
    locked = {
        package_name(line)
        for line in lockfile.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }
    missing = sorted(direct - locked)
    unpinned = sorted(
        line
        for line in lockfile.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#") and "==" not in line
    )
    if missing or unpinned:
        if missing:
            print(f"Missing lock entries: {', '.join(missing)}", file=sys.stderr)
        if unpinned:
            print(f"Unpinned lock entries: {', '.join(unpinned)}", file=sys.stderr)
        return 1
    print(f"Validated {len(direct)} direct dependency lock entries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
