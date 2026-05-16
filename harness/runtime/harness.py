"""Antigravity Harness — Master CLI entry point."""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

_RUNTIME_DIR = Path(__file__).parent

# WORKSPACE_ROOT: project root (contains .memory/ or .git/)
# Default to cwd if run from project, else fall back to parent of skills/
def _find_workspace_root() -> Path:
    """Find the workspace root by looking for .memory/ or .git/ markers."""
    # Start from cwd or from runtime dir parent chain
    candidates = [Path.cwd()]
    # Also check if opencode config dir is the parent of skills/harness
    if (_RUNTIME_DIR.parent.parent.parent / ".memory").exists():
        candidates.append(_RUNTIME_DIR.parent.parent.parent)
    for candidate in candidates:
        if (candidate / ".memory").exists() or (candidate / ".git").exists():
            return candidate
    # Fallback to first candidate (cwd)
    return candidates[0]

WORKSPACE_ROOT = _find_workspace_root()
STATE_FILE = WORKSPACE_ROOT / ".harness-state.json"

import importlib.util

def _import_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module

state_mod = _import_module("runtime.state", _RUNTIME_DIR / "state.py")
HarnessState = state_mod.HarnessState
state_load = state_mod.load
state_save = state_mod.save
load_state = state_load
save_state = state_save
detect_mode = state_mod.detect_mode
init_state = state_mod.init_state
read_state_dict = state_mod.read_state
write_state_dict = state_mod.write_state

conductor_mod = _import_module("runtime.conductor", _RUNTIME_DIR / "conductor.py")
route = conductor_mod.route
RouteResult = conductor_mod.RouteResult

mistakes_mod = _import_module("runtime.mistakes", _RUNTIME_DIR / "mistakes.py")
check_relevant = mistakes_mod.check_relevant
mark_resolved = mistakes_mod.mark_resolved
mistakes_load_all = mistakes_mod.load_all

memory_watch_mod = _import_module("runtime.memory_watch", _RUNTIME_DIR / "memory_watch.py")
check_staleness = memory_watch_mod.check_staleness


def read_state() -> HarnessState:
    """Load HarnessState from file."""
    if not STATE_FILE.exists():
        return _create_fresh_state()
    return state_load(str(STATE_FILE))


def write_state(state: HarnessState) -> None:
    """Save HarnessState to file."""
    state_save(state, str(STATE_FILE))


def _create_fresh_state() -> HarnessState:
    """Create a fresh HarnessState."""
    return HarnessState(
        session_id=datetime.now(timezone.utc).strftime("%Y-%m-%d-%H%M"),
        mode=detect_mode(),
        state="BOOTING",
        boot_time=datetime.now(timezone.utc),
    )


def _check_session_close_staging() -> bool:
    """Check .session-close-staging/ for interrupted close. Returns True if found."""
    staging = WORKSPACE_ROOT / "00_Memory" / ".session-close-staging"
    return staging.exists() and any(staging.iterdir())


def _run_script(script_name: str, *args) -> int:
    """Run a Python script as subprocess and return exit code."""
    script_path = _RUNTIME_DIR / script_name
    # Use PYTHONPATH to allow runtime.* imports (must use forward slashes for Python)
    env = os.environ.copy()
    runtime_parent = str(_RUNTIME_DIR.parent).replace("\\", "/")  # skills/harness/
    env["PYTHONPATH"] = runtime_parent
    # Ensure UTF-8 output for Unicode characters (Windows fix)
    env["PYTHONIOENCODING"] = "utf-8"
    # Run as module via -m so relative imports (.state) work within the runtime package
    script_module = f"runtime.{script_path.stem}"
    cmd = [sys.executable, "-m", script_module] + list(args)
    result = subprocess.run(cmd, cwd=str(_RUNTIME_DIR), env=env)
    return result.returncode


def _parse_stale_output(lines: list[str]) -> tuple[list[dict], bool]:
    """Parse check_staleness string output into structured dicts."""
    results = []
    has_stale = False
    for line in lines:
        if line.startswith("MISSING:"):
            results.append({"file": line.split(":", 1)[1].strip(), "status": "MISSING", "age_minutes": None})
        elif line.startswith("STALE"):
            parts = line.split(":")
            file = parts[1].strip() if len(parts) > 1 else "unknown"
            age_str = line.split("(")[1].split("m)")[0] if "(" in line else "0"
            results.append({"file": file, "status": "STALE", "age_minutes": int(age_str)})
            has_stale = True
        elif line.endswith(": OK"):
            results.append({"file": line.split(":")[0].strip(), "status": "OK", "age_minutes": 0})
    return results, has_stale


