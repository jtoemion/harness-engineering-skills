"""Memory watch: validates .memory/ on demand and as git pre-commit hook."""

import argparse
import sys
import time
from pathlib import Path
from typing import Tuple, List

WORKSPACE_ROOT = Path(__file__).parent.parent.parent
HARNESS_ROOT = Path(r"C:\Users\jtoem\.config\opencode\skills\harness")
MEMORY_DIR = Path(".memory")
CANONICAL_FILES = [".memory/activeContext.md", ".memory/progress.md"]
MAX_STALENESS_MINUTES = 60

SCHEMA_REQUIREMENTS = {
    ".memory/activeContext.md": {
        "frontmatter_keys": ["project", "context", "updated"],
        "required_sections": ["# Context", "# Task"],
        "type_checks": {"updated": str},
    },
    ".memory/progress.md": {
        "frontmatter_keys": ["project", "phase", "updated"],
        "required_sections": ["# Progress", "# Next Steps"],
        "type_checks": {"phase": str, "updated": str},
    },
}


def check_staleness() -> List[str]:
    issues = []
    for rel_path in CANONICAL_FILES:
        file_path = Path(rel_path)
        if not file_path.exists():
            issues.append(f"MISSING: {rel_path}")
        else:
            age_seconds = time.time() - file_path.stat().st_mtime
            age_minutes = age_seconds / 60
            if age_minutes > MAX_STALENESS_MINUTES:
                issues.append(f"STALE ({int(age_minutes)}m): {rel_path}")
    return issues


def validate_schema(file_path: str) -> Tuple[bool, str]:
    path = Path(file_path)
    if not path.exists():
        return False, f"File does not exist: {file_path}"

    content = path.read_text(encoding="utf-8")
    lines = content.split("\n")

    if not content.startswith("---"):
        return False, f"Missing frontmatter delimiter in {file_path}"

    end_idx = content.find("---", 3)
    if end_idx == -1:
        return False, f"Malformed frontmatter in {file_path}"

    frontmatter_text = content[3:end_idx].strip()
    frontmatter = {}
    for line in frontmatter_text.split("\n"):
        if ":" in line:
            key, val = line.split(":", 1)
            frontmatter[key.strip()] = val.strip()

    reqs = SCHEMA_REQUIREMENTS.get(file_path, {})
    for key in reqs.get("frontmatter_keys", []):
        if key not in frontmatter:
            return False, f"Missing frontmatter key '{key}' in {file_path}"

    for key, expected_type in reqs.get("type_checks", {}).items():
        if key in frontmatter:
            val = frontmatter[key]
            if expected_type == str and not val:
                return False, f"Invalid type for '{key}' in {file_path}: expected non-empty string"

    body = content[end_idx + 3 :].strip()
    for section in reqs.get("required_sections", []):
        if section not in body:
            return False, f"Missing required section '{section}' in {file_path}"

    return True, ""


def check_all() -> Tuple[List[str], List[str]]:
    stale_files = check_staleness()
    schema_errors = []
    for rel_path in CANONICAL_FILES:
        is_valid, err = validate_schema(rel_path)
        if not is_valid:
            schema_errors.append(f"SCHEMA ERROR in {rel_path}: {err}")
    return stale_files, schema_errors


def check_staging(staging_dir: str) -> bool:
    staging_path = Path(staging_dir)
    if not staging_path.exists():
        return False

    for md_file in staging_path.rglob("*.md"):
        is_valid, err = validate_schema(str(md_file.relative_to(staging_path)))
        if not is_valid:
            print(f"Staging validation failed: {err}", file=sys.stderr)
            return False
    return True


def main():
    parser = argparse.ArgumentParser(description="Memory watch validator")
    parser.add_argument("--check-staleness", action="store_true", help="Check staleness of canonical files")
    parser.add_argument("--check-staging", metavar="DIR", help="Validate all markdown in staging directory")
    args = parser.parse_args()

    if args.check_staging:
        success = check_staging(args.check_staging)
        sys.exit(0 if success else 1)

    if args.check_staleness:
        stale = check_staleness()
        for issue in stale:
            print(issue)
        sys.exit(0 if not stale else 1)

    stale_files, schema_errors = check_all()
    has_issues = stale_files or schema_errors
    for issue in stale_files:
        print(f"STALE: {issue}")
    for err in schema_errors:
        print(f"ERROR: {err}")
    sys.exit(0 if not has_issues else 1)


if __name__ == "__main__":
    main()


validate_schemas = check_all