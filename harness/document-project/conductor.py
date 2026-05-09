#!/usr/bin/env python3
"""
conductor.py — document-project skill conductor
Orchestrates the agent + enforcer loop. Ensures enforce.py is called at every
phase boundary. Detects non-compliance. Retries on failure.

Single-agent mode:  conductor calls enforce.py, pipes instructions to stdout
                    for the agent to read. Agent does work, calls enforce.py done.
                    Conductor monitors state progression.

Multi-agent mode:   conductor calls a configurable worker command (subprocess)
                    for each phase, injects only that phase's context, validates
                    the phase advanced, retries with failure injection if not.

Usage:
  # Monitor mode — conductor watches, agent is already running in same shell
  python conductor.py monitor --mode initial_scan --level deep

  # Orchestrate mode — conductor drives an agent subprocess per phase
  python conductor.py orchestrate --mode initial_scan --level deep \\
      --worker "gemini -p {prompt_file}" [--max-retries 3]

  # Status check — parse state and emit JSON summary
  python conductor.py status

Environment:
  ENFORCE_AGENT=1        passed through to enforce.py
  CONDUCTOR_WORKER_CMD   default worker command (overridden by --worker)
"""

import json
import os
import subprocess
import sys
import time
import tempfile
import argparse
from datetime import datetime, timezone
from pathlib import Path

# ── Constants ─────────────────────────────────────────────────────────────────

ENFORCE_CMD   = ["python", "enforce.py"]
STATE_FILE    = Path(".docs/.scan-state.json")
DOCS_DIR      = Path(".docs")
POLL_INTERVAL = 2.0    # seconds between state polls in monitor mode
POLL_TIMEOUT  = 600.0  # 10 min max wait per phase in monitor mode
MAX_RETRIES   = 3      # default max retries per phase in orchestrate mode

# ── Helpers ───────────────────────────────────────────────────────────────────

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def read_state() -> dict | None:
    if not STATE_FILE.exists():
        return None
    with open(STATE_FILE, encoding="utf-8") as f:
        return json.load(f)

def run_enforcer(*args, capture: bool = True) -> tuple[int, dict | str]:
    """
    Run enforce.py with --agent (JSON output).
    Returns (exit_code, parsed_json_or_raw_string).
    """
    cmd = ENFORCE_CMD + list(args) + ["--agent"]
    env = {**os.environ, "ENFORCE_AGENT": "1"}
    result = subprocess.run(cmd, capture_output=capture, text=True, env=env)
    if capture:
        try:
            return result.returncode, json.loads(result.stdout)
        except json.JSONDecodeError:
            return result.returncode, result.stdout
    return result.returncode, {}

def enforcer_phase_ids(mode: str) -> list[str]:
    """Return expected phase IDs for a given mode without calling enforce.py."""
    if mode == "deep_dive":
        return [f"step_{i}" for i in range(1, 7)]
    return [f"phase_{i}" for i in range(1, 7)]

def emit(msg: str):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[conductor {ts}] {msg}", flush=True)

def emit_json(obj: dict):
    print(json.dumps(obj, ensure_ascii=False), flush=True)

# ── Compliance injection ───────────────────────────────────────────────────────

COMPLIANCE_INJECTION = """\
⚠️  COMPLIANCE FAILURE — enforce.py was not called

You completed work but did not call:
  python enforce.py done {phase} --agent

This is REQUIRED by the document-project protocol. The enforcer must validate your
output before you are allowed to proceed.

Call it now — before doing anything else:
  python enforce.py done {phase} --agent

If it exits 1: read the FAIL lines, fix the exact issue, retry.
If it exits 0: you will receive the next phase instructions.
Do NOT proceed until this returns exit 0.
"""

RETRY_INJECTION = """\
⚠️  PHASE {phase} FAILED VALIDATION (attempt {attempt}/{max_retries})

The enforcer reported these failures:
{failures}

Fix the above issues in the output file, then retry:
  python enforce.py done {phase} --agent

Do NOT call done until you have fixed every FAIL item listed above.
"""

# ── Monitor mode ──────────────────────────────────────────────────────────────
# Use when the agent is already running interactively and you want the conductor
# to watch state progression and inject compliance messages when needed.

