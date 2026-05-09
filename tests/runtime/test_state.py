"""Tests for state.py."""

import json
import os
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "skills"))
from harness.runtime.state import (
    STATE_FILE,
    detect_mode,
    init_state,
    read_state,
    write_state,
)


class TestDetectMode:
    """Tests for detect_mode()."""

    def test_detects_full_when_memory_dir_exists(self, tmp_path):
        """Should return 'full' when .memory/ directory exists."""
        workspace = tmp_path / "workspace"
        workspace.mkdir()
        (workspace / ".memory").mkdir()
        with patch("harness.runtime.state.WORKSPACE_ROOT", workspace):
            result = detect_mode()
        assert result == "full"

    def test_detects_quick_when_memory_dir_missing(self, tmp_path):
        """Should return 'quick' when .memory/ directory does not exist."""
        workspace = tmp_path / "workspace"
        workspace.mkdir()
        with patch("harness.runtime.state.WORKSPACE_ROOT", workspace):
            result = detect_mode()
        assert result == "quick"


class TestReadState:
    """Tests for read_state()."""

    def test_returns_empty_dict_when_file_missing(self, tmp_path):
        """Should return empty dict when state file does not exist."""
        with patch("harness.runtime.state.STATE_FILE", tmp_path / "missing.json"):
            result = read_state()
        assert result == {}

    def test_reads_existing_state(self, tmp_path):
        """Should read and parse existing state file."""
        state_file = tmp_path / ".harness-state.json"
        test_state = {"session_id": "2026-05-09-1200", "mode": "full"}
        state_file.write_text(json.dumps(test_state))
        with patch("harness.runtime.state.STATE_FILE", state_file):
            result = read_state()
        assert result == test_state


class TestWriteState:
    """Tests for write_state()."""

    def test_writes_state_to_file(self, tmp_path):
        """Should write state dict as JSON to file."""
        state_file = tmp_path / ".harness-state.json"
        test_state = {"session_id": "test", "mode": "quick"}
        with patch("harness.runtime.state.STATE_FILE", state_file):
            write_state(test_state)
        assert json.loads(state_file.read_text()) == test_state


class TestInitState:
    """Tests for init_state()."""

    def test_initializes_with_detected_mode(self, tmp_path):
        """Should detect mode and initialize state when mode is None."""
        state_file = tmp_path / ".harness-state.json"
        with patch("harness.runtime.state.STATE_FILE", state_file):
            with patch("harness.runtime.state.detect_mode", return_value="quick"):
                state = init_state()
        assert state["mode"] == "quick"
        assert state["state"] == "ACTIVE"
        assert state["session_id"] is not None
        assert state["boot_time"] is not None

    def test_initializes_with_specified_mode(self, tmp_path):
        """Should use specified mode when provided."""
        state_file = tmp_path / ".harness-state.json"
        with patch("harness.runtime.state.STATE_FILE", state_file):
            state = init_state(mode="full")
        assert state["mode"] == "full"

    def test_writes_state_to_file(self, tmp_path):
        """Should write initialized state to file."""
        state_file = tmp_path / ".harness-state.json"
        with patch("harness.runtime.state.STATE_FILE", state_file):
            init_state(mode="quick")
        saved = json.loads(state_file.read_text())
        assert saved["mode"] == "quick"
        assert saved["state"] == "ACTIVE"

    def test_session_id_format(self, tmp_path):
        """Should generate session_id in YYYY-MM-DD-HHMM format."""
        state_file = tmp_path / ".harness-state.json"
        with patch("harness.runtime.state.STATE_FILE", state_file):
            state = init_state()
        assert len(state["session_id"]) == 15
        assert state["session_id"][4] == "-"
        assert state["session_id"][7] == "-"

    def test_boot_time_is_iso8601(self, tmp_path):
        """Should generate boot_time in ISO8601 format."""
        state_file = tmp_path / ".harness-state.json"
        with patch("harness.runtime.state.STATE_FILE", state_file):
            state = init_state()
        datetime.fromisoformat(state["boot_time"])
