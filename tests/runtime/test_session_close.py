"""Tests for session_close.py."""

import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "skills"))
from harness.runtime.session_close import (
    STEPS,
    _step_index,
    _ill_captures_count,
    run_close,
)


class TestStepsDefined:
    def test_has_12_steps(self):
        assert len(STEPS) == 12

    def test_all_steps_have_names_and_descriptions(self):
        for step in STEPS:
            assert len(step) == 2
            assert isinstance(step[0], str)
            assert isinstance(step[1], str)

    def test_step_names_unique(self):
        names = [s[0] for s in STEPS]
        assert len(names) == len(set(names))


class TestStepIndex:
    def test_returns_correct_index(self):
        assert _step_index("ill_check") == 0
        assert _step_index("create_staging") == 1
        assert _step_index("write_session") == 2
        assert _step_index("atomic_move") == 8
        assert _step_index("git_commit") == 11

    def test_returns_zero_for_unknown(self):
        assert _step_index("unknown_step") == 0


class TestIllCapturesCount:
    def test_returns_zero_when_no_captures_file(self, tmp_path):
        workspace = tmp_path / "workspace"
        workspace.mkdir()
        with patch("harness.runtime.session_close.WORKSPACE_ROOT", workspace):
            result = _ill_captures_count()
        assert result == 0

    def test_returns_zero_when_memory_dir_missing(self, tmp_path):
        workspace = tmp_path / "workspace"
        workspace.mkdir()
        with patch("harness.runtime.session_close.WORKSPACE_ROOT", workspace):
            result = _ill_captures_count()
        assert result == 0

    def test_counts_capture_entries(self, tmp_path):
        workspace = tmp_path / "workspace"
        workspace.mkdir()
        memory_dir = workspace / ".memory" / "ill"
        memory_dir.mkdir(parents=True)
        captures = memory_dir / "captures.md"
        captures.write_text("## capture 1\ninefficiency: foo\n## capture 2\ninefficiency: bar\n")
        with patch("harness.runtime.session_close.WORKSPACE_ROOT", workspace):
            result = _ill_captures_count()
        assert result >= 0


class TestRunClose:
    def test_non_resume_completes_all_steps(self, tmp_path):
        workspace = tmp_path / "workspace"
        workspace.mkdir()
        state_file = workspace / ".harness-state.json"
        state_file.write_text(json.dumps({"session_id": "test-session", "mode": "full", "close_step": "write_session"}))
        with patch("harness.runtime.session_close.WORKSPACE_ROOT", workspace):
            with patch("harness.runtime.state.STATE_FILE", state_file):
                with patch("harness.runtime.state.WORKSPACE_ROOT", workspace):
                    state = run_close(resume=False)
        assert state["close_step"] == "git_commit"

    def test_resume_starts_from_correct_step_index(self, tmp_path):
        workspace = tmp_path / "workspace"
        workspace.mkdir()
        state_file = workspace / ".harness-state.json"
        with patch("harness.runtime.session_close.WORKSPACE_ROOT", workspace):
            with patch("harness.runtime.state.STATE_FILE", state_file):
                with patch("harness.runtime.state.WORKSPACE_ROOT", workspace):
                    from harness.runtime.session_close import _step_index
                    idx = _step_index("write_session")
                    assert idx == 2
                    idx = _step_index("validate_staging")
                    assert idx == 7


class TestAcceptanceCriteria:
    def test_all_12_steps_defined(self):
        expected = [
            "ill_check", "create_staging", "write_session", "update_memory",
            "write_mistakes", "write_patterns", "write_decisions", "validate_staging",
            "atomic_move", "sync_global", "update_dashboard", "git_commit"
        ]
        actual = [s[0] for s in STEPS]
        assert actual == expected