"""PHASE2 Checkpoint Enforcer — blocks completion claims until verification runs."""

import os
import shutil
import yaml
from datetime import datetime, timezone
from pathlib import Path

from .state import STATE_FILE, read_state, write_state

WORKSPACE_ROOT = Path(__file__).parent.parent.parent.parent
GLOBAL_VAULT = os.environ.get(
    "ANTIGRAVITY_GLOBAL_VAULT",
    Path.home() / "Obsidian" / "AntigravityV"
)

STEPS = [
    ("update_active_context", "Update activeContext.md"),
    ("update_progress",      "Update progress.md"),
    ("update_tech_context",   "Update tech_context.md"),
    ("write_session_note",    "Write session note"),
    ("append_sessions_log",   "Append to sessions.log"),
    ("write_mistakes",        "Write mistake notes"),
    ("write_patterns",        "Write pattern notes"),
    ("update_dashboard",      "Update Dashboard.md"),
    ("sync_global",           "Sync to GLOBAL_VAULT"),
]


def _get_session_id() -> str:
    state = read_state()
    return state.get("session_id", datetime.now(timezone.utc).strftime("%Y-%m-%d-%H%M"))


def _update_active_context(state: dict, task_description: str) -> None:
    memory_dir = WORKSPACE_ROOT / ".memory"
    if not memory_dir.exists():
        return
    active_context_path = memory_dir / "activeContext.md"
    now = datetime.now(timezone.utc)
    entry = f"\n## [{now.isoformat()}] Checkpoint\n- Task: {task_description}\n"
    if active_context_path.exists():
        active_context_path.write_text(
            active_context_path.read_text(encoding="utf-8") + entry,
            encoding="utf-8"
        )
    else:
        active_context_path.write_text(entry, encoding="utf-8")


def _update_progress(state: dict, task_description: str) -> None:
    memory_dir = WORKSPACE_ROOT / ".memory"
    if not memory_dir.exists():
        return
    progress_path = memory_dir / "progress.md"
    now = datetime.now(timezone.utc)
    entry = f"\n## [{now.isoformat()}] Checkpoint: {task_description}\n"
    if progress_path.exists():
        progress_path.write_text(
            progress_path.read_text(encoding="utf-8") + entry,
            encoding="utf-8"
        )
    else:
        progress_path.write_text(entry, encoding="utf-8")


def _update_tech_context(state: dict, task_description: str) -> None:
    memory_dir = WORKSPACE_ROOT / ".memory"
    if not memory_dir.exists():
        return
    tech_path = memory_dir / "tech_context.md"
    now = datetime.now(timezone.utc)
    entry = f"\n## [{now.isoformat()}] Checkpoint\n- Task: {task_description}\n"
    if tech_path.exists():
        tech_path.write_text(
            tech_path.read_text(encoding="utf-8") + entry,
            encoding="utf-8"
        )
    else:
        tech_path.write_text(entry, encoding="utf-8")


def _write_session_note(state: dict, task_description: str) -> None:
    session_id = _get_session_id()
    memory_dir = WORKSPACE_ROOT / ".memory"
    if not memory_dir.exists():
        return
    now = datetime.now(timezone.utc)
    content = f"""---
type: checkpoint
date: {now.isoformat()}
task: {task_description}
session: {session_id}
---
# Checkpoint: {task_description}

**Session**: {session_id}
**Time**: {now.isoformat()}
"""
    (memory_dir / "session_note.md").write_text(content, encoding="utf-8")


def _append_sessions_log(state: dict, task_description: str) -> None:
    sessions_log = WORKSPACE_ROOT / "00_Memory" / "sessions.log"
    sessions_log.parent.mkdir(parents=True, exist_ok=True)
    session_id = _get_session_id()
    now = datetime.now(timezone.utc)
    line = f"{now.isoformat()} | CHECKPOINT | {session_id} | {task_description}\n"
    sessions_log.write_text(
        sessions_log.read_text(encoding="utf-8") + line
        if sessions_log.exists() else line,
        encoding="utf-8"
    )


def _write_mistakes(state: dict, task_description: str) -> None:
    pass


def _write_patterns(state: dict, task_description: str) -> None:
    pass


def _update_dashboard(state: dict, task_description: str) -> None:
    staging = WORKSPACE_ROOT / "00_Memory" / ".session-close-staging"
    dashboard_src = staging / "04_Index" / "Dashboard.md" if staging.exists() else None
    dashboard_dest = WORKSPACE_ROOT / "04_Index" / "Dashboard.md"
    if dashboard_src and dashboard_src.exists():
        shutil.copy2(dashboard_src, dashboard_dest)


def _sync_global(state: dict, task_description: str) -> None:
    global_vault = Path(GLOBAL_VAULT)
    if not global_vault.exists():
        return
    session_id = _get_session_id()
    now = datetime.now(timezone.utc)
    global_checkpoints = global_vault / "00_Global" / "Checkpoints"
    global_checkpoints.mkdir(parents=True, exist_ok=True)
    content = f"""---
type: checkpoint
date: {now.isoformat()}
session: {session_id}
---
# Global Checkpoint: {session_id}

**Time**: {now.isoformat()}
"""
    (global_checkpoints / f"{session_id}-checkpoint.md").write_text(content, encoding="utf-8")


STEP_HANDLERS = {
    "update_active_context": lambda s, td: _update_active_context(s, td),
    "update_progress":       lambda s, td: _update_progress(s, td),
    "update_tech_context":   lambda s, td: _update_tech_context(s, td),
    "write_session_note":    lambda s, td: _write_session_note(s, td),
    "append_sessions_log":   lambda s, td: _append_sessions_log(s, td),
    "write_mistakes":        lambda s, td: _write_mistakes(s, td),
    "write_patterns":        lambda s, td: _write_patterns(s, td),
    "update_dashboard":      lambda s, td: _update_dashboard(s, td),
    "sync_global":           lambda s, td: _sync_global(s, td),
}


def run_checkpoint(state: dict, task_description: str) -> dict:
    """Run all checkpoint steps and reset verification_logged.

    Enforces PHASE2: must run verification-before-completion after checkpoint.
    """
    state["checkpoint_complete"] = True

    for step_name, step_desc in STEPS:
        handler = STEP_HANDLERS.get(step_name)
        if handler:
            handler(state, task_description)

    state["verification_logged"] = False
    state["last_checkpoint"] = datetime.now(timezone.utc).isoformat()
    write_state(state)

    print("=" * 60)
    print("CHECKPOINT COMPLETE")
    print("=" * 60)
    print(f"  Session: {_get_session_id()}")
    print(f"  Task:    {task_description}")
    print()
    print("  WARNING: verification_logged = False")
    print("  You must run verification-before-completion")
    print("  before claiming task completion.")
    print("=" * 60)

    return state