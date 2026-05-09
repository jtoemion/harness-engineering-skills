"""Memory staleness guardian + schema validator."""

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any

WORKSPACE_ROOT = Path(__file__).parent.parent.parent.parent

CANONICAL_FILES = [
    ".memory/activeContext.md",
    ".memory/progress.md",
]
MAX_STALENESS_MINUTES = 60


def _get_file_age_minutes(path: Path) -> int:
    """Return age of file in minutes."""
    if not path.exists():
        return -1
    mtime = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
    now = datetime.now(timezone.utc)
    return int((now - mtime).total_seconds() / 60)


def check_staleness() -> List[Dict[str, Any]]:
    """Check memory files for staleness.

    Returns list of dicts with file path and age info.
    Files older than MAX_STALENESS_MINUTES are considered stale.
    Non-existent files are marked as MISSING.
    """
    results = []
    for rel_path in CANONICAL_FILES:
        path = WORKSPACE_ROOT / rel_path
        age = _get_file_age_minutes(path)
        if age < 0:
            results.append({"file": str(rel_path), "status": "MISSING", "age_minutes": None})
        elif age > MAX_STALENESS_MINUTES:
            results.append({"file": str(rel_path), "status": "STALE", "age_minutes": age})
        else:
            results.append({"file": str(rel_path), "status": "OK", "age_minutes": age})
    return results


def validate_schemas() -> List[Dict[str, str]]:
    """Validate memory files match templates.

    Currently placeholder — returns empty list.
    """
    return []


def main() -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Memory staleness guardian")
    parser.add_argument("--check", action="store_true", help="Check staleness")
    args = parser.parse_args()

    if args.check:
        results = check_staleness()
        for r in results:
            print(f"{r['file']}: {r['status']} (age={r['age_minutes']})")
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
