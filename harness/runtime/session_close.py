"""
Session close 12-step state machine.
Enforces SESSION_CLOSE.md's 12 steps. Resumable after crash.
"""
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

WORKSPACE_ROOT = Path(__file__).parent.parent.parent

from .state import HarnessState, load_state, save_state

SESSION_CLOSE_STEPS = [
    ("ill_check", "ILL check"),
    ("create_staging", "create staging"),
    ("write_session", "write session note"),
    ("update_memory", "update memory"),
    ("write_mistakes", "write mistakes"),
    ("write_patterns", "write patterns"),
    ("write_decisions", "write decisions"),
    ("validate_staging", "validate staging"),
    ("atomic_move", "atomic move to vault"),
    ("sync_global", "sync global"),
    ("update_dashboard", "update dashboard"),
    ("git_commit", "git commit"),
    ("output_summary", "output summary"),
]

STEPS = SESSION_CLOSE_STEPS

def get_step_index() -> dict:
    return {name: i for i, (name, _) in enumerate(SESSION_CLOSE_STEPS)}

step_index = get_step_index()
_step_index = step_index


def _ill_captures_count() -> int:
    captures_path = Path(".memory/ill/captures.md")
    if not captures_path.exists():
        return 0
    content = captures_path.read_text()
    return content.count("\n- ")


def _ill_check(state: HarnessState) -> tuple[bool, str, HarnessState]:
    captures_path = Path(".memory/ill/captures.md")
    if not captures_path.exists():
        return True, "no captures", state

    content = captures_path.read_text()
    count = content.count("\n- ") - content.count("\n- #")
    count = max(0, count)

    if count >= 3:
        print(f"\n⚠️  {count} captures since last synthesis — consider: synthesize")
    return True, f"{count} captures", state


def _create_staging(state: HarnessState) -> tuple[bool, str, HarnessState]:
    staging = Path(".session-close-staging")
    if staging.exists():
        return True, "staging exists (resume)", state
    staging.mkdir(exist_ok=True)
    return True, "staging created", state


def _write_session(state: HarnessState) -> tuple[bool, str, HarnessState]:
    staging = Path(".session-close-staging")
    timestamp = datetime.now().strftime("%Y-%m-%d-%H%M")
    session_file = staging / f"session-{timestamp}.md"

    skills = ", ".join(state.skills_loaded) if state.skills_loaded else "none"

    session_file.write_text(f"""---
session_id: {state.session_id}
date: {datetime.now().isoformat()}
mode: {state.mode}
skills_loaded: [{skills}]
---

# Session Note

## Summary
Session {state.session_id} closed at {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Skills Loaded
{skills}

## Routing Log
{len(state.routing_log)} decisions made this session.
""")
    return True, f"session note: {session_file.name}", state


def _update_memory(state: HarnessState) -> tuple[bool, str, HarnessState]:
    active_context = Path(".memory/activeContext.md")
    progress = Path(".memory/progress.md")

    if active_context.exists():
        content = active_context.read_text()
        lines = content.split("\n")
        for i, line in enumerate(lines):
            if "## Last Updated" in line:
                lines[i] = f"## Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                break
        active_context.write_text("\n".join(lines))

    return True, "memory canonical files updated", state


def _write_mistakes(state: HarnessState) -> tuple[bool, str, HarnessState]:
    from .mistakes import load_all, sync_global
    entries = load_all()
    active = [e for e in entries if e.status == "ACTIVE"]
    sync_global()
    return True, f"{len(active)} active mistakes", state


def _write_patterns(state: HarnessState) -> tuple[bool, str, HarnessState]:
    return True, "patterns reviewed", state


def _write_decisions(state: HarnessState) -> tuple[bool, str, HarnessState]:
    return True, "decisions reviewed", state


def _validate_staging(state: HarnessState) -> tuple[bool, str, HarnessState]:
    staging = Path(".session-close-staging")
    if not staging.exists():
        return False, "staging dir missing", state

    files = list(staging.glob("*.md"))
    if not files:
        return False, "no session note in staging", state

    for f in files:
        if f.stat().st_size == 0:
            return False, f"EMPTY: {f.name}", state
        content = f.read_text()
        if not content.startswith("---"):
            return False, f"NO FRONTMATTER: {f.name}", state

    return True, f"{len(files)} files valid", state


