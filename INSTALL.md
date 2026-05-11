# Installation Guide

This guide covers two audiences: **humans** who want to set up harness in their own project, and **AI agents** who need to install harness into a fresh environment programmatically.

---

## For Humans

### Prerequisites

- Python 3.10+
- Node.js 18+
- A project with an existing `AGENTS.md` (or willingness to create one)

### Step 1: Clone the Repo

```bash
git clone https://github.com/jtoemion/harness-engineering-skills.git
cd harness-engineering-skills
```

Or if you're adding it as a submodule:

```bash
git submodule add https://github.com/jtoemion/harness-engineering-skills.git skills
```

### Step 2: Install Flow-Watcher Dependencies

```bash
cd harness/runtime/flow-watcher
npm install
```

This installs [Transformers.js](https://huggingface.co/docs/transformers.js) — the nli-deberta-v3-base model downloads on first use (~250MB).

### Step 3: Integrate Into Your AGENTS.md

Add these lines to your `AGENTS.md` (create it if you don't have one):

```
## CONFIG
```
SKILLS_ROOT     = /path/to/your/skills
MASTER_PROTOCOL  = /path/to/your/AGENTS.md
SKILL_ROUTER    = /path/to/your/skills/skill-router.yaml
DETECT_MODE     = /path/to/your/skills/detect-mode.sh (Unix) or .bat (Win)
```

Then add the harness runtime commands to your boot sequence and skill routing section. See [INTEGRATION_GUIDE.md](./INTEGRATION_GUIDE.md) for the full protocol.

### Step 4: Run Boot

```bash
cd /path/to/your/project
python /path/to/harness-engineering-skills/harness/runtime/harness.py boot
```

You should see:

```
⚡ ONLINE
  Agent   : [your agent]
  Time    : YYYY-MM-DD HH:MM
  Mode    : FULL
  Memory  : [WARM | COLD START]
  Harness : LOADED ✓
```

### Step 5: Optional — Install Git Hooks

```bash
python harness/runtime/hooks/install_hooks.py
```

This installs a `pre-commit` hook that blocks commits if a session is open.

---

## For AI Agents

Use this section when you need to install harness into a fresh project environment automatically.

### Detect if Harness is Already Installed

Check for these markers in the project root:

1. `AGENTS.md` exists and references `harness.py`
2. `.memory/` directory exists
3. `skill-router.yaml` exists

If all three exist → harness is installed, skip to Verify.

If any are missing → proceed with automated install below.

### Automated Install Sequence

#### 1. Create Directory Structure

```bash
mkdir -p skills/harness/runtime/flow-watcher
mkdir -p skills/harness/runtime/hooks
mkdir -p .memory
```

#### 2. Copy Runtime Files

The agent should copy these files from the harness-engineering-skills repo:

- `harness/runtime/harness.py`
- `harness/runtime/state.py`
- `harness/runtime/conductor.py`
- `harness/runtime/bridge.py`
- `harness/runtime/mistakes.py`
- `harness/runtime/memory_watch.py`
- `harness/runtime/checkpoint.py`
- `harness/runtime/session_close.py`
- `harness/runtime/flow-watcher/flow-watcher.js`
- `harness/runtime/flow-watcher/package.json`
- `harness/runtime/hooks/pre-commit`
- `harness/runtime/hooks/install_hooks.py`
- `harness/SKILL.md`
- `harness/MISTAKES.md`
- `harness/SESSION_CLOSE.md`
- `harness/SUBAGENT_PROTOCOL.md`
- `skill-router.yaml`
- `detect-mode.sh` (or `.bat` for Windows)

#### 3. Install Flow-Watcher Dependencies

```bash
cd skills/harness/runtime/flow-watcher && npm install
```

#### 4. Update AGENTS.md

Insert the following configuration block at the top of the project's `AGENTS.md`:

```
## CONFIG
```
SKILLS_ROOT     = /absolute/path/to/skills
MASTER_PROTOCOL = /absolute/path/to/AGENTS.md
SKILL_ROUTER    = /absolute/path/to/skills/skill-router.yaml
DETECT_MODE     = /absolute/path/to/skills/detect-mode.sh
```

Then add the skill routing section pointing to `skill-router.yaml`.

#### 5. Run Boot

```bash
python skills/harness/runtime/harness.py boot
```

#### 6. Verify

Run `python skills/harness/runtime/harness.py status` — should output the Boot Status Report.

### Environment Detection

The harness detects mode automatically:

- **FULL mode**: `.memory/` directory exists in project root
- **QUICK mode**: `.memory/` does not exist

### Dependency Verification

Verify these are available before running:

| Dependency | Check command | Required |
|-----------|--------------|----------|
| Python | `python --version` | 3.10+ |
| Node.js | `node --version` | 18+ |
| npm | `npm --version` | any |
| git | `git --version` | optional (for hooks) |
| pydantic | `python -c "import pydantic; print(pydantic.__version__)"` | 2.x |

If pydantic is missing: `pip install pydantic pyyaml`

### Post-Install Verification Checklist

- [ ] `python harness.py boot` runs without errors
- [ ] `python harness.py status` prints Boot Status Report
- [ ] `skill-router.yaml` is readable and valid YAML
- [ ] Flow-watcher initializes on first boot (model downloads ~250MB)
- [ ] `.memory/` directory was created for FULL mode
- [ ] Git hook installed (if git available)

### Troubleshooting

**"Module not found: pydantic"**
```bash
pip install pydantic pyyaml
```

**"flow-watcher.js not found"**
Flow-watcher was not copied. Ensure the `harness/runtime/flow-watcher/` directory exists with `flow-watcher.js` and `package.json`.

**"AGENTS.md not found"**
The project doesn't have an `AGENTS.md` yet. Create one with the CONFIG block pointing to your skills directory.

**"Model download fails"**
Check internet connection. The nli-deberta-v3-base model downloads from HuggingFace Hub on first run. Proxy settings may block it.