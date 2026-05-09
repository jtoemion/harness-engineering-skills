"""State management for Antigravity runtime."""

import json
import os
from pathlib import Path
from datetime import datetime, timezone

RUNTIME_DIR = Path(__file__).parent
STATE_FILE = RUNTIME_DIR / ".harness-state.json"
WORKSPACE_ROOT = Path(__file__).parent.parent.parent.parent


def detect_mode() -> str:
    """Detect whether running in QUICK or FULL mode based on .memory/ presence."""
    memory_dir = WORKSPACE_ROOT / ".memory"
    return "full" if memory_dir.exists() else "quick"


def read_state() -> dict:
    """Read current state from .harness-state.json."""
    if not STATE_FILE.exists():
        return {}
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def write_state(state: dict) -> None:
    """Write state to .harness-state.json."""
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


def init_state(mode: str = None) -> dict:
    """Initialize new state with session_id and timestamps."""
    if mode is None:
        mode = detect_mode()
    now = datetime.now(timezone.utc)
    session_id = now.strftime("%Y-%m-%d-%H%M")
    state = {
        "session_id": session_id,
        "mode": mode,
        "state": "ACTIVE",
        "boot_time": now.isoformat(),
        "last_checkpoint": None,
        "mistakes_checked": False,
        "verification_logged": False,
        "skills_loaded": [],
        "routing_log": [],
        "ill_captures_since_synthesis": 0,
        "close_step": None
    }
    write_state(state)
    return state
