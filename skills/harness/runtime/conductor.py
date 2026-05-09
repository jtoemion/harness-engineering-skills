"""Live Skill Router — parses skill-router.yaml directly."""

import re
from pathlib import Path
from typing import Optional

import yaml

from .state import detect_mode, read_state, write_state

ROUTER_PATH = Path(__file__).parent.parent.parent.parent / "skills" / "skill-router.yaml"
_router_cache: Optional[dict] = None


def load_router() -> dict:
    """Load and parse skill-router.yaml."""
    global _router_cache
    if _router_cache is not None:
        return _router_cache

    with open(ROUTER_PATH, "r", encoding="utf-8") as f:
        _router_cache = yaml.safe_load(f)
    return _router_cache


def _extract_keywords(condition: str) -> list[str]:
    """Extract meaningful keywords from condition string."""
    condition = condition.lower()
    keywords = re.findall(r"\b\w+\b", condition)
    stopwords = {
        "a", "an", "the", "or", "and", "in", "on", "at", "to", "for", "of", "with",
        "by", "is", "are", "was", "were", "be", "been", "being", "have", "has", "had",
        "do", "does", "did", "will", "would", "could", "should", "may", "might",
        "must", "shall", "can", "need", "dare", "ought", "used", "that", "this",
        "these", "those", "it", "its", "i", "you", "he", "she", "we", "they",
        "what", "which", "who", "whom", "when", "where", "why", "how",
        "if", "then", "else", "when", "while", "about", "into", "through",
        "during", "before", "after", "above", "below", "up", "down", "out",
        "off", "over", "under", "again", "further", "once", "any", "no", "not",
        "only", "own", "same", "so", "than", "too", "very", "just", "also",
        "now", "here", "there", "from", "up", "down", "in", "out", "as", "but",
        "user", "says", "explicitly", "types", "something", "all", "both",
        "each", "few", "more", "most", "other", "some", "such", "no", "nor",
        "not", "only", "own", "same", "so", "than", "too", "very", "s",
    }
    return [k for k in keywords if len(k) > 2 and k not in stopwords]


def _get_quoted_phrases(condition: str) -> list[str]:
    """Extract quoted phrases from condition."""
    return [m.group(1) or m.group(2) for m in re.finditer(r"'([^']+)'|\"([^\"]+)\"", condition)]


def _keyword_match(task_input: str, condition: str) -> tuple[bool, int]:
    """Check if task_input matches condition. Returns (matched, match_score)."""
    task_lower = task_input.lower()
    condition_lower = condition.lower()

    quoted = _get_quoted_phrases(condition_lower)
    for phrase in quoted:
        if phrase.strip() in task_lower:
            return True, 100

    or_parts = condition_lower.split("or")
    for part in or_parts:
        part = part.strip()
        part_quoted = _get_quoted_phrases(part)
        for pq in part_quoted:
            if pq.strip() in task_lower:
                return True, 80

        part_keywords = _extract_keywords(part)
        if len(part_keywords) >= 2:
            matches = sum(1 for kw in part_keywords if kw in task_lower)
            threshold = max(1, int(len(part_keywords) * 0.3))
            if matches >= threshold:
                return True, 60 + matches
        elif len(part_keywords) == 1:
            if part_keywords[0] in task_lower:
                return True, 70

    keywords = _extract_keywords(condition_lower)
    match_count = sum(1 for kw in keywords if kw in task_lower)

    if len(keywords) >= 4:
        threshold = max(1, int(len(keywords) * 0.3))
        if match_count >= threshold:
            return True, match_count
    elif 2 <= len(keywords) <= 3:
        if match_count >= max(1, int(len(keywords) * 0.3)):
            return True, match_count
    elif len(keywords) == 1:
        if keywords[0] in task_lower:
            return True, 5

    return False, 0


def _check_mode_guard(skill: dict, current_mode: str) -> tuple[bool, str]:
    """Check if mode guard blocks this skill. Returns (allowed, reason)."""
    mode_required = skill.get("mode_required", "any")

    if mode_required == "full" and current_mode == "quick":
        return False, f"Skill '{skill['id']}' requires FULL mode. Blocked in QUICK mode."

    if mode_required == "both":
        return True, ""

    return True, ""


def _check_disambiguation_warning(matched_skills: list[dict]) -> Optional[str]:
    """Check for disambiguation warnings between skills within 10 weight points."""
    if len(matched_skills) < 2:
        return None

    for i, skill_a in enumerate(matched_skills):
        for skill_b in matched_skills[i + 1:]:
            weight_diff = abs(skill_a.get("weight", 0) - skill_b.get("weight", 0))
            if weight_diff <= 10:
                return (
                    f"WARNING: Skills '{skill_a['id']}' (weight {skill_a.get('weight', 0)}) "
                    f"and '{skill_b['id']}' (weight {skill_b.get('weight', 0)}) are within "
                    f"10 weight points. Consider disambiguation."
                )
    return None


def route(task_input: str) -> dict:
    """Route task to skill via first-match with weight resolution.

    Returns skill dict or empty dict if no match.
    """
    router = load_router()
    routing_table = router.get("routing", [])
    current_mode = detect_mode()

    matched_candidates = []

    for skill in routing_table:
        condition = skill.get("condition", "")
        matched, match_score = _keyword_match(task_input, condition)

        if matched:
            allowed, reason = _check_mode_guard(skill, current_mode)
            if allowed:
                matched_candidates.append((skill, match_score))

    if not matched_candidates:
        return {}

    matched_candidates.sort(key=lambda x: (x[1], x[0].get("weight", 0)), reverse=True)
    best_skill = matched_candidates[0][0]

    disambiguation_warning = _check_disambiguation_warning(
        [s[0] for s in matched_candidates[:3]]
    )

    routing_entry = {
        "skill_id": best_skill["id"],
        "skill_path": best_skill.get("skill_path", ""),
        "matched_on": task_input,
        "mode": current_mode,
        "disambiguation_warning": disambiguation_warning,
    }

    state = read_state()
    if "routing_log" not in state:
        state["routing_log"] = []
    state["routing_log"].append(routing_entry)
    write_state(state)

    return best_skill