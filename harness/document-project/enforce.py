#!/usr/bin/env python3
"""
enforce.py — document-project skill enforcer  v2.0
AI agent MUST call this script at every phase boundary.
Blocks protocol violations. Maintains state. Validates outputs.

Usage:
  python enforce.py start --mode <mode> --level <level> [--area <area>] [--force] [--agent]
  python enforce.py done <phase>   [--agent]
  python enforce.py status         [--agent]
  python enforce.py resume         [--agent]
  python enforce.py validate       [--agent]
  python enforce.py anchor-check   [--agent]

Modes:    initial_scan | full_rescan | deep_dive
Levels:   quick | deep | exhaustive
Phases:   phase_1 | phase_2 | phase_3 | phase_4 | phase_5 | phase_6
          (deep_dive: step_1 | step_2 | step_3 | step_4 | step_5 | step_6)

Agent / subagentic flags:
  --force   Overwrite existing scan without interactive prompt (required in agent mode)
  --agent   Non-interactive mode: no prompts, JSON-structured output, machine-readable
            exit codes. Also activated by env var ENFORCE_AGENT=1.

Exit codes:
  0  Success / all checks passed
  1  Validation failure (fixable — re-run after fixing issues)
  2  Blocked (prerequisite not met — check sequence)
  3  Fatal / unexpected error
"""

import hashlib
import json
import os
import re
import sys
import argparse
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

try:
    import fcntl
except ImportError:
    fcntl = None

# ── UTF-8 output on Windows ───────────────────────────────────────────────────
if sys.platform == "win32":
    sys.stdout = open(sys.stdout.fileno(), mode="w", encoding="utf-8", errors="replace")
    sys.stderr = open(sys.stderr.fileno(), mode="w", encoding="utf-8", errors="replace")

# ── Agent mode detection ──────────────────────────────────────────────────────
# Activated by --agent flag OR ENFORCE_AGENT=1 env var (set by orchestrators).
# When active: no stdin prompts, all output is JSON, exit codes are machine-readable.
AGENT_MODE: bool = os.environ.get("ENFORCE_AGENT", "").strip() in ("1", "true", "yes")

# ── Constants ─────────────────────────────────────────────────────────────────
STATE_FILE        = Path(".docs/.scan-state.json")
LOCK_FILE         = Path(".docs/.scan-state.lock")
DOCS_DIR          = Path(".docs")
CONTEXT_MD        = Path("CONTEXT.md")

TOKEN_BUDGET      = 4000   # CONTEXT.md hard cap
CHARS_PER_TOKEN   = 4      # rough proxy
SECTION_EXTRACT_THRESH_TOKENS = 1000  # sections larger than this → deep-dives/

PLACEHOLDER_PATTERNS = [
    r"\bTODO\b",
    r"\bTBD\b",
    r"\bfill in later\b",
    r"\bplaceholder\b",
    r"\bcome back to this\b",
    r"^\s*\.\.\.\s*$",
]

# ── File locking (cross-process safety for multi-agent runs) ──────────────────
# Uses an advisory lock file so parallel agents don't clobber state simultaneously.
# Falls back silently on platforms that don't support fcntl (Windows without portalocker).

@contextmanager
def state_lock(timeout: float = 10.0):
    """Acquire an exclusive advisory lock on the state file before read/write."""
    DOCS_DIR.mkdir(exist_ok=True)
    acquired = False
    deadline = time.monotonic() + timeout
    try:
        lf = open(LOCK_FILE, "w", encoding="utf-8")
        while time.monotonic() < deadline:
            try:
                fcntl.flock(lf, fcntl.LOCK_EX | fcntl.LOCK_NB)
                acquired = True
                break
            except (OSError, BlockingIOError):
                time.sleep(0.05)
        if not acquired:
            # Timeout — proceed anyway (best-effort; don't block the agent)
            pass
        yield
    except (AttributeError, ImportError):
        # fcntl not available (Windows without portalocker) — skip locking
        yield
    finally:
        if acquired:
            try:
                fcntl.flock(lf, fcntl.LOCK_UN)
                lf.close()
            except Exception:
                pass

# ── I/O helpers ───────────────────────────────────────────────────────────────