def _print_boot_status_report(mode: str, state: HarnessState) -> None:
    """Print Boot Status Report in exact format."""
    memory_status = "WARM" if (WORKSPACE_ROOT / ".memory").exists() else "N/A"
    if mode == "full":
        raw_stale = check_staleness()
        stale_results, has_stale = _parse_stale_output(raw_stale)
        if has_stale or any(r["status"] in ("STALE", "MISSING") for r in stale_results):
            memory_status = "STALE"
        elif stale_results and all(r["status"] == "OK" for r in stale_results):
            memory_status = "WARM"

    print()
    print("= ONLINE")
    print(f"  Agent   : Antigravity [harness]")
    print(f"  Time    : {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')}")
    print(f"  Mode    : {mode.upper()}")
    print(f"  Memory  : {memory_status}")
    print(f"  Harness : LOADED +")
    print(f"  Project : {state.session_id}")
    print(f"  Task    : N/A")
    print(f"  Next    : N/A")
    print()


def cmd_boot() -> int:
    """FULL mode only: Initialize harness state."""
    mode = detect_mode()

    if _check_session_close_staging():
        print()
        print("[RECOVERY] Interrupted session close detected.")
        print("  Staging preserved at 00_Memory/.session-close-staging/")
        print("  Use: harness close --resume")
        print()

    if mode == "quick":
        print("QUICK mode — harness not active")
        return 0

    state = _create_fresh_state()
    state.state = "ACTIVE"  # Transition from BOOTING to ACTIVE
    write_state(state)

    check_staleness()

    try:
        from runtime.bridge import QwenBridge
        bridge = QwenBridge.get()
        _ = bridge.ask("warmup", {"ping": "pong"})
    except Exception:
        pass

    _print_boot_status_report(mode, state)
    return 0


def _gate_pre_task(task_input: str) -> tuple[int, RouteResult | None]:
    """Run pre-task gate checks. Returns (exit_code, RouteResult)."""
    state = load_state()
    mode = detect_mode()

    print("=" * 60)
    print("GATE: PRE-TASK")
    print("=" * 60)
    print(f"  Mode: {mode.upper()}")

    if mode == "full":
        raw_stale = check_staleness()
        stale_results, has_stale = _parse_stale_output(raw_stale)
        stale_files = [r for r in stale_results if r["status"] in ("STALE", "MISSING")]
        if stale_files:
            print()
            print("  WARNING: Memory files are stale or missing:")
            for r in stale_files:
                print(f"    {r['file']}: {r['status']} (age={r['age_minutes']})")

    relevant = check_relevant(task_input)
    if relevant:
        print()
        print(f"  RELEVANT MISTAKES ({len(relevant)}):")
        for entry in relevant[:3]:
            print(f"    - [{entry.date}] {entry.error[:50]}")
            print(f"      Lesson: {entry.lesson[:50]}")

    result = route(task_input, mode)
    state.mistakes_checked = True
    write_state(state)

    skill_path = result.skill_path
    warnings = []
    if result.gate == "BLOCKED":
        warnings.append("FULL mode required but QUICK mode active")
    if relevant:
        warnings.append(f"{len(relevant)} relevant mistake(s) found")

    print()
    print(f"  Skill: {skill_path}")
    if warnings:
        for w in warnings:
            print(f"  WARNING: {w}")
    print("=" * 60)

    gate_exit = 1 if result.gate == "BLOCKED" else 0
    return gate_exit, result


def cmd_gate(args: argparse.Namespace) -> int:
    """Handle gate subcommand."""
    if args.phase == "pre-task":
        exit_code, _ = _gate_pre_task(args.input or "")
        return exit_code
    elif args.phase == "pre-complete":
        state = load_state()
        print("=" * 60)
        print("GATE: PRE-COMPLETE")
        print("=" * 60)
        if not state.verification_logged:
            print("  BLOCK: verification_logged = False")
            print("  Run: harness verify-done")
            print("=" * 60)
            return 1
        if not state.checkpoint_complete:
            print("  BLOCK: checkpoint_complete = False")
            print("  Run: harness checkpoint --task '...'")
            print("=" * 60)
            return 1
        print("  PASS")
        print("=" * 60)
        return 0
    else:
        print(f"Unknown gate phase: {args.phase}")
        return 1


