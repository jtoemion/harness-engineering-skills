"""
Shared incident logging for harness pipelines.
"""
import hashlib
import json
import traceback
from datetime import datetime
from pathlib import Path

from .state import HarnessState

_RUNTIME_DIR = Path(__file__).parent


def _find_workspace_root() -> Path:
    """Find the workspace root by looking for .memory/ or .git/ markers."""
    candidates = [Path.cwd()]
    if (_RUNTIME_DIR.parent.parent.parent / ".memory").exists():
        candidates.append(_RUNTIME_DIR.parent.parent.parent)
    for candidate in candidates:
        if (candidate / ".memory").exists() or (candidate / ".git").exists():
            return candidate
    return candidates[0]


WORKSPACE_ROOT = _find_workspace_root()


def _write_incident(
    state: HarnessState,
    step_name: str,
    error: Exception,
    pipeline: str = "unknown",
    step_index: int = -1,
) -> Path | None:
    """Write incident record to .memory/incidents/. Returns path or None."""
    incidents_dir = WORKSPACE_ROOT / ".memory" / "incidents"
    try:
        incidents_dir.mkdir(parents=True, exist_ok=True)
    except Exception:
        return None

    timestamp = datetime.now().strftime("%Y-%m-%d-%H%M")
    error_type = type(error).__name__
    hash4 = hashlib.md5(f"{error_type}{step_name}".encode()).hexdigest()[:4]
    filename = f"{timestamp}-{step_name}-{hash4}.json"

    incident = {
        "timestamp": datetime.now().isoformat(),
        "pipeline": pipeline,
        "step_name": step_name,
        "step_index": step_index,
        "error_type": error_type,
        "error_message": str(error),
        "traceback": traceback.format_exc(),
        "state_snapshot": {
            "session_id": state.session_id,
            "mode": state.mode,
            "state": state.state,
            "skills_loaded": state.skills_loaded,
            "checkpoint_complete": getattr(state, "checkpoint_complete", None),
            "mistakes_checked": getattr(state, "mistakes_checked", None),
            "boot_receipt": state.boot_receipt is not None if hasattr(state, "boot_receipt") else None,
        },
        "recovery": {
            "attempted": False,
            "method": None,
            "succeeded": None,
        },
    }

    try:
        filepath = incidents_dir / filename
        filepath.write_text(json.dumps(incident, indent=2, default=str), encoding="utf-8")
        return filepath
    except Exception:
        return None