def read_utf8(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")

def _json_result(ok: bool, command: str, message: str, data: dict = None) -> dict:
    return {
        "ok":      ok,
        "command": command,
        "message": message,
        "data":    data or {},
    }

# ── Output (human vs agent) ───────────────────────────────────────────────────
# All output is buffered into a results list during execution, then flushed.
# In agent mode: flushed as a single JSON object.
# In human mode: flushed as formatted terminal output.

_output_records: list[dict] = []      # {"type": "check"|"info"|"header"|"block", ...}
_all_passed_global: bool = True       # tracks across the run

def _emit(record: dict):
    _output_records.append(record)

def header(text: str):
    _emit({"type": "header", "text": text})

def info(text: str):
    _emit({"type": "info", "text": text})

def check(label: str, result: bool, detail: str = "") -> bool:
    global _all_passed_global
    if not result:
        _all_passed_global = False
    _emit({"type": "check", "label": label, "passed": result, "detail": detail})
    return result

def block(reason: str):
    """Emit a blocking error and exit with code 2 (prerequisite/sequence error)."""
    _emit({"type": "block", "reason": reason})
    _flush_output()
    sys.exit(2)

def fatal(reason: str):
    """Emit a fatal error and exit with code 3."""
    _emit({"type": "fatal", "reason": reason})
    _flush_output()
    sys.exit(3)

def _flush_output():
    """Print all buffered output in human or agent format."""
    if AGENT_MODE:
        # Single JSON object — agents parse this
        checks = [r for r in _output_records if r["type"] == "check"]
        blocks = [r for r in _output_records if r["type"] == "block"]
        fatals = [r for r in _output_records if r["type"] == "fatal"]
        infos  = [r for r in _output_records if r["type"] in ("header", "info")]

        ok = (not blocks) and (not fatals) and all(c["passed"] for c in checks)
        out = {
            "ok":      ok,
            "checks":  checks,
            "blocks":  blocks,
            "fatals":  fatals,
            "info":    [r["text"] for r in infos],
        }
        print(json.dumps(out, ensure_ascii=False))
    else:
        # Human-readable terminal output
        for r in _output_records:
            t = r["type"]
            if t == "header":
                print(f"\n{'─' * 60}")
                print(f"  {r['text']}")
                print(f"{'─' * 60}")
            elif t == "info":
                print(f"  ℹ️   {r['text']}")
            elif t == "check":
                icon = "✅ PASS" if r["passed"] else "❌ FAIL"
                line = f"  {icon}  {r['label']}"
                if r.get("detail"):
                    line += f"\n         {r['detail']}"
                print(line)
            elif t == "block":
                print(f"\n  🚫 BLOCKED  {r['reason']}\n")
            elif t == "fatal":
                print(f"\n  💥 FATAL  {r['reason']}\n")

# ── Phase definitions ─────────────────────────────────────────────────────────

SCAN_PHASES = [
    {
        "id": "phase_1",
        "name": "Phase 1: Project Detection",
        "output_files": [DOCS_DIR / "project-overview.md"],
        "required_sections": ["project type", "purpose", "primary language", "lede"],
        "required_previous": [],
        "instructions": (
            "Read top-level files (README, package.json, Cargo.toml, etc.).\n"
            "Scan top 2 directory levels. Detect project type in priority order:\n"
            "  mobile → desktop → game → web_app → api → library\n"
            "NEWSPAPER FORMAT: Write ledé first (3 lines: identity + primary stack + purpose).\n"
            "Write .docs/project-overview.md with type, purpose, primary language.\n"
            "Then call: python enforce.py done phase_1"
        ),
    },
    {
        "id": "phase_2",
        "name": "Phase 2: Technology Stack",
        "output_files": [DOCS_DIR / "project-overview.md"],
        "required_sections": ["technology stack", "tech stack"],
        "required_previous": ["phase_1"],
        "instructions": (
            "Read all dependency files and config files.\n"
            "Classify every technology as: core | infrastructure | development | testing | services | inactive | planned.\n"
            "NEWSPAPER FORMAT: Classified bullet lists under headers — NOT a flat unclassified list.\n"
            "  Example:\n"
            "    **Core runtime**\n"
            "    - React 19 (UI framework)\n"
            "    **Inactive**\n"
            "    - Docker (configured but not wired)\n"
            "Mark inactive deps explicitly. Do not mix into active lists.\n"
            "Append ## Tech Stack section to .docs/project-overview.md.\n"
            "Then call: python enforce.py done phase_2"
        ),
    },
    {
        "id": "phase_3",
        "name": "Phase 3: Architecture",
        "output_files": [DOCS_DIR / "architecture.md"],
        "required_sections": ["lede", "entry point", "data flow", "authentication", "key modules"],
        "required_previous": ["phase_1", "phase_2"],
        "instructions": (
            "Identify entry points and trace request/data flow end to end.\n"
            "Name the architectural pattern (MVC, layered, event-driven, etc.).\n"
            "Map key modules, inter-module communication, error handling, auth patterns.\n"
            "NEWSPAPER FORMAT: Ledé first (3 lines: project type + 2 hardest architectural rules).\n"
            "Layer diagram MUST be inline — never behind a link.\n"
            "If project has a user-identity proxy pattern, show it verbatim (e.g. getRealUserId()).\n"
            "Add #section-anchors to every major section.\n"
            "Required anchors: #overview #entry-points #data-flow #authentication-patterns\n"
            "                  #key-modules #error-handling #architectural-decisions\n"
            "Write .docs/architecture.md.\n"
            "Then call: python enforce.py done phase_3"
        ),
    },
    {
        "id": "phase_4",
        "name": "Phase 4: Source Tree",
        "output_files": [DOCS_DIR / "source-tree.md"],
        "required_sections": [],
        "required_previous": ["phase_1", "phase_2", "phase_3"],
        "instructions": (
            "Generate annotated directory tree (respect .gitignore).\n"
            "Annotate every source directory with its purpose.\n"
            "Annotate key files: entry points, configs, main modules.\n"
            "Depth by scan level:\n"
            "  quick       → top 3 levels + key files\n"
            "  deep        → full tree + source directory annotations\n"
            "  exhaustive  → full tree + annotation on every source file\n"
            "Write .docs/source-tree.md.\n"
            "Then call: python enforce.py done phase_4"
        ),
    },
    {
        "id": "phase_5",
        "name": "Phase 5: Development Guide",
        "output_files": [DOCS_DIR / "dev-guide.md"],
        "required_sections": ["lede", "setup", "gotchas"],
        "required_previous": ["phase_1", "phase_2", "phase_3", "phase_4"],
        "instructions": (
            "Read README, CONTRIBUTING, Makefile, scripts/.\n"
            "Document: prerequisites, env setup, build, test, lint, deploy commands.\n"
            "NEWSPAPER FORMAT: Ledé first (2-3 lines: what it is + prereqs + ONE start command).\n"
            "CRITICAL: Gotchas MUST be in a table near the top — NOT buried at the bottom.\n"
            "  Format: | Gotcha | What it means | Don't do this |\n"
            "If no gotchas found: write one row 'No unexpected gotchas found during scan'.\n"
            "Verify every command exists in an actual config file before writing it.\n"
            "Write .docs/dev-guide.md.\n"
            "Then call: python enforce.py done phase_5"
        ),
    },
    {
        "id": "phase_6",
        "name": "Phase 6: Context Root (CONTEXT.md)",
        "output_files": [CONTEXT_MD],
        "required_sections": [
            "project context",
            "critical constraints",
            "tech stack",
            "entry points",
            "layer reference",
        ],
        "required_previous": ["phase_1", "phase_2", "phase_3", "phase_4", "phase_5"],
        "instructions": (
            "This phase runs LAST. All phase 1-5 docs must exist first.\n"
            "Read a summary of each .docs/ file (not full content).\n"
            "Write CONTEXT.md at PROJECT ROOT — not inside .docs/.\n\n"
            "NEWSPAPER LEDE FORMAT (first 3 lines, no preamble):\n"
            "  > [Line 1: What it is + type]\n"
            "  > HARD RULE: [Line 2: The single hardest architectural rule]\n"
            "  > HARD RULE: [Line 3: Second hardest rule or auth/data quirk]\n\n"
            "Required sections in order:\n"
            "  ## Critical Constraints  — table, one row per constraint, actionable\n"
            "  ## Tech Stack            — classified (core | UI | inactive | planned), NOT flat\n"
            "  ## Entry Points          — ONE link per topic to most specific doc\n"
            "  ## Layer Reference       — inline diagram, NOT behind a link\n\n"
            "Budget: ≤4,000 tokens (~16,000 chars). Enforcer blocks if over.\n"
            "Use #anchor links — NOT line numbers.\n"
            f"Extract any section >{SECTION_EXTRACT_THRESH_TOKENS} tokens to .docs/deep-dives/ and link.\n"
            "DO NOT include a 'Deep Dives Available' section — redundant with Entry Points.\n"
            "Then call: python enforce.py done phase_6\n"
            "Then call: python enforce.py validate\n"
            "Then call: python enforce.py anchor-check"
        ),
    },
]

DEEP_DIVE_STEPS = [
    {
        "id": "step_1",
        "name": "Step 1: Target Area Selection",
        "output_files": [],   # no file until step_6
        "required_sections": [],
        "required_previous": [],
        "instructions": (
            "Confirm scope with user if ambiguous (skip in --agent mode).\n"
            "Define in writing: which directories, files, concepts are in scope.\n"
            "Then call: python enforce.py done step_1"
        ),
    },
    {
        "id": "step_2",
        "name": "Step 2: File Inventory",
        "output_files": [],
        "required_sections": [],
        "required_previous": ["step_1"],
        "instructions": (
            "List EVERY file in scope using glob patterns. No sampling.\n"
            "Categorize: source | test | config | documentation.\n"
            "Note file sizes and recency. Exclude generated/vendor/build.\n"
            "Then call: python enforce.py done step_2"
        ),
    },
    {
        "id": "step_3",
        "name": "Step 3: Exhaustive File Review",
        "output_files": [],
        "required_sections": [],
        "required_previous": ["step_1", "step_2"],
        "instructions": (
            "Read EVERY file in scope completely — no truncation, no skipping.\n"
            "For each file document: purpose, exports, dependencies, dependents,\n"
            "key functions/classes, state management, error handling, config deps.\n"
            "Write-as-you-go: write documentation per file as you complete it.\n"
            "Then call: python enforce.py done step_3"
        ),
    },
    {
        "id": "step_4",
        "name": "Step 4: Dependency Mapping",
        "output_files": [],
        "required_sections": [],
        "required_previous": ["step_1", "step_2", "step_3"],
        "instructions": (
            "Map: internal deps, internal dependents, external packages,\n"
            "data flow in/through/out, config requirements, runtime services.\n"
            "Produce a dependency map (text diagram or structured list).\n"
            "Then call: python enforce.py done step_4"
        ),
    },
    {
        "id": "step_5",
        "name": "Step 5: Pattern Documentation",
        "output_files": [],
        "required_sections": [],
        "required_previous": ["step_1", "step_2", "step_3", "step_4"],
        "instructions": (
            "Catalog: code patterns, data patterns, error patterns,\n"
            "testing patterns, configuration patterns.\n"
            "Include actual code examples from the files you reviewed.\n"
            "Then call: python enforce.py done step_5"
        ),
    },
    {
        "id": "step_6",
        "name": "Step 6: Implementation Guidance",
        # output_files is populated dynamically from deep_dive_area at runtime.
        # Left empty here — see _resolve_deep_dive_output() below.
        "output_files": [],
        "required_sections": [
            "scope",
            "file inventory",
            "architecture",
            "dependency map",
            "patterns",
            "implementation guidance",
        ],
        "required_previous": ["step_1", "step_2", "step_3", "step_4", "step_5"],
        "instructions": (
            "Write: modification guide, extension points, constraints,\n"
            "testing guidance, common pitfalls.\n"
            "Write the COMPLETE .docs/deep-dives/<area>.md file.\n"
            "Do NOT update CONTEXT.md's 'Deep Dives Available' section — that section\n"
            "is removed per newspaper logic. Link from Entry Points instead.\n"
            "Then call: python enforce.py done step_6\n"
            "Then call: python enforce.py validate"
        ),
    },
]

# ── Helpers ───────────────────────────────────────────────────────────────────

def _resolve_deep_dive_output(state: dict) -> Path:
    """Return the expected output path for deep_dive step_6."""
    area = (state or {}).get("deep_dive_area", "unknown")
    return DOCS_DIR / "deep-dives" / f"{area}.md"

def load_state() -> dict | None:
    if not STATE_FILE.exists():
        return None
    with state_lock():
        with open(STATE_FILE, encoding="utf-8") as f:
            state = json.load(f)
    if not _verify_state_integrity(state):
        _emit({"type": "block", "reason": (
            "State file integrity check FAILED — .docs/.scan-state.json was modified outside "
            "of enforce.py. This breaks the enforcement chain.\n"
            "  To reset: delete .docs/.scan-state.json and re-run enforce.py start"
        )})
        _flush_output()
        sys.exit(2)
    return state

def save_state(state: dict):
    DOCS_DIR.mkdir(exist_ok=True)
    _sign_state(state)
    with state_lock():
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2, ensure_ascii=False)