def cmd_verify_done() -> int:
    """Sets state.verification_logged = True."""
    state = load_state()
    state.verification_logged = True
    write_state(state)
    print("verification_logged = True")
    return 0


def cmd_checkpoint(args: argparse.Namespace) -> int:
    """Run checkpoint 12-step pipeline via subprocess."""
    state = load_state()
    state.checkpoint_complete = False
    write_state(state)

    ret = _run_script("checkpoint.py", "--task", args.task or "Untitled task")

    state = load_state()
    state.checkpoint_complete = True
    write_state(state)
    return ret


def cmd_close(args: argparse.Namespace) -> int:
    """Run session close 12-step pipeline via subprocess."""
    cmd = ["close"]
    if args.resume:
        cmd.append("--resume")
    ret = _run_script("session_close.py", *cmd)
    if ret == 0:
        state = load_state()
        state.state = "CLOSED"
        write_state(state)
    return ret


def cmd_mistakes(args: argparse.Namespace) -> int:
    """Handle mistakes list / resolve commands."""
    if args.action == "list":
        try:
            entries = mistakes_load_all()
        except Exception:
            print("MISTAKES.md not found or parse error")
            return 1
        active = [e for e in entries if e.status == "ACTIVE"]
        print(f"ACTIVE mistakes: {len(active)}")
        for e in active:
            print(f"  [{e.date}] {e.error[:60]}")
            print(f"    Cause: {e.cause[:60]}")
            print(f"    Lesson: {e.lesson[:60]}")
        return 0
    elif args.action == "resolve":
        try:
            mark_resolved(args.date)
            print(f"Marked RESOLVED: {args.date}")
            return 0
        except Exception as e:
            print(f"Error: {e}")
            return 1
    else:
        print(f"Unknown mistakes action: {args.action}")
        return 1


def cmd_status() -> int:
    """Print Boot Status Report."""
    mode = detect_mode()
    if STATE_FILE.exists():
        state = state_load(str(STATE_FILE))
    else:
        state = _create_fresh_state()
    _print_boot_status_report(mode, state)
    return 0


def cmd_hook_check_session() -> int:
    """Internal git hook check. Exit 1 if state != CLOSED."""
    if not STATE_FILE.exists():
        return 0
    state = state_load(str(STATE_FILE))
    if state.state != "CLOSED":
        print("Session not closed")
        return 1
    return 0


def main(argv: list[str] = None) -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        prog="harness",
        description="Antigravity harness CLI"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("boot", help="Boot harness (FULL mode)")

    gate_parser = subparsers.add_parser("gate", help="Gate check")
    gate_parser.add_argument("--phase", default="pre-task", help="pre-task or pre-complete")
    gate_parser.add_argument("--input", help="Task input string")

    subparsers.add_parser("verify-done", help="Mark verification complete")

    checkpoint_parser = subparsers.add_parser("checkpoint", help="Run checkpoint")
    checkpoint_parser.add_argument("--task", help="Task description")

    close_parser = subparsers.add_parser("close", help="Close session")
    close_parser.add_argument("--resume", action="store_true", help="Resume from last step")

    mistakes_parser = subparsers.add_parser("mistakes", help="Mistakes commands")
    mistakes_sub = mistakes_parser.add_subparsers(dest="action", required=True)
    mistakes_sub.add_parser("list", help="List active mistakes")
    mistakes_resolve = mistakes_sub.add_parser("resolve", help="Resolve a mistake")
    mistakes_resolve.add_argument("date", help="Date string YYYY-MM-DD")

    subparsers.add_parser("status", help="Print boot status report")

    subparsers.add_parser("_hook-check-session", help="Internal git hook check")

    try:
        args = parser.parse_args(argv)
    except SystemExit:
        return 1

    if args.command == "boot":
        return cmd_boot()
    elif args.command == "gate":
        return cmd_gate(args)
    elif args.command == "verify-done":
        return cmd_verify_done()
    elif args.command == "checkpoint":
        return cmd_checkpoint(args)
    elif args.command == "close":
        return cmd_close(args)
    elif args.command == "mistakes":
        return cmd_mistakes(args)
    elif args.command == "status":
        return cmd_status()
    elif args.command == "_hook-check-session":
        return cmd_hook_check_session()
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