def cmd_monitor(args):
    mode  = args.mode
    level = args.level
    force = args.force

    emit(f"Starting in monitor mode | mode={mode} level={level}")

    # Start enforcer
    force_flag = ["--force"] if force else []
    code, out = run_enforcer("start", "--mode", mode, "--level", level, *force_flag)
    if code not in (0, 1):
        emit(f"enforce.py start failed (exit {code})")
        if isinstance(out, dict):
            emit_json(out)
        sys.exit(code)

    emit("Enforcer started. Agent should now be running.")
    emit("Monitoring state progression...")

    phase_ids   = enforcer_phase_ids(mode)
    last_phase  = None

    for expected_phase in phase_ids:
        emit(f"Waiting for phase: {expected_phase}")
        deadline    = time.monotonic() + POLL_TIMEOUT
        phase_done  = False

        while time.monotonic() < deadline:
            state = read_state()
            if not state:
                time.sleep(POLL_INTERVAL)
                continue

            completed = state.get("completed_phases", [])

            if expected_phase in completed:
                emit(f"✅  {expected_phase} complete.")
                last_phase  = expected_phase
                phase_done  = True
                break

            # Phase not done yet — check if state advanced at all (agent may be working)
            time.sleep(POLL_INTERVAL)

        if not phase_done:
            emit(
                f"⏱  Timeout waiting for {expected_phase} after {POLL_TIMEOUT}s.\n"
                f"   Injecting compliance reminder...\n"
                f"{COMPLIANCE_INJECTION.format(phase=expected_phase)}"
            )
            # In monitor mode we can only emit to stdout — the human/orchestrator
            # must feed this to the agent.

    # Final validation
    emit("All phases complete. Running final validation...")
    code, out = run_enforcer("validate")
    if code == 0:
        emit("validate passed.")
    else:
        emit(f"validate FAILED (exit {code}). See failures above.")
        sys.exit(1)

    code, out = run_enforcer("anchor-check")
    if code == 0:
        emit("anchor-check passed. Scan complete.")
    else:
        emit(f"anchor-check FAILED (exit {code}). Fix broken anchors.")
        sys.exit(1)

# ── Orchestrate mode ──────────────────────────────────────────────────────────
# Use when the conductor drives the agent as a subprocess per phase.
# Injects only the current phase's context. Retries on failure.

def cmd_orchestrate(args):
    mode        = args.mode
    level       = args.level
    area        = getattr(args, "area", None)
    worker_cmd  = args.worker or os.environ.get("CONDUCTOR_WORKER_CMD", "")
    max_retries = args.max_retries
    force       = args.force

    if not worker_cmd:
        emit("ERROR: --worker <cmd> required for orchestrate mode.")
        emit("  Example: --worker 'gemini -p {prompt_file}'")
        emit("  The worker command receives a temp file path via {prompt_file}.")
        sys.exit(3)

    emit(f"Starting in orchestrate mode | mode={mode} level={level} worker={worker_cmd!r}")

    # ── Start enforcer ─────────────────────────────────────────────────────
    start_args = ["start", "--mode", mode, "--level", level]
    if area:
        start_args += ["--area", area]
    if force:
        start_args.append("--force")

    code, out = run_enforcer(*start_args)
    if code not in (0,):
        emit(f"enforce.py start failed (exit {code})")
        emit_json(out if isinstance(out, dict) else {"raw": out})
        sys.exit(code)

    # Extract first phase instructions from start output
    phase_instructions = "\n".join(out.get("info", [])) if isinstance(out, dict) else str(out)

    phase_ids    = enforcer_phase_ids(mode)
    phase_context = phase_instructions  # Seeded from start output

    for phase_id in phase_ids:
        emit(f"Phase: {phase_id}")
        attempt = 0
        phase_passed = False

        while attempt < max_retries:
            attempt += 1
            emit(f"  Attempt {attempt}/{max_retries}")

            # ── Record state before running agent ─────────────────────────
            state_before = read_state()
            completed_before = set((state_before or {}).get("completed_phases", []))

            # ── Build prompt for agent ─────────────────────────────────────
            prompt = _build_phase_prompt(
                mode=mode,
                level=level,
                phase_id=phase_id,
                phase_context=phase_context,
                attempt=attempt,
                max_retries=max_retries,
            )

            # ── Run worker ─────────────────────────────────────────────────
            worker_exit = _run_worker(worker_cmd, prompt)
            emit(f"  Worker exited: {worker_exit}")

            # ── Check if agent called enforce.py done ─────────────────────
            time.sleep(0.5)  # brief settle
            state_after = read_state()
            completed_after = set((state_after or {}).get("completed_phases", []))

            if phase_id in completed_after and phase_id not in completed_before:
                emit(f"  ✅  Agent called enforce.py done and passed.")
                # Extract next phase instructions from enforcer state/output
                phase_context = _get_next_phase_context(phase_id, phase_ids)
                phase_passed = True
                break

            elif phase_id in completed_after:
                emit(f"  Phase was already marked complete before this attempt — skipping.")
                phase_passed = True
                break

            else:
                # Agent did not call enforce.py done — compliance failure
                emit(f"  ⚠️  Agent did NOT call enforce.py done {phase_id}.")

                # Try calling done ourselves to get the failure detail
                done_code, done_out = run_enforcer("done", phase_id)

                if done_code == 0:
                    emit(f"  Phase passed when conductor called done — agent forgot to call it.")
                    phase_context = _get_next_phase_context(phase_id, phase_ids)
                    phase_passed = True
                    break
                else:
                    # Phase genuinely failed
                    failures = _extract_failures(done_out)
                    emit(f"  Phase failed. Failures: {failures}")
                    phase_context = RETRY_INJECTION.format(
                        phase=phase_id,
                        attempt=attempt,
                        max_retries=max_retries,
                        failures="\n".join(f"  - {f}" for f in failures),
                    )
                    if attempt >= max_retries:
                        emit(f"  ❌  Max retries reached for {phase_id}. Aborting.")
                        sys.exit(1)

        if not phase_passed:
            emit(f"❌  Could not complete {phase_id} after {max_retries} attempts.")
            sys.exit(1)

    # ── Final validation ───────────────────────────────────────────────────
    emit("All phases complete. Running final validation...")

    for final_cmd in (["validate"], ["anchor-check"]):
        code, out = run_enforcer(*final_cmd)
        label = final_cmd[0]
        if code == 0:
            emit(f"✅  {label} passed.")
        else:
            failures = _extract_failures(out)
            emit(f"❌  {label} FAILED:\n" + "\n".join(f"  - {f}" for f in failures))
            sys.exit(1)

    emit("🎉  SCAN COMPLETE — all phases validated.")
    state = read_state()
    if state:
        for f in state.get("files_written", []):
            emit(f"  Output: {f}")
        emit("  Output: CONTEXT.md (project root)")


