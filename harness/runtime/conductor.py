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


def _load_router():
    global _ROUTES, _SKILLS
    with open(ROUTER_YAML, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    _ROUTES = data.get("ROUTES", [])
    _SKILLS = data.get("SKILLS", {})


_load_router()


def mode_guard_check(skill_id: str, current_mode: str) -> bool:
    """If skill requires FULL and mode is QUICK → BLOCK immediately."""
    skill = _SKILLS.get(skill_id, {})
    required_mode = skill.get("mode", "QUICK")
    if required_mode == "FULL" and current_mode == "QUICK":
        return False
    return True


def get_skill_path(skill_id: str) -> str:
    """Return the path to the skill file."""
    skill = _SKILLS.get(skill_id, {})
    return skill.get("path", "")


def _yaml_keyword_fallback(user_input: str) -> tuple[Optional[str], float]:
    """Fallback routing via YAML keyword matching."""
    user_lower = user_input.lower()
    best_match = None
    best_weight = 0

    for route in _ROUTES:
        keywords = route.get("keywords", [])
        for kw in keywords:
            if kw.lower() in user_lower:
                weight = route.get("weight", 0)
                if weight > best_weight:
                    best_weight = weight
                    best_match = route.get("skill_id")
                break

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
    try:
        from bridge import classify_with_qwen
    except ImportError:
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
            print(f"\n[CONDUCTOR] → {path}")
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
        print(f"\n[CONDUCTOR] → {path}")
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
    print(f"\n[CONDUCTOR] → {path}")
    return result
