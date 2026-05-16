"""Conductor - Routing engine that replaces passive YAML reading."""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional
import yaml

SKILLS_ROOT = Path(__file__).parent.parent.parent
ROUTER_YAML = SKILLS_ROOT / "skill-router.yaml"


@dataclass
class RouteResult:
    skill_id: str
    skill_path: str
    confidence: float
    gate: str
    reason: str
    needs_disambiguation: bool = False


_ROUTES: list[dict] = []
_SKILLS: dict[str, dict] = {}
_STATE_FILE = Path(__file__).parent / ".routing_state.yaml"
_router_cache = {}


def _load_router():
    global _ROUTES, _SKILLS
    with open(ROUTER_YAML, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    _ROUTES = data.get("routing", [])
    _SKILLS = data.get("skills", {})
    return data


_load_router()

load_router = _load_router


def mode_guard_check(skill_id: str, current_mode: str) -> bool:
    """If skill requires FULL and mode is QUICK → BLOCK immediately."""
    skill = _SKILLS.get(skill_id, {})
    required_mode = skill.get("mode", "QUICK")
    if required_mode == "FULL" and current_mode == "QUICK":
        return False
    return True


def _extract_keywords(text: str) -> set:
    text = text.lower()
    import re
    words = re.findall(r"\b\w+\b", text)
    stopwords = {"a", "the", "in", "on", "at", "to", "for", "of", "and", "or", "is", "are", "was", "were", "be", "been", "being", "have", "has", "had", "do", "does", "did", "will", "would", "could", "should", "may", "might", "must", "shall", "can", "need", "dare", "ought", "used", "it", "its", "this", "that", "these", "those", "i", "you", "he", "she", "we", "they", "what", "which", "who", "whom", "whose", "where", "when", "why", "how", "all", "each", "every", "both", "few", "more", "most", "other", "some", "such", "no", "nor", "not", "only", "own", "same", "so", "than", "too", "very", "s", "t", "just", "don", "now", "user", "says", "say", "said"}
    filtered = [w for w in words if w not in stopwords and len(w) > 2]
    return set(filtered)


def _keyword_match(query: str, pattern: str) -> tuple[bool, int]:
    query_kw = _extract_keywords(query)
    pattern_kw = _extract_keywords(pattern)
    if not query_kw or not pattern_kw:
        return False, 0
    match = query_kw.intersection(pattern_kw)
    if match:
        score = min(100, len(match) * 30)
        return True, score
    return False, 0


def _check_mode_guard(skill: dict, mode: str) -> tuple[bool, str]:
    req = skill.get("mode_required", skill.get("mode", "quick")).upper()
    if req == "FULL" and mode.lower() == "quick":
        return False, f"Skill requires FULL mode but current mode is QUICK"
    return True, "OK"


def _check_disambiguation_warning(skills: list) -> str | None:
    if len(skills) < 2:
        return None
    sorted_skills = sorted(skills, key=lambda x: x.get("weight", 0), reverse=True)
    w1 = sorted_skills[0].get("weight", 0)
    w2 = sorted_skills[1].get("weight", 0)
    if abs(w1 - w2) <= 10:
        return f"⚠️ Multiple skills ({sorted_skills[0]['id']}, {sorted_skills[1]['id']}) are within 10 weight points."
    return None


def get_skill_path(skill_id: str) -> str:
    """Return the path to the skill file."""
    # Look in routing table for the skill_path
    for route in _ROUTES:
        if route.get("id") == skill_id:
            return route.get("skill_path", "")
    return ""


def _yaml_keyword_fallback(user_input: str) -> tuple[Optional[str], float]:
    """Fallback routing via YAML condition matching."""
    user_lower = user_input.lower()
    best_match = None
    best_weight = 0

    for route in _ROUTES:
        condition = route.get("condition", "")
        weight = route.get("weight", 0)
        skill_id = route.get("id", "")

        # Extract quoted phrases from condition for matching
        import re
        phrases = re.findall(r"'([^']+)'", condition)

        matched = False
        for phrase in phrases:
            phrase_lower = phrase.lower()
            if phrase_lower in user_lower:
                matched = True
                break
            # Also check partial word matches for simple keywords
            words = phrase_lower.split()
            if all(w in user_lower for w in words if len(w) > 2):
                matched = True
                break

        if matched and weight > best_weight:
            best_weight = weight
            best_match = skill_id

    if best_match:
        return best_match, 0.5
    return None, 0.0


def _disambiguation(skill1: str, skill2: str, w1: int, w2: int) -> Optional[str]:
    """Print structured choice and block until human resolves."""
    s1_desc = _SKILLS.get(skill1, {}).get("description", "")
    s2_desc = _SKILLS.get(skill2, {}).get("description", "")

    print("\nAMBIGUOUS ROUTING")
    print(f"  Input matched: {skill1} (weight {w1}) and {skill2} (weight {w2})")
    print(f"  {skill1} = [{s1_desc}]")
    print(f"  {skill2} = [{s2_desc}]")

    while True:
        choice = input("  Which applies? [1/2]: ").strip()
        if choice == "1":
            return skill1
        elif choice == "2":
            return skill2


def _check_auto_fire(user_input: str) -> Optional[str]:
    """Auto-fire skills when conditions met."""
    auto_fire = {
        "dev-journey-log": ["feature", "fix", "refactor", "update", "add", "remove"],
        "scope-guard": ["feature", "fix", "refactor", "update", "add", "remove"],
    }
    for skill_id, triggers in auto_fire.items():
        if any(t in user_input.lower() for t in triggers):
            return skill_id
    return None


def _write_routing_state(result: RouteResult):
    """Write routing decision to state."""
    state = {
        "skill_id": result.skill_id,
        "skill_path": result.skill_path,
        "confidence": result.confidence,
        "gate": result.gate,
        "reason": result.reason,
        "needs_disambiguation": result.needs_disambiguation,
    }
    with open(_STATE_FILE, "w", encoding="utf-8") as f:
        yaml.safe_dump(state, f)


def route(user_input: str, current_mode: str = "QUICK") -> RouteResult:
    """Main routing pipeline."""
    # LLM classification disabled - using keyword-based routing only
    classify_with_qwen = None

    auto_skill = _check_auto_fire(user_input)
    if auto_skill:
        path = get_skill_path(auto_skill)
        return RouteResult(
            skill_id=auto_skill,
            skill_path=path,
            confidence=1.0,
            gate="AUTO",
            reason=f"Auto-triggered by keyword match",
            needs_disambiguation=False,
        )

    if classify_with_qwen:
        skill_id, confidence = classify_with_qwen(user_input)
        if skill_id and confidence >= 0.65:
            if not mode_guard_check(skill_id, current_mode):
                return RouteResult(
                    skill_id=skill_id,
                    skill_path=get_skill_path(skill_id),
                    confidence=confidence,
                    gate="BLOCKED",
                    reason="FULL mode required but QUICK mode active",
                    needs_disambiguation=False,
                )
            path = get_skill_path(skill_id)
            result = RouteResult(
                skill_id=skill_id,
                skill_path=path,
                confidence=confidence,
                gate="LLM",
                reason="Qwen classification",
                needs_disambiguation=False,
            )
            _write_routing_state(result)
            print(f"\n[CONDUCTOR] -> {path}")
            return result

    fallback_skill, fallback_conf = _yaml_keyword_fallback(user_input)
    if fallback_skill:
        if not mode_guard_check(fallback_skill, current_mode):
            return RouteResult(
                skill_id=fallback_skill,
                skill_path=get_skill_path(fallback_skill),
                confidence=fallback_conf,
                gate="BLOCKED",
                reason="FULL mode required but QUICK mode active",
                needs_disambiguation=False,
            )
        path = get_skill_path(fallback_skill)
        result = RouteResult(
            skill_id=fallback_skill,
            skill_path=path,
            confidence=fallback_conf,
            gate="YAML",
            reason="YAML keyword fallback",
            needs_disambiguation=False,
        )
        _write_routing_state(result)
        print(f"\n[CONDUCTOR] -> {path}")
        return result

    return RouteResult(
        skill_id="",
        skill_path="",
        confidence=0.0,
        gate="NONE",
        reason="No matching skill found",
        needs_disambiguation=False,
    )


def disambiguation_route(skill1: str, skill2: str, w1: int, w2: int) -> RouteResult:
    """Handle disambiguation case where two skills are within 10 weight points."""
    chosen = _disambiguation(skill1, skill2, w1, w2)
    path = get_skill_path(chosen)
    result = RouteResult(
        skill_id=chosen,
        skill_path=path,
        confidence=1.0,
        gate="DISAMBIGUATION",
        reason=f"Human selected {chosen}",
        needs_disambiguation=False,
    )
    _write_routing_state(result)
    print(f"\n[CONDUCTOR] -> {path}")
    return result
