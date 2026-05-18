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
load_state = state_mod.load_state  # Use wrapper that has default path
save_state = state_mod.save_state  # Use wrapper that has default path
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
    # Use WORKSPACE_ROOT as cwd so Path.cwd() returns the project dir
    result = subprocess.run(cmd, cwd=str(WORKSPACE_ROOT), env=env)
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


def _check_incident_patterns() -> list[dict]:
    """Scan incidents for recurring patterns. Returns list of pattern dicts."""
    incidents_dir = WORKSPACE_ROOT / ".memory" / "incidents"
    if not incidents_dir.exists():
        return []

    required_fields = {"step_name", "error_type", "error_message", "timestamp"}
    incidents = []
    for f in incidents_dir.glob("*.json"):
        try:
            inc = json.loads(f.read_text(encoding="utf-8"))
            if all(k in inc for k in required_fields):
                incidents.append(inc)
        except Exception:
            pass

    if not incidents:
        return []

    from collections import Counter
    step_counts = Counter(inc["step_name"] for inc in incidents)

    patterns = []
    for step_name, count in step_counts.items():
        if count >= 2:
            examples = [inc for inc in incidents if inc["step_name"] == step_name]
            latest = max(examples, key=lambda x: x["timestamp"])
            patterns.append({
                "step_name": step_name,
                "count": count,
                "error_types": list(set(inc["error_type"] for inc in examples)),
                "latest_error": latest["error_message"],
                "latest_timestamp": latest["timestamp"],
                "data_loss_risk": latest.get("data_loss_risk", "UNKNOWN"),
            })

    return patterns


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
    # Incident count
    incidents_dir = WORKSPACE_ROOT / ".memory" / "incidents"
    if incidents_dir.exists():
        incident_count = len(list(incidents_dir.glob("*.json")))
        if incident_count > 0:
            print(f"  Incidents: {incident_count} on record")
            # Check for recurring incident patterns
            if incident_count >= 2:
                patterns = _check_incident_patterns()
                if patterns:
                    print(f"  ⚠️ Recurring failures detected:")
                    for p in patterns:
                        print(f"    {p['step_name']}: {p['count']}x — {p['error_types'][0]}")
                        print(f"      Latest: {p['latest_error'][:80]}")
                    print(f"    >>> Consider adding to MISTAKES.md if not already tracked")
    if mode == "full" and state.boot_receipt:
        print(f"  Boot Receipt : {state.boot_receipt.get('mistakes_loaded', 0)} mistakes, {state.boot_receipt.get('patterns_loaded', 0)} patterns, {state.boot_receipt.get('variables_loaded', 0)} variables")
    print(f"  Harness : LOADED +")
    print(f"  Project : {state.session_id}")
    print(f"  Task    : N/A")
    print(f"  Next    : N/A")
    print()


def _generate_boot_receipt() -> dict:
    """Generate boot receipt with counts of loaded knowledge files."""
    receipt = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "mistakes_loaded": 0,
        "patterns_loaded": 0,
        "variables_loaded": 0,
        "files_read": []
    }
    
    mem_dir = WORKSPACE_ROOT / ".memory"
    
    mistakes_file = mem_dir / "mistakes.json"
    if mistakes_file.exists():
        try:
            data = json.loads(mistakes_file.read_text(encoding="utf-8"))
            receipt["mistakes_loaded"] = len(data.get("mistakes", []))
            receipt["files_read"].append("mistakes.json")
        except Exception:
            pass
    
    patterns_file = mem_dir / "patterns.json"
    if patterns_file.exists():
        try:
            data = json.loads(patterns_file.read_text(encoding="utf-8"))
            receipt["patterns_loaded"] = len(data.get("patterns", []))
            receipt["files_read"].append("patterns.json")
        except Exception:
            pass
    
    variables_file = mem_dir / "variables.json"
    if variables_file.exists():
        try:
            data = json.loads(variables_file.read_text(encoding="utf-8"))
            receipt["variables_loaded"] = len(data.get("variables", []))
            receipt["files_read"].append("variables.json")
        except Exception:
            pass
    
    # Legacy systemPatterns.md — no longer used, JSON knowledge graph is source of truth
    # Kept as optional receipt entry for backward compatibility during migration
    system_patterns = mem_dir / "systemPatterns.md"
    if system_patterns.exists():
        receipt["files_read"].append("systemPatterns.md (legacy)")
    
    return receipt


