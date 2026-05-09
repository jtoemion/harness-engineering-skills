from datetime import datetime
from pathlib import Path
from typing import Literal

import pydantic

SessionState = Literal["BOOTING", "ACTIVE", "CHECKPOINTING", "CLOSING", "CLOSED"]
Mode = Literal["quick", "full"]
GateDecision = Literal["PASS", "WARN", "BLOCK"]

WORKSPACE_ROOT = Path(__file__).parent.parent.parent.parent
STATE_FILE = WORKSPACE_ROOT / ".harness-state.json"

VALID_TRANSITIONS: dict[SessionState, list[SessionState]] = {
    "BOOTING": ["ACTIVE"],
    "ACTIVE": ["CHECKPOINTING", "CLOSING"],
    "CHECKPOINTING": ["ACTIVE", "CLOSING"],
    "CLOSING": ["CLOSED"],
    "CLOSED": [],
}


class InvalidTransitionError(Exception):
    pass


class HarnessState(pydantic.BaseModel):
    session_id: str
    mode: Mode
    state: SessionState = "BOOTING"
    boot_time: datetime
    last_checkpoint: datetime | None = None
    mistakes_checked: bool = False
    verification_logged: bool = False
    checkpoint_complete: bool = False
    skills_loaded: list[str] = pydantic.Field(default_factory=list)
    routing_log: list[dict] = pydantic.Field(default_factory=list)
    close_step: int | None = None
    ill_captures_since_synthesis: int = 0
    _pending_route: str | None = None
    _llm_verdict: dict | None = None

    def transition(self, new_state: SessionState) -> None:
        if new_state not in VALID_TRANSITIONS.get(self.state, []):
            raise InvalidTransitionError(
                f"Cannot transition from {self.state} to {new_state}"
            )
        self.state = new_state


def detect_mode() -> str:
    """Detect mode by checking for .memory/ directory."""
    return "full" if (WORKSPACE_ROOT / ".memory").exists() else "quick"


def init_state() -> HarnessState:
    """Create and save a fresh HarnessState."""
    state = HarnessState(
        session_id=datetime.now().strftime("%Y-%m-%d-%H%M"),
        mode=detect_mode(),
        state="BOOTING",
        boot_time=datetime.now(),
    )
    save(state, str(STATE_FILE))
    return state


def read_state() -> dict:
    """Read state file as plain dict (for checkpoint/session_close compatibility)."""
    if not STATE_FILE.exists():
        return {}
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        import json
        return json.load(f)


def write_state(state: dict) -> None:
    """Write state dict to file (for checkpoint/session_close compatibility)."""
    import json
    import os
    import tempfile

    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", delete=False, suffix=".tmp"
    ) as tmp:
        json.dump(state, tmp, indent=2, default=str)
        tmp_path = tmp.name
    os.replace(tmp_path, STATE_FILE)


def load(path: str) -> HarnessState:
    import json

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return HarnessState.model_validate(data)


def save(state: HarnessState, path: str) -> None:
    import json
    import os
    import tempfile

    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", delete=False, suffix=".tmp"
    ) as tmp:
        json.dump(state.model_dump(mode="json"), tmp, indent=2, default=str)
        tmp_path = tmp.name
    os.replace(tmp_path, path)
