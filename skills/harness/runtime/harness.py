"""CLI Entry Point — wires together all runtime scripts."""

import argparse
import sys
from pathlib import Path

from .state import detect_mode, read_state, init_state
from .conductor import route
from .mistakes import check_relevant
from .checkpoint import run_checkpoint
from .session_close import run_close as session_close_run
from .memory_watch import check_staleness

WORKSPACE_ROOT = Path(__file__).parent.parent.parent.parent


def _print_gate_header(phase: str) -> None:
    print("=" * 60)
    print(f"GATE: {phase.upper()}")
    print("=" * 60)


def _print_boot_status(mode: str) -> None:
    state = read_state()
    session_id = state.get("session_id", "none")
    print(f"  Mode    : {mode.upper()}")
    print(f"  Session : {session_id}")


def _check_memory_staleness() -> list[dict]:
    results = check_staleness()
    stale = [r for r in results if r["status"] in ("STALE", "MISSING")]
    if stale:
        print()
        print("  WARNING: Memory files are stale or missing:")
        for r in stale:
            status_icon = "!" if r["status"] == "STALE" else "?"
            print(f"    [{status_icon}] {r['file']}: {r['status']} (age={r['age_minutes']})")
    return stale


def _gate_pre_task(task_input: str) -> int:
    """Run pre-task gate checks."""
    _print_gate_header("pre-task")

    mode = detect_mode()
    _print_boot_status(mode)

    print()
    print("  [1/5] Mode detection...")
    print(f"        Mode: {mode.upper()}")
    if mode == "quick":
        print("        Note: FULL harness not active (no .memory/)")

    print()
    print("  [2/5] Memory staleness check...")
    if mode == "full":
        stale = _check_memory_staleness()
        if stale:
            print("        WARNING: Stale memory may cause inaccurate routing.")
        else:
            print("        OK: Memory files are fresh.")
    else:
        print("        SKIPPED: QUICK mode")

    print()
    print("  [3/5] Checking relevant mistakes...")
    relevant = check_relevant(task_input)
    if relevant:
        print(f"        Found {len(relevant)} relevant mistake(s):")
        for entry in relevant[:3]:
            print(f"          - {entry['error'][:60]}")
            print(f"            Lesson: {entry['lesson'][:60]}")
    else:
        print("        No relevant mistakes found.")

    print()
    print("  [4/5] Routing task...")
    routed_skill = route(task_input)
    if routed_skill:
        print(f"        Skill: {routed_skill.get('id', 'unknown')}")
        print(f"        Path:  {routed_skill.get('skill_path', 'N/A')}")
        if routed_skill.get("disambiguation_warning"):
            print(f"        WARNING: {routed_skill['disambiguation_warning']}")
    else:
        print("        No skill matched.")

    print()
    print("  [5/5] Verification status...")
    state = read_state()
    verification_logged = state.get("verification_logged", False)
    if verification_logged:
        print("        OK: verification_logged = True")
    else:
        print("        WARNING: verification_logged = False")
        print("        You must run verification-before-completion after completing the task.")

    print()
    print("=" * 60)
    print("GATE DECISION")
    print("=" * 60)
    print(f"  Task    : {task_input}")
    print(f"  Mode    : {mode.upper()}")
    if routed_skill:
        print(f"  Route   : {routed_skill.get('id', 'unknown')}")
        print("  Decision: PROCEED")
    else:
        print("  Route   : none")
        print("  Decision: PROCEED (no skill matched, but no block)")
    print("=" * 60)

    return 0


def cmd_gate(args: argparse.Namespace) -> int:
    """Handle gate subcommand."""
    if args.phase == "pre-task":
        return _gate_pre_task(args.input or "")
    else:
        print(f"Unknown gate phase: {args.phase}")
        return 1


def cmd_route(args: argparse.Namespace) -> int:
    """Handle route subcommand."""
    if not args.input:
        print("Error: --input is required")
        return 1

    mode = detect_mode()
    print(f"Routing: {args.input}")
    print(f"Mode: {mode.upper()}")

    skill = route(args.input)
    if skill:
        print(f"Skill: {skill.get('id', 'unknown')}")
        print(f"Path: {skill.get('skill_path', 'N/A')}")
        if skill.get("disambiguation_warning"):
            print(f"Warning: {skill['disambiguation_warning']}")
        return 0
    else:
        print("No skill matched.")
        return 1


def cmd_checkpoint(args: argparse.Namespace) -> int:
    """Handle checkpoint subcommand."""
    state = read_state()
    task_description = args.task or "Untitled task"
    run_checkpoint(state, task_description)
    return 0


def cmd_close(args: argparse.Namespace) -> int:
    """Handle close subcommand."""
    try:
        session_close_run(resume=args.resume)
        return 0
    except Exception as e:
        print(f"Session close failed: {e}")
        if args.resume:
            print("Use --resume to retry from last failed step.")
        return 1


def main(argv: list[str] = None) -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        prog="harness.py",
        description="Antigravity harness CLI — session management and routing"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    gate_parser = subparsers.add_parser("gate", help="Pre-task gate check")
    gate_parser.add_argument("--phase", default="pre-task", help="Gate phase (default: pre-task)")
    gate_parser.add_argument("--input", help="Task input string")

    route_parser = subparsers.add_parser("route", help="Route task to skill")
    route_parser.add_argument("--input", required=True, help="Task input string")

    checkpoint_parser = subparsers.add_parser("checkpoint", help="Run checkpoint")
    checkpoint_parser.add_argument("--task", help="Task description")

    close_parser = subparsers.add_parser("close", help="Close session")
    close_parser.add_argument("--resume", action="store_true", help="Resume from last step")

    try:
        args = parser.parse_args(argv)
    except SystemExit:
        return 1

    if args.command == "gate":
        return cmd_gate(args)
    elif args.command == "route":
        return cmd_route(args)
    elif args.command == "checkpoint":
        return cmd_checkpoint(args)
    elif args.command == "close":
        return cmd_close(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))