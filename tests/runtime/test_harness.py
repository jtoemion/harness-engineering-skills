"""Tests for harness.py — CLI entry point."""

import argparse
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "skills"))
from harness.runtime import harness


class TestGatePreTask:
    """Tests for gate --phase pre-task."""

    @patch("harness.runtime.harness.detect_mode")
    @patch("harness.runtime.harness.read_state")
    @patch("harness.runtime.harness.check_staleness")
    @patch("harness.runtime.harness.check_relevant")
    @patch("harness.runtime.harness.route")
    def test_gate_routes_task(
        self, mock_route, mock_check_relevant, mock_check_staleness,
        mock_read_state, mock_detect_mode, capsys
    ):
        mock_detect_mode.return_value = "quick"
        mock_read_state.return_value = {"session_id": "test-001", "mode": "quick", "verification_logged": False}
        mock_check_staleness.return_value = []
        mock_check_relevant.return_value = []
        mock_route.return_value = {"id": "systematic-debugging", "skill_path": "skills/superpowers/systematic-debugging/SKILL.md"}

        args = argparse.Namespace(phase="pre-task", input="fix auth bug")
        result = harness.cmd_gate(args)

        assert result == 0
        mock_route.assert_called_once_with("fix auth bug")

    @patch("harness.runtime.harness.detect_mode")
    @patch("harness.runtime.harness.read_state")
    @patch("harness.runtime.harness.check_staleness")
    @patch("harness.runtime.harness.check_relevant")
    @patch("harness.runtime.harness.route")
    def test_gate_warns_when_verification_not_logged(
        self, mock_route, mock_check_relevant, mock_check_staleness,
        mock_read_state, mock_detect_mode, capsys
    ):
        mock_detect_mode.return_value = "quick"
        mock_read_state.return_value = {"session_id": "test-001", "mode": "quick", "verification_logged": False}
        mock_check_staleness.return_value = []
        mock_check_relevant.return_value = []
        mock_route.return_value = {"id": "test-skill", "skill_path": ""}

        args = argparse.Namespace(phase="pre-task", input="test task")
        harness.cmd_gate(args)

        captured = capsys.readouterr()
        assert "WARNING: verification_logged = False" in captured.out

    @patch("harness.runtime.harness.detect_mode")
    @patch("harness.runtime.harness.read_state")
    @patch("harness.runtime.harness.check_staleness")
    @patch("harness.runtime.harness.check_relevant")
    @patch("harness.runtime.harness.route")
    def test_gate_shows_relevant_mistakes(
        self, mock_route, mock_check_relevant, mock_check_staleness,
        mock_read_state, mock_detect_mode, capsys
    ):
        mock_detect_mode.return_value = "quick"
        mock_read_state.return_value = {"session_id": "test-001", "mode": "quick", "verification_logged": False}
        mock_check_staleness.return_value = []
        mock_check_relevant.return_value = [
            {"error": "null pointer in auth", "lesson": "always check for null"}
        ]
        mock_route.return_value = {"id": "test-skill", "skill_path": ""}

        args = argparse.Namespace(phase="pre-task", input="fix auth bug")
        harness.cmd_gate(args)

        captured = capsys.readouterr()
        assert "null pointer in auth" in captured.out


class TestCmdRoute:
    """Tests for route subcommand."""

    @patch("harness.runtime.harness.detect_mode")
    @patch("harness.runtime.harness.route")
    def test_route_calls_conductor(self, mock_route, mock_detect_mode, capsys):
        mock_detect_mode.return_value = "quick"
        mock_route.return_value = {"id": "systematic-debugging", "skill_path": "skills/superpowers/systematic-debugging/SKILL.md"}

        args = argparse.Namespace(input="debug auth issue")
        result = harness.cmd_route(args)

        assert result == 0
        mock_route.assert_called_once_with("debug auth issue")
        captured = capsys.readouterr()
        assert "systematic-debugging" in captured.out

    def test_route_requires_input(self, capsys):
        args = argparse.Namespace(input=None)
        result = harness.cmd_route(args)
        assert result == 1
        captured = capsys.readouterr()
        assert "--input is required" in captured.out


class TestCmdCheckpoint:
    """Tests for checkpoint subcommand."""

    @patch("harness.runtime.harness.read_state")
    @patch("harness.runtime.harness.run_checkpoint")
    def test_checkpoint_calls_run_checkpoint(self, mock_run, mock_read_state, capsys):
        mock_read_state.return_value = {"session_id": "test"}
        mock_run.return_value = {"checkpoint_complete": True}

        args = argparse.Namespace(task="fixed auth bug")
        result = harness.cmd_checkpoint(args)

        assert result == 0
        mock_run.assert_called_once()
        call_args = mock_run.call_args
        assert call_args[0][1] == "fixed auth bug"


class TestCmdClose:
    """Tests for close subcommand."""

    @patch("harness.runtime.harness.session_close_run")
    def test_close_calls_session_close(self, mock_run, capsys):
        mock_run.return_value = {}

        args = argparse.Namespace(resume=False)
        result = harness.cmd_close(args)

        assert result == 0
        mock_run.assert_called_once_with(resume=False)

    @patch("harness.runtime.harness.session_close_run")
    def test_close_resume_calls_with_resume_true(self, mock_run, capsys):
        mock_run.return_value = {}

        args = argparse.Namespace(resume=True)
        result = harness.cmd_close(args)

        assert result == 0
        mock_run.assert_called_once_with(resume=True)

    @patch("harness.runtime.harness.session_close_run")
    def test_close_handles_exception(self, mock_run, capsys):
        mock_run.side_effect = RuntimeError("Step failed")

        args = argparse.Namespace(resume=False)
        result = harness.cmd_close(args)

        assert result == 1
        captured = capsys.readouterr()
        assert "failed" in captured.out


class TestMain:
    """Tests for main entry point."""

    def test_gate_command_parsed(self):
        with patch.object(harness, "cmd_gate", return_value=0) as mock:
            result = harness.main(["gate", "--phase", "pre-task", "--input", "test"])
            mock.assert_called_once()
        assert result == 0

    def test_route_command_parsed(self):
        with patch.object(harness, "cmd_route", return_value=0) as mock:
            result = harness.main(["route", "--input", "test"])
            mock.assert_called_once()
        assert result == 0

    def test_checkpoint_command_parsed(self):
        with patch.object(harness, "cmd_checkpoint", return_value=0) as mock:
            result = harness.main(["checkpoint", "--task", "test"])
            mock.assert_called_once()
        assert result == 0

    def test_close_command_parsed(self):
        with patch.object(harness, "cmd_close", return_value=0) as mock:
            result = harness.main(["close"])
            mock.assert_called_once()
        assert result == 0

    def test_close_resume_command_parsed(self):
        with patch.object(harness, "cmd_close", return_value=0) as mock:
            result = harness.main(["close", "--resume"])
            mock.assert_called_once()
        assert result == 0

    def test_unknown_command_shows_help(self, capsys):
        with patch("sys.argv", ["harness.py", "unknown"]):
            try:
                result = harness.main()
            except SystemExit:
                result = 1
        assert result == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])