def _build_phase_prompt(
    mode: str, level: str, phase_id: str,
    phase_context: str, attempt: int, max_retries: int
) -> str:
    """Build the full prompt string to pass to the worker for this phase."""
    is_retry = attempt > 1
    header = (
        f"document-project skill | mode={mode} level={level}\n"
        f"{'=' * 60}\n"
        f"CURRENT TASK: {phase_id} (attempt {attempt}/{max_retries})\n"
        f"{'=' * 60}\n\n"
    )
    if is_retry:
        header += "⚠️  RETRY — previous attempt failed or did not call enforce.py done.\n\n"

    footer = (
        f"\n{'─' * 60}\n"
        f"REQUIRED: When you have completed the work above, call:\n"
        f"  python enforce.py done {phase_id} --agent\n"
        f"Exit 0 = passed. Exit 1 = fix and retry. Exit 2 = sequence error.\n"
        f"DO NOT proceed further until this returns exit 0.\n"
    )
    return header + phase_context + footer


def _run_worker(worker_cmd: str, prompt: str) -> int:
    """Write prompt to temp file and run the worker command."""
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".txt", delete=False, encoding="utf-8"
    ) as tf:
        tf.write(prompt)
        prompt_file = tf.name

    cmd = worker_cmd.replace("{prompt_file}", prompt_file)
    result = subprocess.run(cmd, shell=True)
    try:
        os.unlink(prompt_file)
    except OSError:
        pass
    return result.returncode


def _get_next_phase_context(current_phase_id: str, phase_ids: list[str]) -> str:
    """
    Get next phase instructions by calling enforce.py status and parsing.
    Falls back to a generic 'check status' message.
    """
    code, out = run_enforcer("status")
    if isinstance(out, dict):
        return "\n".join(out.get("info", ["Run enforce.py status for next instructions."]))
    return "Run: python enforce.py status --agent for next phase instructions."


def _extract_failures(enforcer_out) -> list[str]:
    """Extract failed check labels from enforce.py JSON output."""
    if not isinstance(enforcer_out, dict):
        return [str(enforcer_out)]
    failures = [
        c["label"] + (f" — {c['detail']}" if c.get("detail") else "")
        for c in enforcer_out.get("checks", [])
        if not c.get("passed", True)
    ]
    failures += [b.get("reason", str(b)) for b in enforcer_out.get("blocks", [])]
    return failures or ["Unknown failure — run enforce.py done <phase> --agent manually"]


# ── Status command ─────────────────────────────────────────────────────────────

def cmd_status(args):
    code, out = run_enforcer("status")
    emit_json({
        "enforcer_exit": code,
        "enforcer_output": out,
        "state_file_exists": STATE_FILE.exists(),
        "timestamp": now_iso(),
    })


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="document-project conductor",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # monitor
    p_mon = sub.add_parser("monitor", help="Watch state progression, inject compliance messages")
    p_mon.add_argument("--mode",  required=True, choices=["initial_scan", "full_rescan", "deep_dive"])
    p_mon.add_argument("--level", required=True, choices=["quick", "deep", "exhaustive"])
    p_mon.add_argument("--force", action="store_true")
    p_mon.set_defaults(func=cmd_monitor)

    # orchestrate
    p_orch = sub.add_parser("orchestrate", help="Drive agent subprocess per phase")
    p_orch.add_argument("--mode",        required=True, choices=["initial_scan", "full_rescan", "deep_dive"])
    p_orch.add_argument("--level",       required=True, choices=["quick", "deep", "exhaustive"])
    p_orch.add_argument("--area",        help="Deep-dive area (required for deep_dive)")
    p_orch.add_argument("--worker",      help="Worker command — use {prompt_file} for context injection")
    p_orch.add_argument("--max-retries", type=int, default=MAX_RETRIES)
    p_orch.add_argument("--force",       action="store_true")
    p_orch.set_defaults(func=cmd_orchestrate)

    # status
    p_status = sub.add_parser("status", help="Emit JSON conductor + enforcer status")
    p_status.set_defaults(func=cmd_status)

    args = parser.parse_args()
    try:
        args.func(args)
    except KeyboardInterrupt:
        emit("Interrupted.")
        sys.exit(0)
    except Exception as e:
        emit(f"FATAL: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(3)


if __name__ == "__main__":
    main()
