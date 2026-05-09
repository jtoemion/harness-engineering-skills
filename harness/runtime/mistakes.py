import re
import shutil
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Literal

MISTAKES_PATH = Path(__file__).parent.parent / "MISTAKES.md"
GLOBAL_VAULT = Path("C:/Users/jtoem/Obsidian/AntigravityV")
CANONICAL_FILES = [".memory/activeContext.md", ".memory/progress.md"]
MAX_STALENESS_MINUTES = 60


@dataclass
class MistakeEntry:
    date: str
    category: str
    error: str
    cause: str
    lesson: str
    references: list[str] = field(default_factory=list)
    status: Literal["ACTIVE", "RESOLVED", "SUPERSEDED"] = "ACTIVE"


def load_all() -> list[MistakeEntry]:
    entries = []
    content = MISTAKES_PATH.read_text(encoding="utf-8")
    pattern = re.compile(
        r"## \[(\d{4}-\d{2}-\d{2})\] \| \[([^\]]+)\]\s+"
        r"\*\*Error\*\*\s*:\s*(.+?)\s*\n"
        r"\*\*Cause\*\*\s*:\s*(.+?)\s*\n"
        r"\*\*Lesson\*\*\s*:\s*(.+?)\s*\n"
        r"(?:\*\*References\*\*\s*:\s*(.+?)\s*\n)?"
        r"\*\*Status\*\*\s*:\s*(\w+)",
        re.DOTALL,
    )
    for match in pattern.finditer(content):
        refs = []
        if match.group(6):
            refs = [r.strip() for r in match.group(6).split(",")]
        entries.append(
            MistakeEntry(
                date=match.group(1),
                category=match.group(2),
                error=match.group(3).strip(),
                cause=match.group(4).strip(),
                lesson=match.group(5).strip(),
                references=refs,
                status=match.group(7).strip(),
            )
        )
    return entries


def save_all(entries: list[MistakeEntry]) -> None:
    lines = [
        "# Global Mistakes Log",
        "",
        "This file tracks all mistakes made across projects to prevent repetition.",
        "Format: `[DATE] | [CATEGORY]` — each entry encodes an assumption that failed.",
        "",
        "## Schema",
        "```markdown",
        "## [YYYY-MM-DD] | [MISTAKE CATEGORY]",
        "**Error**     : [What went wrong]",
        "**Cause**     : [Why it happened]",
        "**Lesson**    : [How to avoid it in future]",
        "**References**: [Files/code affected]",
        "**Status**    : [ACTIVE | RESOLVED | SUPERSEDED]",
        "```",
        "",
        "---",
        "",
        "## Entry Template (DO NOT DELETE THIS LINE)",
        "<!-- New entries go below this line -->",
        "",
    ]
    for e in entries:
        refs = ", ".join(e.references) if e.references else ""
        lines.append(f"## [{e.date}] | [{e.category}]")
        lines.append(f"**Error**     : {e.error}")
        lines.append(f"**Cause**     : {e.cause}")
        lines.append(f"**Lesson**    : {e.lesson}")
        if refs:
            lines.append(f"**References**: {refs}")
        lines.append(f"**Status**    : {e.status}")
        lines.append("")
    MISTAKES_PATH.write_text("\n".join(lines), encoding="utf-8")


def check_relevant(task_input: str) -> list[MistakeEntry]:
    active = [e for e in load_all() if e.status == "ACTIVE"]
    if not active:
        return []
    words = set(task_input.lower().split())
    scored = []
    for e in active:
        text = f"{e.error} {e.lesson}".lower()
        entry_words = set(text.split())
        overlap = len(words & entry_words)
        score = overlap / len(entry_words) if entry_words else 0
        if score > 0.3:
            scored.append((score, e))
    for score, entry in sorted(scored, key=lambda x: -x[0]):
        print(f"[{entry.date}] {entry.category}: {entry.lesson}")
    return [e for _, e in scored]


def log_mistake(entry: MistakeEntry) -> None:
    anchor = "<!-- New entries go below this line -->"
    content = MISTAKES_PATH.read_text(encoding="utf-8")
    refs = ", ".join(entry.references) if entry.references else ""
    new_entry = (
        f"## [{entry.date}] | [{entry.category}]\n"
        f"**Error**     : {entry.error}\n"
        f"**Cause**     : {entry.cause}\n"
        f"**Lesson**    : {entry.lesson}\n"
    )
    if refs:
        new_entry += f"**References**: {refs}\n"
    new_entry += f"**Status**    : {entry.status}\n"
    if refs:
        parts = content.split(anchor, 1)
        parts[1] = new_entry + "\n" + parts[1]
    else:
        parts = content.split(anchor, 1)
        parts[1] = new_entry + "\n" + parts[1]
    MISTAKES_PATH.write_text(anchor.join(parts), encoding="utf-8")


def mark_resolved(date_str: str) -> None:
    entries = load_all()
    changed = False
    for e in entries:
        if e.date == date_str and e.status == "ACTIVE":
            e.status = "RESOLVED"
            changed = True
    if changed:
        save_all(entries)
    else:
        print(f"No active entry found for date {date_str}")


def sync_global() -> None:
    active = [e for e in load_all() if e.status == "ACTIVE"]
    if not active:
        return
    dest_dir = GLOBAL_VAULT / "00_Global" / "Mistakes"
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_file = dest_dir / "harness_mistakes.md"
    lines = ["# Active Mistakes from Harness\n"]
    for e in active:
        refs = ", ".join(e.references) if e.references else ""
        lines.append(f"## [{e.date}] | [{e.category}]")
        lines.append(f"**Error**     : {e.error}")
        lines.append(f"**Cause**     : {e.cause}")
        lines.append(f"**Lesson**    : {e.lesson}")
        if refs:
            lines.append(f"**References**: {refs}")
        lines.append(f"**Status**    : {e.status}")
        lines.append("")
    dest_file.write_text("\n".join(lines), encoding="utf-8")