"""Tests for checkpoint.py."""

import os
import sys
import json
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "skills"))
from harness.runtime.state import STATE_FILE
from harness.runtime import checkpoint


class TestRunCheckpoint:
    """Tests for run_checkpoint()."""

    def test_sets_checkpoint_complete_true(self, tmp_path):
        """Should set checkpoint_complete = True."""
        state_file = tmp_path / ".harness-state.json"
        state_file.write_text(json.dumps({"session_id": "test", "mode": "quick"}))
        with patch("harness.runtime.state.STATE_FILE", state_file):
            with patch("harness.runtime.checkpoint.WORKSPACE_ROOT", tmp_path):
                result = checkpoint.run_checkpoint({}, "Test task")
        assert result["checkpoint_complete"] is True

    def test_resets_verification_logged_false(self, tmp_path):
        """Should reset verification_logged to False after checkpoint."""
        state_file = tmp_path / ".harness-state.json"
        state_file.write_text(json.dumps({
            "session_id": "test",
            "mode": "quick",
            "verification_logged": True
        }))
        with patch("harness.runtime.state.STATE_FILE", state_file):
            with patch("harness.runtime.checkpoint.WORKSPACE_ROOT", tmp_path):
                result = checkpoint.run_checkpoint({"verification_logged": True}, "Test task")
        assert result["verification_logged"] is False

    def test_sets_last_checkpoint_timestamp(self, tmp_path):
        """Should set last_checkpoint to ISO8601 timestamp."""
        state_file = tmp_path / ".harness-state.json"
        state_file.write_text(json.dumps({"session_id": "test", "mode": "quick"}))
        with patch("harness.runtime.state.STATE_FILE", state_file):
            with patch("harness.runtime.checkpoint.WORKSPACE_ROOT", tmp_path):
                result = checkpoint.run_checkpoint({}, "Test task")
        assert result["last_checkpoint"] is not None
        datetime.fromisoformat(result["last_checkpoint"])

    def test_step_handlers_called_in_order(self, tmp_path):
        """Should call each step handler in order."""
        state_file = tmp_path / ".harness-state.json"
        state_file.write_text(json.dumps({"session_id": "test", "mode": "quick"}))

        call_order = []
        original_handlers = checkpoint.STEP_HANDLERS.copy()

        def make_wrapper(name, orig):
            def wrapper(*args, **kwargs):
                call_order.append(name)
                return orig(*args, **kwargs)
            return wrapper

        wrapped_handlers = {
            name: make_wrapper(name, orig)
            for name, orig in original_handlers.items()
        }

        with patch("harness.runtime.state.STATE_FILE", state_file):
            with patch("harness.runtime.checkpoint.WORKSPACE_ROOT", tmp_path):
                with patch.object(checkpoint, "STEP_HANDLERS", wrapped_handlers):
                    checkpoint.run_checkpoint({}, "Test task")

        assert call_order == list(original_handlers.keys())


class TestCheckpointSteps:
    """Tests for individual checkpoint steps."""

    def test_steps_defined(self):
        """Should define all required checkpoint steps."""
        step_names = [s[0] for s in checkpoint.STEPS]
        required_steps = [
            "update_active_context",
            "update_progress",
            "update_tech_context",
            "write_session_note",
            "append_sessions_log",
            "write_mistakes",
            "write_patterns",
            "update_dashboard",
            "sync_global",
        ]
        for req in required_steps:
            assert req in step_names

    def test_sync_global_creates_checkpoint_file(self, tmp_path):
        """Should create checkpoint file in global vault."""
        state_file = tmp_path / ".harness-state.json"
        state_file.write_text(json.dumps({"session_id": "test", "mode": "quick"}))

        global_vault = tmp_path / "global_vault"
        global_vault.mkdir(parents=True, exist_ok=True)

        with patch("harness.runtime.state.STATE_FILE", state_file):
            with patch("harness.runtime.checkpoint.WORKSPACE_ROOT", tmp_path):
                with patch("harness.runtime.checkpoint.GLOBAL_VAULT", str(global_vault)):
                    checkpoint._sync_global({"session_id": "test"}, "Test task")

        checkpoints_dir = global_vault / "00_Global" / "Checkpoints"
        assert checkpoints_dir.exists()
        files = list(checkpoints_dir.glob("*.md"))
        assert len(files) == 1

    def test_append_sessions_log_creates_log(self, tmp_path):
        """Should create sessions.log and append entry."""
        state_file = tmp_path / ".harness-state.json"
        state_file.write_text(json.dumps({"session_id": "test", "mode": "quick"}))

        with patch("harness.runtime.state.STATE_FILE", state_file):
            with patch("harness.runtime.checkpoint.WORKSPACE_ROOT", tmp_path):
                checkpoint._append_sessions_log({"session_id": "test"}, "Test task")

        sessions_log = tmp_path / "00_Memory" / "sessions.log"
        assert sessions_log.exists()
        content = sessions_log.read_text(encoding="utf-8")
        assert "CHECKPOINT" in content
        assert "test" in content
        assert "Test task" in content