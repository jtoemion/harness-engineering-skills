"""Mistakes tracking — auto-writes MISTAKES.md and surfaces relevant lessons."""

import re
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE_ROOT = Path(__file__).parent.parent.parent.parent
MISTAKES_FILE = WORKSPACE_ROOT / "skills" / "harness" / "MISTAKES.md"
INSERT_MARKER = "<!-- New entries go below this line -->"
ENTRY_TEMPLATE = """## [{date}] | AUTO-LOGGED
**Error**     : {error}
**Cause**     : {cause}
**Lesson**    : {lesson}
**References**: {refs}
**Status**    : ACTIVE
"""


def log_mistake(error: str, cause: str, lesson: str, refs: list[str]) -> None:
    """Add entry to MISTAKES.md below insert marker."""
    if not MISTAKES_FILE.exists():
        raise FileNotFoundError(f"MISTAKES.md not found at {MISTAKES_FILE}")

    content = _read_mistakes()
    date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    refs_str = ", ".join(refs) if refs else "none"

    new_entry = ENTRY_TEMPLATE.format(
        date=date,
        error=error,
        cause=cause,
        lesson=lesson,
        refs=refs_str,
    )

    if INSERT_MARKER not in content:
        raise ValueError(f"Insert marker '{INSERT_MARKER}' not found in MISTAKES.md")

    new_content = content.replace(INSERT_MARKER, f"{INSERT_MARKER}\n{new_entry}")
    MISTAKES_FILE.write_text(new_content, encoding="utf-8")


def _read_mistakes() -> str:
    """Read MISTAKES.md with fallback encoding handling."""
    try:
        return MISTAKES_FILE.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return MISTAKES_FILE.read_text(encoding="utf-8", errors="replace")


def _parse_entries(content: str) -> list[dict]:
    """Parse all mistake entries from MISTAKES.md content."""
    entries = []
    entry_pattern = re.compile(
        r"^\s*## \[(\d{4}-\d{2}-\d{2})\] \| [^\n]+\n"
        r"^\s*\*\*Error\*\*\s*: ([^\n]+)\n"
        r"^\s*\*\*Cause\*\*\s*: ([^\n]+)\n"
        r"^\s*\*\*Lesson\*\*\s*: ([^\n]+)\n"
        r"^\s*\*\*References\*\*\s*: ([^\n]+)\n"
        r"^\s*\*\*Status\*\*\s*: ([^\n]+)",
        re.MULTILINE,
    )
    for match in entry_pattern.finditer(content):
        entries.append({
            "date": match.group(1),
            "error": match.group(2),
            "cause": match.group(3),
            "lesson": match.group(4),
            "references": match.group(5),
            "status": match.group(6),
        })
    return entries


def check_relevant(task_input: str) -> list[dict]:
    """Return ACTIVE entries whose fields contain keywords from task_input."""
    if not MISTAKES_FILE.exists():
        return []

    content = _read_mistakes()
    entries = _parse_entries(content)

    keywords = [w.lower() for w in re.split(r"\W+", task_input) if len(w) > 2]
    relevant = []

    for entry in entries:
        if entry["status"] != "ACTIVE":
            continue
        for kw in keywords:
            if (kw in entry["error"].lower() or
                kw in entry["cause"].lower() or
                kw in entry["lesson"].lower() or
                kw in entry["references"].lower()):
                relevant.append(entry)
                break

    return relevant


def mark_resolved(date_str: str) -> None:
    """Change ACTIVE to RESOLVED for entry matching date_str."""
    if not MISTAKES_FILE.exists():
        raise FileNotFoundError(f"MISTAKES.md not found at {MISTAKES_FILE}")

    content = _read_mistakes()

    status_pattern = re.compile(
        rf"(^\s*## \[{re.escape(date_str)}\] \| [^\n]+\n(?:[^\n]+\n){{4}}^\s*\*\*Status\*\*\s*: )ACTIVE",
        re.MULTILINE,
    )
    if not status_pattern.search(content):
        raise ValueError(f"No ACTIVE entry found for date '{date_str}'")

    new_content = status_pattern.sub(r"\1RESOLVED", content)
    MISTAKES_FILE.write_text(new_content, encoding="utf-8")
