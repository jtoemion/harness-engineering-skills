"""Tests for mistakes.py."""

import re
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "skills"))
from harness.runtime.mistakes import (
    INSERT_MARKER,
    check_relevant,
    log_mistake,
    mark_resolved,
    _parse_entries,
)


MISTAKES_CONTENT = """# Global Mistakes Log

This file tracks all mistakes made across projects to prevent repetition.
Format: `[DATE] | [CATEGORY]` — each entry encodes an assumption that failed.

## Schema
```markdown
## [YYYY-MM-DD] | [MISTAKE CATEGORY]
**Error**     : [What went wrong]
**Cause**     : [Why it happened]
**Lesson**    : [How to avoid it in future]
**References**: [Files/code affected]
**Status**    : [ACTIVE | RESOLVED | SUPERSEDED]
```

---

## Entry Template (DO NOT DELETE THIS LINE)
<!-- New entries go below this line -->
"""


class TestLogMistake:
    """Tests for log_mistake()."""

    def test_adds_entry_below_insert_marker(self, tmp_path):
        """Should insert new entry below the insert marker."""
        mistakes_file = tmp_path / "MISTAKES.md"
        mistakes_file.write_text(MISTAKES_CONTENT)

        with patch("harness.runtime.mistakes.MISTAKES_FILE", mistakes_file):
            log_mistake(
                error="test error",
                cause="test cause",
                lesson="test lesson",
                refs=["file1.py", "file2.py"],
            )

        content = mistakes_file.read_text()
        assert "test error" in content
        assert "test cause" in content
        assert "test lesson" in content
        assert "file1.py, file2.py" in content
        assert "**Status**    : ACTIVE" in content
        idx = content.index(INSERT_MARKER)
        entry_start = content.index("## ", idx)
        assert entry_start > idx

    def test_raises_when_file_missing(self, tmp_path):
        """Should raise FileNotFoundError when MISTAKES.md does not exist."""
        missing = tmp_path / "nonexistent.md"
        with patch("harness.runtime.mistakes.MISTAKES_FILE", missing):
            with pytest.raises(FileNotFoundError):
                log_mistake("err", "cause", "lesson", [])

    def test_raises_when_marker_missing(self, tmp_path):
        """Should raise ValueError when insert marker not found."""
        mistakes_file = tmp_path / "MISTAKES.md"
        mistakes_file.write_text("no marker here")
        with patch("harness.runtime.mistakes.MISTAKES_FILE", mistakes_file):
            with pytest.raises(ValueError):
                log_mistake("err", "cause", "lesson", [])


class TestCheckRelevant:
    """Tests for check_relevant()."""

    def test_returns_active_entries_matching_keywords(self, tmp_path):
        """Should return ACTIVE entries whose fields contain task keywords."""
        content = MISTAKES_CONTENT + """
## [2026-05-09] | AUTO-LOGGED
**Error**     : Subagent dispatch timeout
**Cause**     : Network latency exceeded threshold
**Lesson**    : Always set explicit timeout on subagent calls
**References**: harness/subagent.py, runtime/conductor.py
**Status**    : ACTIVE

## [2026-05-08] | AUTO-LOGGED
**Error**     : Wrong file mode used
**Cause**     : Opened file in write instead of append
**Lesson**    : Check file mode before write operations
**References**: runtime/state.py
**Status**    : RESOLVED
"""
        mistakes_file = tmp_path / "MISTAKES.md"
        mistakes_file.write_text(content)

        with patch("harness.runtime.mistakes.MISTAKES_FILE", mistakes_file):
            result = check_relevant("subagent timeout dispatch")

        assert len(result) == 1
        assert result[0]["error"] == "Subagent dispatch timeout"
        assert result[0]["status"] == "ACTIVE"

    def test_excludes_resolved_entries(self, tmp_path):
        """Should not return entries with RESOLVED status."""
        content = MISTAKES_CONTENT + """
## [2026-05-08] | AUTO-LOGGED
**Error**     : File mode error
**Cause**     : Wrong mode
**Lesson**    : Check mode
**References**: runtime/state.py
**Status**    : RESOLVED
"""
        mistakes_file = tmp_path / "MISTAKES.md"
        mistakes_file.write_text(content)

        with patch("harness.runtime.mistakes.MISTAKES_FILE", mistakes_file):
            result = check_relevant("file mode error")

        assert len(result) == 0

    def test_returns_empty_when_no_match(self, tmp_path):
        """Should return empty list when no keywords match."""
        content = MISTAKES_CONTENT + """
## [2026-05-09] | AUTO-LOGGED
**Error**     : Subagent timeout
**Cause**     : Network issue
**Lesson**    : Set timeout
**References**: subagent.py
**Status**    : ACTIVE
"""
        mistakes_file = tmp_path / "MISTAKES.md"
        mistakes_file.write_text(content)

        with patch("harness.runtime.mistakes.MISTAKES_FILE", mistakes_file):
            result = check_relevant("completely unrelated task xyz")

        assert len(result) == 0

    def test_returns_empty_when_file_missing(self, tmp_path):
        """Should return empty list when MISTAKES.md does not exist."""
        missing = tmp_path / "nonexistent.md"
        with patch("harness.runtime.mistakes.MISTAKES_FILE", missing):
            result = check_relevant("any task")
        assert result == []


