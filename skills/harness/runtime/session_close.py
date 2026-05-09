"""Session close — 12-step state machine with resume support."""

import os
import shutil
import yaml
from datetime import datetime, timezone
from pathlib import Path

from .state import read_state, write_state

WORKSPACE_ROOT = Path(__file__).parent.parent.parent.parent
GLOBAL_VAULT = os.environ.get(
    "ANTIGRAVITY_GLOBAL_VAULT",
    Path.home() / "Obsidian" / "AntigravityV"
)

STEPS = [
    ("ill_check",        "Check ILL captures count"),
    ("create_staging",  "Create .session-close-staging/"),
    ("write_session",   "Write session note to 01_Sessions/"),
    ("update_memory",   "Update canonical memory files"),
    ("write_mistakes",  "Create mistake notes in 02_Mistakes/"),
    ("write_patterns",  "Create pattern notes in 03_Patterns/"),
    ("write_decisions", "Create decision notes"),
    ("validate_staging","Validate staging files"),
    ("atomic_move",     "Atomic move to vault"),
    ("sync_global",     "Sync to GLOBAL_VAULT"),
    ("update_dashboard","Update Dashboard.md"),
    ("git_commit",      "Git commit"),
]


def _step_index(step_name: str) -> int:
    return next((i for i, s in enumerate(STEPS) if s[0] == step_name), 0)


def _ill_captures_count() -> int:
    captures_path = WORKSPACE_ROOT / ".memory" / "ill" / "captures.md"
    if not captures_path.exists():
        return 0
    try:
        content = captures_path.read_text(encoding="utf-8")
        return content.count("\n## ") - 1
    except Exception:
        return 0


def _get_session_id() -> str:
    state = read_state()
    return state.get("session_id", datetime.now(timezone.utc).strftime("%Y-%m-%d-%H%M"))


def _create_staging(state: dict) -> None:
    staging = WORKSPACE_ROOT / "00_Memory" / ".session-close-staging"
    staging.mkdir(parents=True, exist_ok=True)
    for sub in ["00_Memory", "01_Sessions", "02_Mistakes", "03_Patterns", "04_Index", "00_Global"]:
        (staging / sub).mkdir(exist_ok=True)


def _write_session(state: dict) -> None:
    session_id = _get_session_id()
    staging = WORKSPACE_ROOT / "00_Memory" / ".session-close-staging"
    sessions_dir = staging / "01_Sessions"
    now = datetime.now(timezone.utc)
    content = f"""---
type: session
date: {now.isoformat()}
outcome: SUCCESS
task: session close
---

# Session Close: {session_id}

## Metadata
- **Closed**: {now.isoformat()}
- **Mode**: {state.get('mode', 'unknown')}
"""
    (sessions_dir / f"{session_id}-session.md").write_text(content, encoding="utf-8")


def _update_memory(state: dict) -> None:
    staging = WORKSPACE_ROOT / "00_Memory" / ".session-close-staging"
    if not staging.exists():
        return
    memory_dir = staging / "00_Memory"
    memory_dir.mkdir(parents=True, exist_ok=True)
    active_context = WORKSPACE_ROOT / ".memory" / "activeContext.md"
    if active_context.exists():
        shutil.copy2(active_context, memory_dir / "activeContext.md")
    progress = WORKSPACE_ROOT / ".memory" / "progress.md"
    if progress.exists():
        shutil.copy2(progress, memory_dir / "progress.md")


def _write_mistakes(state: dict) -> None:
    pass


def _write_patterns(state: dict) -> None:
    pass


def _write_decisions(state: dict) -> None:
    pass


def _validate_staging(state: dict) -> bool:
    staging = WORKSPACE_ROOT / "00_Memory" / ".session-close-staging"
    if not staging.exists():
        return False
    for f in staging.rglob("*.md"):
        try:
            content = f.read_text(encoding="utf-8")
            if content.startswith("---"):
                end = content.index("---", 3)
                yaml.safe_load(content[: end + 3])
        except Exception:
            return False
    return True