def _state_hash(state: dict) -> str:
    """HMAC-lite: SHA256 of sorted JSON content excluding the integrity field."""
    s = {k: v for k, v in state.items() if k != "_integrity"}
    payload = json.dumps(s, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(payload.encode()).hexdigest()[:16]

def _sign_state(state: dict) -> dict:
    """Attach integrity hash to state before saving."""
    state["_integrity"] = _state_hash(state)
    return state

def _verify_state_integrity(state: dict) -> bool:
    """Return True if state hash matches content. False = tampered."""
    stored = state.get("_integrity")
    if not stored:
        return True  # Legacy state without hash — pass silently
    return stored == _state_hash(state)

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def phases_for_mode(mode: str) -> list[dict]:
    return DEEP_DIVE_STEPS if mode == "deep_dive" else SCAN_PHASES

def file_exists(path: Path) -> bool:
    return path.exists() and path.stat().st_size > 0

def contains_section(path: Path, keyword: str) -> bool:
    """Case-insensitive substring match anywhere in the file."""
    if not path.exists():
        return False
    return keyword.lower() in read_utf8(path).lower()

def has_placeholders(path: Path) -> tuple[bool, str]:
    if not path.exists():
        return False, ""
    text = read_utf8(path)
    for pattern in PLACEHOLDER_PATTERNS:
        m = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        if m:
            return True, f'found "{m.group()}" near char {m.start()}'
    return False, ""

def estimate_tokens(path: Path) -> int:
    if not path.exists():
        return 0
    return len(read_utf8(path)) // CHARS_PER_TOKEN

def check_no_line_numbers(context_path: Path) -> tuple[bool, list[str]]:
    """Detect → line NNN references (line-number links are banned; use #anchors)."""
    if not context_path.exists():
        return True, []
    matches = re.findall(r"→\s*line\s*\d+", read_utf8(context_path), re.IGNORECASE)
    return len(matches) == 0, matches

def validate_anchors(context_path: Path) -> list[tuple[str, bool, str]]:
    """
    Parse every markdown link in CONTEXT.md containing a #anchor.
    Returns list of (description, passed, detail).
    """
    if not context_path.exists():
        return []
    text = read_utf8(context_path)
    results = []
    for m in re.finditer(r'\[([^\]]+)\]\(([^)]+#[^)]+)\)', text):
        label     = m.group(1)
        full_link = m.group(2)
        if "#" not in full_link:
            continue
        file_part, anchor = full_link.rsplit("#", 1)
        target = Path(file_part)
        if not target.exists():
            results.append((f"{label} → {full_link}", False, f"file not found: {file_part}"))
            continue
        content = read_utf8(target)
        # Convert GitHub-style anchor (hyphens→spaces) and search for heading
        anchor_words = anchor.replace("-", " ").replace("_", " ")
        pattern_a = rf"^#{{1,6}}\s+.*{re.escape(anchor_words)}.*$"
        # Also try direct hyphen match as-is
        pattern_b = rf"^#{{1,6}}\s+.*{re.escape(anchor)}.*$"
        found = bool(
            re.search(pattern_a, content, re.IGNORECASE | re.MULTILINE) or
            re.search(pattern_b, content, re.IGNORECASE | re.MULTILINE)
        )
        results.append((
            f"{label} → {full_link}",
            found,
            "" if found else f"no heading matching '#{anchor}' in {file_part}",
        ))
    return results

def _sections_over_threshold(path: Path) -> list[tuple[str, int]]:
    """
    Find sections (## headers) whose content exceeds SECTION_EXTRACT_THRESH_TOKENS.
    Returns list of (section_title, token_count).
    Only relevant as advisory output — not a hard block.
    """
    if not path.exists():
        return []
    text = read_utf8(path)
    chunks = re.split(r"^(#{1,3} .+)$", text, flags=re.MULTILINE)
    heavy = []
    i = 1
    while i + 1 < len(chunks):
        title   = chunks[i].strip()
        content = chunks[i + 1]
        tokens  = len(content) // CHARS_PER_TOKEN
        if tokens > SECTION_EXTRACT_THRESH_TOKENS:
            heavy.append((title, tokens))
        i += 2
    return heavy

# ── Phase validation (shared by cmd_done and cmd_validate) ───────────────────

def _validate_phase(phase_id: str, phase_def: dict, state: dict) -> bool:
    """
    Run all checks for a single completed phase.
    Returns True if all checks passed.
    """
    mode = state["mode"]
    is_deep_dive   = mode == "deep_dive"
    is_step_6      = phase_id == "step_6"
    is_phase_6     = phase_id == "phase_6"

    all_passed = True

    # ── Resolve output files ───────────────────────────────────────────────
    # For deep_dive step_6, the output file is dynamic (area-specific).
    # For all other phases, use phase_def["output_files"].
    if is_deep_dive and is_step_6:
        output_files_to_check = [_resolve_deep_dive_output(state)]
    else:
        output_files_to_check = [f for f in phase_def["output_files"] if f.parts]

    # ── File existence ─────────────────────────────────────────────────────
    for fpath in output_files_to_check:
        passed = check(
            f"Output file exists and non-empty: {fpath}",
            file_exists(fpath),
            "Write the file before marking this phase done." if not file_exists(fpath) else "",
        )
        all_passed = all_passed and passed

    # ── Required sections ──────────────────────────────────────────────────
    for fpath in output_files_to_check:
        if not fpath.exists():
            continue
        for section in phase_def["required_sections"]:
            # phase_2 has two alternate section names — pass if either found
            if isinstance(section, (list, tuple)):
                found = any(contains_section(fpath, s) for s in section)
                label = f"Section present: '{' or '.join(section)}' in {fpath.name}"
            else:
                found = contains_section(fpath, section)
                label = f"Section present: '{section}' in {fpath.name}"
            passed = check(label, found)
            all_passed = all_passed and passed

    # ── Placeholder check ──────────────────────────────────────────────────
    for fpath in output_files_to_check:
        if not fpath.exists():
            continue
        has_ph, detail = has_placeholders(fpath)
        passed = check(f"No placeholders in {fpath.name}", not has_ph, detail)
        all_passed = all_passed and passed

    # ── phase_6 deep checks ────────────────────────────────────────────────
    if is_phase_6 and CONTEXT_MD.exists():
        # Token budget
        tokens = estimate_tokens(CONTEXT_MD)
        passed = check(
            f"CONTEXT.md within ≤{TOKEN_BUDGET} token budget (estimated {tokens})",
            tokens <= TOKEN_BUDGET,
            f"Trim content or extract heavy sections to .docs/deep-dives/",
        )
        all_passed = all_passed and passed

        # Must live at project root
        passed = check(
            "CONTEXT.md is at project root (not inside .docs/)",
            CONTEXT_MD.exists() and not str(CONTEXT_MD).startswith(".docs"),
        )
        all_passed = all_passed and passed

        # Header check
        ctx_text   = read_utf8(CONTEXT_MD)
        first_line = ctx_text.splitlines()[0] if ctx_text.strip() else ""
        passed = check(
            "First line is '# PROJECT CONTEXT'",
            "PROJECT CONTEXT" in first_line,
            f'Got: "{first_line}"',
        )
        all_passed = all_passed and passed

        # No line-number refs
        clean, bad_refs = check_no_line_numbers(CONTEXT_MD)
        passed = check(
            "CONTEXT.md uses #anchors only (no → line NNN references)",
            clean,
            f"Remove: {bad_refs}" if bad_refs else "",
        )
        all_passed = all_passed and passed

        # Prerequisite docs exist
        prereqs = {
            ".docs/project-overview.md": DOCS_DIR / "project-overview.md",
            ".docs/architecture.md":     DOCS_DIR / "architecture.md",
            ".docs/source-tree.md":      DOCS_DIR / "source-tree.md",
            ".docs/dev-guide.md":        DOCS_DIR / "dev-guide.md",
        }
        for name, fpath in prereqs.items():
            passed = check(f"Prerequisite exists: {name}", file_exists(fpath))
            all_passed = all_passed and passed

        # Advisory: sections over extraction threshold
        heavy = _sections_over_threshold(CONTEXT_MD)
        for section_title, tok in heavy:
            info(
                f"⚠️  CONTEXT.md section '{section_title}' is ~{tok} tokens "
                f"(>{SECTION_EXTRACT_THRESH_TOKENS}). Consider extracting to .docs/deep-dives/."
            )

    return all_passed

# ── Commands ──────────────────────────────────────────────────────────────────

def cmd_start(args):
    global AGENT_MODE
    if args.agent:
        AGENT_MODE = True

    mode  = args.mode
    level = args.level
    area  = getattr(args, "area", None)
    force = getattr(args, "force", False)

    if mode == "deep_dive" and not area:
        block("deep_dive mode requires --area <area-name>  e.g. --area auth")

    existing = load_state()
    if existing and existing.get("status") != "complete":
        if AGENT_MODE or force:
            # Non-interactive: overwrite automatically
            info(
                f"Overwriting existing incomplete scan "
                f"(mode={existing.get('mode')} status={existing.get('status')})."
            )
        else:
            # Human mode: prompt
            print(f"\n  ⚠️   Existing incomplete scan found.")
            print(f"  Mode:   {existing.get('mode')}")
            print(f"  Status: {existing.get('status')}")
            print(f"  Phase:  {existing.get('current_phase')}")
            print(f"\n  Run  python enforce.py resume  to continue.")
            print(f"  Or   python enforce.py start ... --force  to overwrite.\n")
            confirm = input("  Overwrite? [y/N] ").strip().lower()
            if confirm != "y":
                print("  Aborted.")
                sys.exit(0)

    phases      = phases_for_mode(mode)
    first_phase = phases[0]["id"]

    state = {
        "mode":             mode,
        "scan_level":       level,
        "deep_dive_area":   area,
        "current_phase":    first_phase,
        "completed_phases": [],
        "files_written":    [],
        "status":           "in_progress",
        "started":          now_iso(),
        "updated":          now_iso(),
        "agent_mode":       AGENT_MODE,
    }
    save_state(state)

    header(f"document-project  |  mode={mode}  level={level}{f'  area={area}' if area else ''}")
    info(f"State file: {STATE_FILE}")
    info(f"Agent mode: {AGENT_MODE}")
    info("")
    info(f"START WITH: {phases[0]['name']}")
    for line in phases[0]["instructions"].splitlines():
        info(line)
    info("")
    info("Protocol: write each output file IMMEDIATELY after its phase completes.")
    info("Never accumulate context across phases.")

    _flush_output()
    sys.exit(0)


def cmd_done(args):
    global AGENT_MODE
    if args.agent:
        AGENT_MODE = True

    phase_id = args.phase
    state    = load_state()

    if not state:
        block("No active scan. Run: python enforce.py start --mode <mode> --level <level>")

    mode      = state["mode"]
    phases    = phases_for_mode(mode)
    phase_ids = [p["id"] for p in phases]

    if phase_id not in phase_ids:
        block(
            f"Unknown phase '{phase_id}' for mode '{mode}'.\n"
            f"  Valid phases: {', '.join(phase_ids)}"
        )

    phase_def = next(p for p in phases if p["id"] == phase_id)

    # Enforce prerequisite ordering
    missing = [p for p in phase_def["required_previous"] if p not in state["completed_phases"]]
    if missing:
        block(
            f"Cannot mark {phase_id} done — prerequisite(s) not complete: {', '.join(missing)}\n"
            f"  Completed so far: {state['completed_phases'] or 'none'}"
        )

    if phase_id in state["completed_phases"]:
        info(f"⚠️  {phase_id} was already marked complete — re-validating.")

    header(f"Validating: {phase_def['name']}")
    all_passed = _validate_phase(phase_id, phase_def, state)

    if not all_passed:
        _flush_output()
        sys.exit(1)  # Fixable validation failure

    # ── Update state ───────────────────────────────────────────────────────
    if phase_id not in state["completed_phases"]:
        state["completed_phases"].append(phase_id)

    # Record output files written
    if mode == "deep_dive" and phase_id == "step_6":
        fp = str(_resolve_deep_dive_output(state))
        if fp not in state["files_written"]:
            state["files_written"].append(fp)
    else:
        for fpath in phase_def["output_files"]:
            fp = str(fpath)
            if fp not in state["files_written"]:
                state["files_written"].append(fp)

    state["updated"] = now_iso()

    # Advance to next phase or mark complete
    current_idx = phase_ids.index(phase_id)
    if current_idx + 1 < len(phases):
        next_phase = phases[current_idx + 1]
        state["current_phase"] = next_phase["id"]
        save_state(state)

        info(f"✅  {phase_id} complete. Next: {next_phase['name']}")
        info("")
        for line in next_phase["instructions"].splitlines():
            info(line)
        info("")
    else:
        state["current_phase"] = "complete"
        state["status"]        = "awaiting_final_validation"
        save_state(state)

        info(f"✅  {phase_id} complete. All phases done.")
        info("")
        info("── FINAL STEPS ────────────────────────────────────────")
        info("  python enforce.py validate")
        info("  python enforce.py anchor-check")

    _flush_output()
    sys.exit(0)


def cmd_status(args):
    global AGENT_MODE
    if args.agent:
        AGENT_MODE = True

    state = load_state()
    if not state:
        info("No active scan. Run: python enforce.py start --mode <mode> --level <level>")
        _flush_output()
        return

    mode      = state["mode"]
    phases    = phases_for_mode(mode)
    phase_ids = [p["id"] for p in phases]

    header("document-project  |  scan status")
    info(f"Mode:    {state['mode']}")
    info(f"Level:   {state.get('scan_level', 'n/a')}")
    if state.get("deep_dive_area"):
        info(f"Area:    {state['deep_dive_area']}")
    info(f"Status:  {state['status']}")
    info(f"Started: {state['started']}")
    info(f"Updated: {state['updated']}")
    info("")

    for pid in phase_ids:
        pdef   = next(p for p in phases if p["id"] == pid)
        done   = pid in state["completed_phases"]
        active = pid == state.get("current_phase")
        marker = "✅" if done else ("▶️ " if active else "⬜")
        info(f"{marker}  {pid}  —  {pdef['name']}")

    info("")
    if state["status"] == "complete":
        info("Scan complete. All files validated.")
    elif state["status"] == "awaiting_final_validation":
        info("All phases done. Run: python enforce.py validate && python enforce.py anchor-check")
    else:
        current = state.get("current_phase", "unknown")
        pdef    = next((p for p in phases if p["id"] == current), None)
        if pdef:
            info(f"Next action: complete {pdef['name']}")
            info(f"Then run:    python enforce.py done {current}")

    _flush_output()


def cmd_resume(args):
    global AGENT_MODE
    if args.agent:
        AGENT_MODE = True

    state = load_state()
    if not state:
        block("No state file. Start fresh: python enforce.py start --mode <mode> --level <level>")

    if state["status"] == "complete":
        header("Scan already complete")
        info("Run 'python enforce.py status' to review output files.")
        _flush_output()
        return

    mode   = state["mode"]
    phases = phases_for_mode(mode)

    # Re-verify completed phases by checking output files actually exist on disk.
    # Phases with output_files=[] (deep dive steps 1-5) CANNOT be verified by file
    # presence alone — they remain trusted from state only (no file evidence to contradict).
    verified_complete = []
    needs_redo        = []

    for pid in state["completed_phases"]:
        pdef = next((p for p in phases if p["id"] == pid), None)
        if not pdef:
            continue

        # Resolve actual output files for this phase
        if mode == "deep_dive" and pid == "step_6":
            files_to_check = [_resolve_deep_dive_output(state)]
        else:
            files_to_check = [f for f in pdef["output_files"] if f.parts]

        if not files_to_check:
            # No file evidence possible — trust state (steps 1-5 of deep dive)
            verified_complete.append(pid)
        elif all(file_exists(f) for f in files_to_check):
            verified_complete.append(pid)
        else:
            needs_redo.append(pid)

    if needs_redo:
        header("⚠️  File verification failed — output files missing for completed phases")
        for pid in needs_redo:
            check(f"{pid} — output file(s) missing", False)
        info("These phases must be re-run before continuing.")
        state["completed_phases"] = verified_complete
        state["updated"]          = now_iso()
        save_state(state)

    # Find next incomplete phase
    phase_ids  = [p["id"] for p in phases]
    next_pid   = next((pid for pid in phase_ids if pid not in verified_complete), None)

    if not next_pid:
        header("All phases verified complete")
        info("Run: python enforce.py validate")
        _flush_output()
        return

    next_phase                    = next(p for p in phases if p["id"] == next_pid)
    state["current_phase"]        = next_pid
    state["completed_phases"]     = verified_complete
    state["updated"]              = now_iso()
    save_state(state)

    header(f"Resuming from: {next_phase['name']}")
    info(f"Verified complete: {verified_complete or 'none'}")
    info("")
    for line in next_phase["instructions"].splitlines():
        info(line)

    _flush_output()


def cmd_validate(args):
    global AGENT_MODE
    if args.agent:
        AGENT_MODE = True

    state = load_state()
    mode  = state["mode"] if state else "initial_scan"

    header("Full Checklist Validation")

    # ── Required output files ──────────────────────────────────────────────
    info("[ Output Files ]")
    if mode != "deep_dive":
        required_files = {
            "CONTEXT.md at project root":  CONTEXT_MD,
            ".docs/project-overview.md":   DOCS_DIR / "project-overview.md",
            ".docs/architecture.md":        DOCS_DIR / "architecture.md",
            ".docs/source-tree.md":         DOCS_DIR / "source-tree.md",
            ".docs/dev-guide.md":           DOCS_DIR / "dev-guide.md",
            ".docs/.scan-state.json":       STATE_FILE,
        }
    else:
        area = (state or {}).get("deep_dive_area", "unknown")
        required_files = {
            f".docs/deep-dives/{area}.md": DOCS_DIR / "deep-dives" / f"{area}.md",
            ".docs/.scan-state.json":      STATE_FILE,
        }

    all_passed = True
    for label, fpath in required_files.items():
        passed = check(label, file_exists(fpath))
        all_passed = all_passed and passed

    # ── Placeholder check ──────────────────────────────────────────────────
    info("")
    info("[ Content Quality ]")
    for fpath in required_files.values():
        if not fpath.exists():
            continue
        has_ph, detail = has_placeholders(fpath)
        passed = check(f"No placeholders: {fpath.name}", not has_ph, detail)
        all_passed = all_passed and passed

    # ── CONTEXT.md specific ────────────────────────────────────────────────
    if mode != "deep_dive" and CONTEXT_MD.exists():
        info("")
        info("[ CONTEXT.md ]")

        tokens = estimate_tokens(CONTEXT_MD)
        passed = check(
            f"Token budget ≤{TOKEN_BUDGET} (estimated {tokens})",
            tokens <= TOKEN_BUDGET,
            "Trim content or extract heavy sections to .docs/deep-dives/",
        )
        all_passed = all_passed and passed

        ctx_text   = read_utf8(CONTEXT_MD)
        first_line = ctx_text.splitlines()[0] if ctx_text.strip() else ""
        passed = check(
            "Required header on line 1: '# PROJECT CONTEXT'",
            "PROJECT CONTEXT" in first_line,
            f'Got: "{first_line}"',
        )
        all_passed = all_passed and passed

        for section in ["Critical Constraints", "Tech Stack", "Entry Points", "Layer Reference"]:
            passed = check(f"Section present: '{section}'", contains_section(CONTEXT_MD, section))
            all_passed = all_passed and passed

        clean, bad_refs = check_no_line_numbers(CONTEXT_MD)
        passed = check(
            "No line-number references (only #anchors)",
            clean,
            f"Found: {bad_refs}" if bad_refs else "",
        )
        all_passed = all_passed and passed

        # Advisory: heavy sections
        heavy = _sections_over_threshold(CONTEXT_MD)
        for section_title, tok in heavy:
            info(
                f"⚠️  Section '{section_title}' is ~{tok} tokens "
                f"(>{SECTION_EXTRACT_THRESH_TOKENS}). Consider extracting."
            )

    # ── State file ─────────────────────────────────────────────────────────
    info("")
    info("[ State File ]")
    if state:
        completed = state.get("completed_phases", [])
        expected  = [p["id"] for p in phases_for_mode(mode)]
        missing   = [p for p in expected if p not in completed]
        passed    = check("All phases completed in state file", not missing,
                          f"Missing: {missing}" if missing else "")
        all_passed = all_passed and passed
    else:
        check("State file exists", False, "No .docs/.scan-state.json found")
        all_passed = False

    # ── Summary ────────────────────────────────────────────────────────────
    info("")
    if all_passed:
        info("All checks passed.")
        info("Run: python enforce.py anchor-check")
        if state:
            state["status"]  = "awaiting_anchor_check"
            state["updated"] = now_iso()
            save_state(state)
    else:
        info("Validation failed. Fix issues above, then re-run.")

    _flush_output()
    sys.exit(0 if all_passed else 1)


def cmd_anchor_check(args):
    global AGENT_MODE
    if args.agent:
        AGENT_MODE = True

    state = load_state()
    header("Anchor Validation  —  CONTEXT.md → .docs/")

    if not CONTEXT_MD.exists():
        block("CONTEXT.md not found. Complete phase_6 first.")

    results = validate_anchors(CONTEXT_MD)

    if not results:
        info("No anchor links found in CONTEXT.md.")
        info("Add links in format: [label](.docs/filename.md#section-anchor)")
        _flush_output()
        return

    all_passed = True
    for label, passed, detail in results:
        check(label, passed, detail)
        all_passed = all_passed and passed

    info("")
    if all_passed:
        info(f"All {len(results)} anchors resolve.")
        if state:
            state["status"]  = "complete"
            state["updated"] = now_iso()
            save_state(state)
            info("")
            info("── SCAN COMPLETE ────────────────────────────────────────")
            for f in state.get("files_written", []):
                info(f"  {f}")
            info(f"  CONTEXT.md  (project root)")
    else:
        failed = sum(1 for _, p, _ in results if not p)
        info(f"{failed} anchor(s) broken. Fix section headers or links, then re-run.")

    _flush_output()
    sys.exit(0 if all_passed else 1)


# ── Entry point ───────────────────────────────────────────────────────────────

def _add_agent_flag(parser):
    parser.add_argument(
        "--agent",
        action="store_true",
        default=False,
        help=(
            "Non-interactive agent mode: no stdin prompts, JSON output, "
            "machine-readable exit codes. Also set via ENFORCE_AGENT=1 env var."
        ),
    )

def main():
    global AGENT_MODE

    parser = argparse.ArgumentParser(
        description="document-project skill enforcer v2.0",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # start
    p_start = sub.add_parser("start", help="Begin a new scan")
    p_start.add_argument("--mode",  required=True,
                         choices=["initial_scan", "full_rescan", "deep_dive"])
    p_start.add_argument("--level", required=True,
                         choices=["quick", "deep", "exhaustive"])
    p_start.add_argument("--area",  help="Deep-dive area name (required for deep_dive)")
    p_start.add_argument("--force", action="store_true",
                         help="Overwrite existing scan without interactive prompt")
    _add_agent_flag(p_start)
    p_start.set_defaults(func=cmd_start)

    # done
    p_done = sub.add_parser("done", help="Mark a phase complete and validate its output")
    p_done.add_argument("phase", help="phase_1..phase_6 or step_1..step_6")
    _add_agent_flag(p_done)
    p_done.set_defaults(func=cmd_done)

    # status
    p_status = sub.add_parser("status", help="Show current scan progress")
    _add_agent_flag(p_status)
    p_status.set_defaults(func=cmd_status)

    # resume
    p_resume = sub.add_parser("resume", help="Resume from last checkpoint")
    _add_agent_flag(p_resume)
    p_resume.set_defaults(func=cmd_resume)

    # validate
    p_validate = sub.add_parser("validate", help="Run full output checklist")
    _add_agent_flag(p_validate)
    p_validate.set_defaults(func=cmd_validate)

    # anchor-check
    p_anchor = sub.add_parser("anchor-check", help="Validate all #anchors in CONTEXT.md")
    _add_agent_flag(p_anchor)
    p_anchor.set_defaults(func=cmd_anchor_check)

    args = parser.parse_args()

    # Propagate env-var agent mode before dispatch
    if os.environ.get("ENFORCE_AGENT", "").strip() in ("1", "true", "yes"):
        AGENT_MODE = True

    try:
        args.func(args)
    except SystemExit:
        raise
    except Exception as e:
        _emit({"type": "fatal", "reason": f"Unexpected error: {e}"})
        _flush_output()
        sys.exit(3)


if __name__ == "__main__":
    main()
