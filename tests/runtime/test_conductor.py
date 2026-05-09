"""Tests for conductor.py — Live Skill Router."""

import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path

from skills.harness.runtime.conductor import (
    load_router,
    route,
    _extract_keywords,
    _keyword_match,
    _check_mode_guard,
    _check_disambiguation_warning,
    _router_cache,
)


class TestExtractKeywords:
    def test_basic_keywords(self):
        result = _extract_keywords("user says 'close session' or 'end session'")
        assert "close" in result
        assert "session" in result
        assert "end" in result

    def test_filters_short_words(self):
        result = _extract_keywords("a the in on at to for")
        assert len(result) == 0

    def test_filters_stopwords(self):
        result = _extract_keywords("user says hello world")
        assert "hello" in result
        assert "world" in result
        assert "says" not in result

    def test_handles_pipe_delimiter(self):
        result = _extract_keywords("bug encountered, test failure, unexpected behavior")
        assert "bug" in result
        assert "test" in result
        assert "failure" in result
        assert "unexpected" in result


class TestKeywordMatch:
    def test_exact_phrase_match(self):
        matched, score = _keyword_match("close session", "user says 'close session'")
        assert matched is True
        assert score == 100

    def test_partial_match(self):
        matched, score = _keyword_match("debug a bug in auth", "bug encountered")
        assert matched is True

    def test_no_match(self):
        matched, score = _keyword_match("random text", "user says 'close session'")
        assert matched is False


class TestModeGuard:
    def test_full_required_quick_mode_blocks(self):
        skill = {"id": "session-close", "mode_required": "full"}
        allowed, reason = _check_mode_guard(skill, "quick")
        assert allowed is False
        assert "requires FULL mode" in reason

    def test_full_required_full_mode_allows(self):
        skill = {"id": "session-close", "mode_required": "full"}
        allowed, reason = _check_mode_guard(skill, "full")
        assert allowed is True

    def test_any_mode_allows_both(self):
        skill = {"id": "test-review", "mode_required": "any"}
        assert _check_mode_guard(skill, "quick")[0] is True
        assert _check_mode_guard(skill, "full")[0] is True

    def test_quick_required_full_mode_allows(self):
        skill = {"id": "quick-skill", "mode_required": "quick"}
        allowed, _ = _check_mode_guard(skill, "full")
        assert allowed is True


class TestDisambiguationWarning:
    def test_no_warning_single_skill(self):
        skills = [{"id": "a", "weight": 100}]
        result = _check_disambiguation_warning(skills)
        assert result is None

    def test_no_warning_distant_weights(self):
        skills = [{"id": "a", "weight": 100}, {"id": "b", "weight": 80}]
        result = _check_disambiguation_warning(skills)
        assert result is None

    def test_warning_within_10_points(self):
        skills = [{"id": "a", "weight": 100}, {"id": "b", "weight": 95}]
        result = _check_disambiguation_warning(skills)
        assert result is not None
        assert "within 10 weight points" in result


class TestLoadRouter:
    def test_loads_yaml(self):
        router = load_router()
        assert isinstance(router, dict)
        assert "routing" in router
        assert "version" in router

    def test_caches_result(self):
        import skills.harness.runtime.conductor as conductor
        conductor._router_cache = None
        router1 = load_router()
        router2 = load_router()
        assert router1 is router2


class TestRoute:
    @patch("skills.harness.runtime.conductor.detect_mode")
    @patch("skills.harness.runtime.conductor.read_state")
    @patch("skills.harness.runtime.conductor.write_state")
    def test_route_close_session_full_mode(self, mock_write, mock_read, mock_detect):
        mock_detect.return_value = "full"
        mock_read.return_value = {"routing_log": []}

        result = route("close session")

        assert result["id"] == "session-close"
        assert result["mode_required"] == "full"
        mock_write.assert_called_once()

    @patch("skills.harness.runtime.conductor.detect_mode")
    def test_route_close_session_quick_mode_blocks(self, mock_detect):
        mock_detect.return_value = "quick"

        result = route("close session")

        assert result == {}

    @patch("skills.harness.runtime.conductor.detect_mode")
    @patch("skills.harness.runtime.conductor.read_state")
    @patch("skills.harness.runtime.conductor.write_state")
    def test_route_bug_in_auth(self, mock_write, mock_read, mock_detect):
        mock_detect.return_value = "quick"
        mock_read.return_value = {"routing_log": []}

        result = route("bug in auth")

        assert result["id"] == "systematic-debugging"
        mock_write.assert_called_once()

    @patch("skills.harness.runtime.conductor.detect_mode")
    @patch("skills.harness.runtime.conductor.read_state")
    @patch("skills.harness.runtime.conductor.write_state")
    def test_route_e2e_scaffold(self, mock_write, mock_read, mock_detect):
        mock_detect.return_value = "quick"
        mock_read.return_value = {"routing_log": []}

        result = route("set up e2e testing")

        assert result["id"] == "e2e-scaffold"

    @patch("skills.harness.runtime.conductor.detect_mode")
    @patch("skills.harness.runtime.conductor.read_state")
    @patch("skills.harness.runtime.conductor.write_state")
    def test_route_no_match(self, mock_write, mock_read, mock_detect):
        mock_detect.return_value = "quick"
        mock_read.return_value = {"routing_log": []}

        result = route("xyzabc123 random nonsense foobar")

        assert result == {}


if __name__ == "__main__":
    pytest.main([__file__, "-v"])