def _flush_quick_buffer() -> None:
    """Flush Quick mode buffer into sessions.json at Full mode boot."""
    home = Path.home()
    buffer_file = home / ".memory" / "quick-buffer.jsonl"
    if not buffer_file.exists():
        return
    
    try:
        lines = buffer_file.read_text(encoding="utf-8").strip().split("\n")
        entries = []
        for line in lines:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except Exception:
                    pass
        
        if entries:
            sessions_file = WORKSPACE_ROOT / ".memory" / "sessions.json"
            if sessions_file.exists():
                try:
                    data = json.loads(sessions_file.read_text(encoding="utf-8"))
                    existing = data.get("sessions", [])
                    existing.extend(entries)
                    data["sessions"] = existing
                    data["updated"] = datetime.now(timezone.utc).isoformat()
                    sessions_file.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
                except Exception:
                    pass
            print(f"  Flushed {len(entries)} Quick mode session(s) into sessions.json")
        
        buffer_file.unlink()
    except Exception:
        pass


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

    _bootstrap_json_knowledge()

    _flush_quick_buffer()

    # Generate and store boot receipt
    receipt = _generate_boot_receipt()
    state.boot_receipt = receipt
    write_state(state)
    
    # Write receipt file
    receipt_file = WORKSPACE_ROOT / ".memory" / "boot-receipt.json"
    if (WORKSPACE_ROOT / ".memory").exists():
        receipt_file.write_text(json.dumps(receipt, indent=2, default=str), encoding="utf-8")
        print(f"  Boot receipt written: {receipt['mistakes_loaded']} mistakes, {receipt['patterns_loaded']} patterns, {receipt['variables_loaded']} variables")

    check_staleness()

    try:
        from runtime.bridge import QwenBridge
        bridge = QwenBridge.get()
        _ = bridge.ask("warmup", {"ping": "pong"})
    except Exception:
        pass

    _print_boot_status_report(mode, state)
    return 0


def _bootstrap_json_knowledge():
    """Create JSON schema if missing in FULL mode."""
    mem_dir = WORKSPACE_ROOT / ".memory"
    if not mem_dir.exists():
        return
        
    knowledge_file = mem_dir / "knowledge.json"
    if not knowledge_file.exists():
        knowledge_file.write_text('{"version":"1.0","project":{},"indexes":{}}', encoding="utf-8")
        print("  WARN: No knowledge graph. Creating empty skeleton.")
        
    mistakes_file = mem_dir / "mistakes.json"
    if not mistakes_file.exists():
        mistakes_file.write_text('{"version":"1.0","mistakes":[]}', encoding="utf-8")
        print("  WARN: No mistakes file. Creating empty skeleton.")
        
    patterns_file = mem_dir / "patterns.json"
    if not patterns_file.exists():
        patterns_file.write_text('{"version":"1.0","patterns":[]}', encoding="utf-8")
        print("  WARN: No patterns file. Creating empty skeleton.")
        
    variables_file = mem_dir / "variables.json"
    if not variables_file.exists():
        variables_file.write_text('{"version":"1.0","variables":[]}', encoding="utf-8")
        print("  WARN: No variables file. Creating empty skeleton.")