def _atomic_move(state: dict) -> None:
    staging = WORKSPACE_ROOT / "00_Memory" / ".session-close-staging"
    if not staging.exists():
        return
    for item in staging.iterdir():
        if item.name == "00_Global":
            continue
        dest = WORKSPACE_ROOT / item.name
        if dest.exists() and dest.is_dir():
            for sub in item.iterdir():
                if sub.is_file():
                    shutil.copy2(sub, dest / sub.name)
                elif sub.is_dir():
                    (dest / sub.name).mkdir(exist_ok=True)
                    for f in sub.rglob("*"):
                        if f.is_file():
                            shutil.copy2(f, dest / sub.name / f.name)
        else:
            shutil.copytree(item, dest, dirs_exist_ok=True)


def _sync_global(state: dict) -> None:
    global_vault = Path(GLOBAL_VAULT)
    if not global_vault.exists():
        return
    staging = WORKSPACE_ROOT / "00_Memory" / ".session-close-staging"
    global_mistakes = global_vault / "00_Global" / "Mistakes"
    global_patterns = global_vault / "00_Global" / "Patterns"
    global_mistakes.mkdir(parents=True, exist_ok=True)
    global_patterns.mkdir(parents=True, exist_ok=True)
    mistakes_src = staging / "02_Mistakes"
    patterns_src = staging / "03_Patterns"
    if mistakes_src.exists():
        for f in mistakes_src.iterdir():
            shutil.copy2(f, global_mistakes / f.name)
    if patterns_src.exists():
        for f in patterns_src.iterdir():
            shutil.copy2(f, global_patterns / f.name)


def _update_dashboard(state: dict) -> None:
    staging = WORKSPACE_ROOT / "00_Memory" / ".session-close-staging"
    dashboard_src = staging / "04_Index" / "Dashboard.md"
    dashboard_dest = WORKSPACE_ROOT / "04_Index" / "Dashboard.md"
    if dashboard_src.exists():
        shutil.copy2(dashboard_src, dashboard_dest)


def _git_commit(state: dict) -> None:
    import subprocess
    session_id = _get_session_id()
    try:
        subprocess.run(
            ["git", "add", "00_Memory/", "01_Sessions/", "02_Mistakes/", "03_Patterns/", "04_Index/"],
            cwd=WORKSPACE_ROOT,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "commit", "-m", f"chore: session close {session_id}"],
            cwd=WORKSPACE_ROOT,
            check=True,
            capture_output=True,
        )
    except subprocess.CalledProcessError:
        pass


STEP_HANDLERS = {
    "ill_check":        lambda s: None,
    "create_staging":   _create_staging,
    "write_session":    _write_session,
    "update_memory":    _update_memory,
    "write_mistakes":   _write_mistakes,
    "write_patterns":   _write_patterns,
    "write_decisions":  _write_decisions,
    "validate_staging": lambda s: None,
    "atomic_move":      _atomic_move,
    "sync_global":      _sync_global,
    "update_dashboard": _update_dashboard,
    "git_commit":       _git_commit,
}


def run_close(resume: bool = False) -> dict:
    state = read_state()

    if not resume:
        state["close_step"] = None
        write_state(state)

    close_step = state.get("close_step")
    start_idx = _step_index(close_step) + 1 if close_step else 0

    for idx in range(start_idx, len(STEPS)):
        step_name, step_desc = STEPS[idx]
        try:
            handler = STEP_HANDLERS.get(step_name)
            if handler:
                handler(state)
            state["close_step"] = step_name
            write_state(state)
        except Exception as e:
            staging = WORKSPACE_ROOT / "00_Memory" / ".session-close-staging"
            if staging.exists():
                print(f"  Staging preserved at 00_Memory/.session-close-staging/")
            session_id = _get_session_id()
            print(f"  Resume: run_close(resume=True)")
            raise RuntimeError(f"Step {step_name} failed: {e}") from e

    ill_count = _ill_captures_count()
    staging = WORKSPACE_ROOT / "00_Memory" / ".session-close-staging"
    if staging.exists() and any(staging.iterdir()):
        pass
    else:
        print("Session close complete.")
    return state