class TestMarkResolved:
    """Tests for mark_resolved()."""

    def test_changes_active_to_resolved(self, tmp_path):
        """Should change ACTIVE status to RESOLVED for matching entry."""
        content = MISTAKES_CONTENT + """
## [2026-05-09] | AUTO-LOGGED
**Error**     : Test error
**Cause**     : Test cause
**Lesson**    : Test lesson
**References**: test.py
**Status**    : ACTIVE
"""
        mistakes_file = tmp_path / "MISTAKES.md"
        mistakes_file.write_text(content)

        with patch("harness.runtime.mistakes.MISTAKES_FILE", mistakes_file):
            mark_resolved("2026-05-09")

        new_content = mistakes_file.read_text()
        assert "**Status**    : RESOLVED" in new_content
        assert "**Status**    : ACTIVE" not in new_content

    def test_raises_when_no_active_entry(self, tmp_path):
        """Should raise ValueError when no ACTIVE entry matches date."""
        content = MISTAKES_CONTENT + """
## [2026-05-09] | AUTO-LOGGED
**Error**     : Test error
**Cause**     : Test cause
**Lesson**    : Test lesson
**References**: test.py
**Status**    : RESOLVED
"""
        mistakes_file = tmp_path / "MISTAKES.md"
        mistakes_file.write_text(content)

        with patch("harness.runtime.mistakes.MISTAKES_FILE", mistakes_file):
            with pytest.raises(ValueError):
                mark_resolved("2026-05-09")

    def test_raises_when_file_missing(self, tmp_path):
        """Should raise FileNotFoundError when MISTAKES.md does not exist."""
        missing = tmp_path / "nonexistent.md"
        with patch("harness.runtime.mistakes.MISTAKES_FILE", missing):
            with pytest.raises(FileNotFoundError):
                mark_resolved("2026-05-09")


class TestParseEntries:
    """Tests for _parse_entries()."""

    def test_parses_all_fields(self):
        """Should correctly parse date, error, cause, lesson, references, status."""
        content = """
## [2026-05-09] | AUTO-LOGGED
**Error**     : Test error
**Cause**     : Test cause
**Lesson**    : Test lesson
**References**: file1.py, file2.py
**Status**    : ACTIVE
"""
        entries = _parse_entries(content)
        assert len(entries) == 1
        assert entries[0]["date"] == "2026-05-09"
        assert entries[0]["error"] == "Test error"
        assert entries[0]["cause"] == "Test cause"
        assert entries[0]["lesson"] == "Test lesson"
        assert entries[0]["references"] == "file1.py, file2.py"
        assert entries[0]["status"] == "ACTIVE"