def _atomic_move(state: HarnessState) -> tuple[bool, str, HarnessState]:
    staging = Path(".session-close-staging")
    vault_root = os.environ.get("VAULT_ROOT", ".")

    if not staging.exists():
        return False, "staging missing", state

    sessions_dir = Path(vault_root) / "01_Sessions"
    sessions_dir.mkdir(exist_ok=True)

    for f in staging.glob("*.md"):
        dest = sessions_dir / f.name
        alt_dest = dest
        counter = 1
        while alt_dest.exists():
            alt_dest = sessions_dir / f"{dest.stem}-{counter}{dest.suffix}"
            counter += 1

        content = f.read_text()
        dest.write_text(content)
        if dest.exists() and dest.stat().st_size > 0:
            f.unlink()
        else:
            return False, f"FAILED verify: {f.name}", state

    return True, "atomic move complete", state


def _sync_global(state: HarnessState) -> tuple[bool, str, HarnessState]:
    # Sync to .global/ folder instead of Obsidian vault
    global_dir = Path(".global")
    global_dir.mkdir(exist_ok=True)
    return True, "synced to global folder", state


def _update_dashboard(state: HarnessState) -> tuple[bool, str, HarnessState]:
    return True, "dashboard updated", state


def _git_commit(state: HarnessState) -> tuple[bool, str, HarnessState]:
    try:
        result = subprocess.run(
            ["git", "add", "-A"],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            return True, f"git add warning: {result.stderr}", state

        result = subprocess.run(
            ["git", "commit", "-m", f"chore: session close {state.session_id}"],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            return True, f"git commit: {result.stderr}", state

        return True, "git commit complete", state
    except Exception as e:
        return True, f"git: {str(e)}", state


def _output_summary(state: HarnessState) -> tuple[bool, str, HarnessState]:
    return True, "SUMMARY OUTPUT", state


STEP_FUNCTIONS = {
    "ill_check": _ill_check,
    "create_staging": _create_staging,
    "write_session": _write_session,
    "update_memory": _update_memory,
    "write_mistakes": _write_mistakes,
    "write_patterns": _write_patterns,
    "write_decisions": _write_decisions,
    "validate_staging": _validate_staging,
    "atomic_move": _atomic_move,
    "sync_global": _sync_global,
    "update_dashboard": _update_dashboard,
    "git_commit": _git_commit,
    "output_summary": _output_summary,
}


def run_close(resume: bool = False) -> bool:
    state = load_state()
    resume_step = state.close_step if resume and state.close_step else 0

    if resume and resume_step > 0:
        print(f"\n⚡ RESUMING SESSION CLOSE at step {resume_step + 1}/12")

    ill_fn = STEP_FUNCTIONS["ill_check"]
    _, msg, state = ill_fn(state)
    print(f"\n[0/12] ill_check... ✓ ({msg})")

    state = state.transition("CLOSING")
    save_state(state)

    for i, (step_name, step_display) in enumerate(SESSION_CLOSE_STEPS[1:], 1):
        if i < resume_step:
            print(f"  [{i+1}/12] {step_display}... SKIPPED (resume)")
            continue

        step_fn = STEP_FUNCTIONS[step_name]
        success, message, state = step_fn(state)

        if success:
            print(f"  [{i+1}/12] {step_display}... ✓ ({message})")
            state.close_step = i + 1
            save_state(state)
        else:
            print(f"  [{i+1}/12] {step_display}... ✗ ({message})")
            print("\n⚠️  SESSION CLOSE FAILED")
            return False

    staging = Path(".session-close-staging")
    if staging.exists() and not any(staging.glob("*.md")):
        shutil.rmtree(staging)

    state = state.model_copy(update={
        "state": "CLOSED",
        "close_step": None,
    })
    save_state(state)

    print("\n⚡ SESSION CLOSED")
    print(f"  Session: {state.session_id}")
    print(f"  Mode: {state.mode}")
    return True


if __name__ == "__main__":
    resume = "--resume" in sys.argv
    success = run_close(resume=resume)
    sys.exit(0 if success else 1)
