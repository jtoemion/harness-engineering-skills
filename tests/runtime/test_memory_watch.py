"""Tests for memory_watch.py."""

import sys
import tempfile
from datetime import datetime, timezone, timedelta
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "skills"))
from harness.runtime.memory_watch import (
    CANONICAL_FILES,
    MAX_STALENESS_MINUTES,
    check_staleness,
    validate_schemas,
)


class TestCheckStaleness:
    """Tests for check_staleness()."""

    def test_returns_ok_for_recent_file(self, tmp_path):
        """Should return OK for files newer than MAX_STALENESS_MINUTES."""
        workspace = tmp_path / "workspace"
        workspace.mkdir()
        memory = workspace / ".memory"
        memory.mkdir()
        (memory / "activeContext.md").write_text("recent")
        (memory / "progress.md").write_text("recent")
        with patch("harness.runtime.memory_watch.WORKSPACE_ROOT", workspace):
            results = check_staleness()
        for r in results:
            assert r["status"] == "OK"
            assert r["age_minutes"] == 0

    def test_returns_stale_for_old_file(self, tmp_path):
        """Should return STALE for files older than MAX_STALENESS_MINUTES."""
        workspace = tmp_path / "workspace"
        workspace.mkdir()
        memory = workspace / ".memory"
        memory.mkdir()
        old_file = memory / "activeContext.md"
        old_file.write_text("old")
        old_time = datetime.now(timezone.utc) - timedelta(minutes=MAX_STALENESS_MINUTES + 1)
        old_ts = old_time.timestamp()
        old_file.touch()
        import os
        os.utime(old_file, (old_ts, old_ts))
        with patch("harness.runtime.memory_watch.WORKSPACE_ROOT", workspace):
            results = check_staleness()
        stale = next(r for r in results if "activeContext" in r["file"])
        assert stale["status"] == "STALE"

    def test_returns_missing_for_nonexistent_file(self, tmp_path):
        """Should return MISSING for files that do not exist."""
        workspace = tmp_path / "workspace"
        workspace.mkdir()
        with patch("harness.runtime.memory_watch.WORKSPACE_ROOT", workspace):
            results = check_staleness()
        for r in results:
            assert r["status"] == "MISSING"
            assert r["age_minutes"] is None


class TestValidateSchemas:
    """Tests for validate_schemas()."""

    def test_returns_empty_list(self):
        """Should return empty list (placeholder)."""
        assert validate_schemas() == []


class TestConstants:
    """Tests for constants."""

    def test_canonical_files_defined(self):
        """Should have CANONICAL_FILES defined."""
        assert len(CANONICAL_FILES) == 2
        assert ".memory/activeContext.md" in CANONICAL_FILES
        assert ".memory/progress.md" in CANONICAL_FILES

    def test_max_staleness_minutes(self):
        """Should have MAX_STALENESS_MINUTES set to 60."""
        assert MAX_STALENESS_MINUTES == 60
