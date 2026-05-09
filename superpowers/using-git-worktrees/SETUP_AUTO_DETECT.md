# Setup Auto-Detection

## Supported Project Types

| Type | Detection File | Setup Command |
|------|---------------|---------------|
| Node.js | `package.json` | `npm install` |
| Rust | `Cargo.toml` | `cargo build` |
| Python | `requirements.txt` | `pip install -r requirements.txt` |
| Python (Poetry) | `pyproject.toml` | `poetry install` |
| Go | `go.mod` | `go mod download` |

## Implementation

```bash
# Node.js
if [ -f package.json ]; then npm install; fi

# Rust
if [ -f Cargo.toml ]; then cargo build; fi

# Python
if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
if [ -f pyproject.toml ]; then poetry install; fi

# Go
if [ -f go.mod ]; then go mod download; fi
```

**Note:** If no recognized project file is found, skip dependency installation.