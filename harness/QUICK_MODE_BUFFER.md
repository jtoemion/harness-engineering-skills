# Quick Mode Learning Buffer

**Purpose**: Capture minimal learning from QUICK mode sessions that would otherwise be lost.

## Mechanism

### Write (Quick Mode)
At session end, append ONE line to `~/.memory/quick-buffer.jsonl`:

```json
{"timestamp": "2026-05-17T16:00:00Z", "task": "brief description", "outcome": "success|partial|blocked|failed", "files_touched": 1, "duration_minutes": 5}
```

### Flush (Full Mode Boot)
At next Full Mode boot, `harness.py boot`:
1. Check if `~/.memory/quick-buffer.jsonl` exists
2. If yes: read all lines, append to `.memory/sessions.json`
3. Delete `quick-buffer.jsonl` after flush
4. Print: "Flushed N Quick mode session(s) into sessions.json"

### Auto-Upgrade Heuristic
If during a Quick mode session:
- **>2 files touched** OR **>10 minutes elapsed**
→ Print: "This session exceeds Quick mode thresholds. Consider switching to Full Mode for persistent memory."
→ This is a SUGGESTION, not forced. User decides.

## Implementation

The buffer logic is in `harness.py`:
- `cmd_boot()` flushes the buffer at FULL mode boot
- Quick mode close writes the buffer entry (agent-managed, not code-enforced)

## File Location

- Buffer file: `C:\Users\jtoem\.memory\quick-buffer.jsonl` (user home, NOT project .memory/)
- This ensures the buffer persists across projects

## Anti-Rationalization

| If you think... | You are wrong because... |
|-----------------|--------------------------|
| "Quick mode shouldn't have any persistence" | One line per session is not persistence — it's a breadcrumb for the next Full boot |
| "Auto-upgrade is too aggressive" | It's a suggestion, not forced. The user decides. |
| "This adds complexity" | It adds 4 lines of code. The learning gap it closes is worth 100x that. |