def _check_project_knowledge(task_input: str) -> tuple[list[dict], list[dict]]:
    """Check project JSON knowledge graph for relevant mistakes and patterns."""
    mistakes = []
    patterns = []
    if not task_input:
        return mistakes, patterns
        
    words = set(task_input.lower().split())
    
    mistakes_file = WORKSPACE_ROOT / ".memory" / "mistakes.json"
    if mistakes_file.exists():
        try:
            data = json.loads(mistakes_file.read_text(encoding="utf-8"))
            for m in data.get("mistakes", []):
                text = f"{m.get('error', '')} {m.get('lesson', '')}".lower()
                entry_words = set(text.split())
                if len(entry_words) < 3:
                    continue  # Skip entries too short to score meaningfully
                overlap = len(words & entry_words)
                score = overlap / len(entry_words)
                if score > 0.15:
                    mistakes.append(m)
        except Exception:
            pass

    patterns_file = WORKSPACE_ROOT / ".memory" / "patterns.json"
    if patterns_file.exists():
        try:
            data = json.loads(patterns_file.read_text(encoding="utf-8"))
            for p in data.get("patterns", []):
                text = f"{p.get('pattern', '')} {p.get('prevention', '')}".lower()
                entry_words = set(text.split())
                if len(entry_words) < 3:
                    continue  # Skip entries too short to score meaningfully
                overlap = len(words & entry_words)
                score = overlap / len(entry_words)
                if score > 0.15:
                    patterns.append(p)
        except Exception:
            pass

    return mistakes, patterns


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

    proj_mistakes, proj_patterns = _check_project_knowledge(task_input)
    if proj_mistakes or proj_patterns:
        print()
        print("  PROJECT KNOWLEDGE MATCHES:")
        for m in proj_mistakes[:3]:
            print(f"    [MISTAKE] {m.get('error', '')[:80]}")
            print(f"      Lesson: {m.get('lesson', '')[:100]}")
        for p in proj_patterns[:3]:
            print(f"    [PATTERN] {p.get('pattern', '')[:80]}")
            print(f"      Prevention: {p.get('prevention', '')[:100]}")
        print()
        print("  >>> ACTION REQUIRED: You MUST explicitly acknowledge and incorporate")
        print("  >>> these lessons into your plan BEFORE execution. Do not ignore them.")
        print()

    # Generate pasteable Pitfalls block for subagent briefs
    if proj_mistakes:
        print()
        print("  SUBAGENT PITFALLS (paste into brief):")
        print("  ┌─────────────────────────────────────────")
        for m in proj_mistakes[:5]:
            mid = m.get('id', '?')
            lesson = m.get('lesson', '')[:120]
            print(f"  │ - [{mid}] {lesson}")
        print("  └─────────────────────────────────────────")

    # Permission error diagnosis protocol
    permission_keywords = {"permission", "firebase", "firestore", "auth", "uid", "security rules", "access denied", "insufficient permissions", "getrealuserid", "anonymous"}
    task_words = set(task_input.lower().split()) if task_input else set()
    if task_words & permission_keywords:
        print()
        print("  PERMISSION ERROR DIAGNOSIS PROTOCOL (mandatory):")
        print("    1. Identify WHICH collection is being accessed")
        print("    2. Identify WHICH operation (read/write/create/delete)")
        print("    3. Check WHICH user ID is being used (uid vs actualUserId vs getRealUserId())")
        print("    4. Verify security rules match the operation and user ID")
        print("    5. For anonymous proxy auth: ensure getRealUserId() resolution is consistent")
        print()
        print("  >>> This checklist is MANDATORY for any task touching auth/permissions/Firestore.")
        print()
        
    relevant = check_relevant(task_input)
    if relevant:
        print()
        print(f"  GLOBAL RELEVANT MISTAKES ({len(relevant)}):")
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
        warnings.append(f"{len(relevant)} global mistake(s) found")
    if proj_mistakes or proj_patterns:
        warnings.append(f"{len(proj_mistakes)} project mistake(s) and {len(proj_patterns)} pattern(s) found")

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
        # Check boot receipt
        if not state.boot_receipt:
            print("  BLOCK: No boot receipt found for this session")
            print("  Run: harness boot")
            print("=" * 60)
            return 1
        
        # Check knowledge was consulted
        if not state.mistakes_checked:
            print("  BLOCK: mistakes_checked = False")
            print("  Run: harness gate --phase pre-task --input 'your task'")
            print("=" * 60)
            return 1
        
        # Check if JSON knowledge files were updated since boot
        if state.boot_time:
            import os
            knowledge_updated = False
            for kf in ("mistakes.json", "patterns.json"):
                kf_path = WORKSPACE_ROOT / ".memory" / kf
                if kf_path.exists():
                    mod_time = datetime.fromtimestamp(os.path.getmtime(kf_path), tz=timezone.utc)
                    if mod_time > state.boot_time:
                        knowledge_updated = True
                        break
            if not knowledge_updated:
                print("  WARN: No mistakes or patterns logged since boot")
                print("  Consider running retrospective before closing (writes to mistakes.json/patterns.json)")

        # Check for unprocessed incident patterns
        incident_patterns = _check_incident_patterns()
        if incident_patterns:
            print(f"  WARN: {len(incident_patterns)} recurring incident pattern(s) detected")
            for p in incident_patterns:
                print(f"    {p['step_name']}: {p['count']}x — consider promoting to MISTAKES.md")

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
