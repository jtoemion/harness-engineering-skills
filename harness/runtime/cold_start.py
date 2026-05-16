"""
cold_start.py — Cold start procedure for new projects

Creates `.memory/` with 5 files from templates.
Triggered on `ENGAGE` if no `.memory/` exists.
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional

# Template content for the 5 canonical memory files
TEMPLATES = {
    "projectbrief.md": """---
type: projectbrief
status: active
created: {timestamp}
---

# Project Brief: {project_name}

## Overview
{description}

## Goals
- [ ] Goal 1
- [ ] Goal 2
- [ ] Goal 3

## Status
- Current phase: {phase}
- Next milestone: TBD

## Notes
- Created via cold start
""",
    "activeContext.md": """---
type: activeContext
status: active
created: {timestamp}
---

# Active Context

## Current Focus
{current_focus}

## Recent Decisions
- None yet

## Next Actions
- [ ] Action 1
- [ ] Action 2

## Blockers
- None

## Notes
- Created via cold start
""",
    "progress.md": """---
type: progress
status: active
created: {timestamp}
---

# Progress Log

## Sessions

### {timestamp} — Cold Start
- Initialized project memory
- Tech stack: {stack}
- Priority: {priority}

## Completed Tasks
- [x] Project initialized

## In Progress
- [ ] Initial setup

## Upcoming
- TBD
""",
    "techContext.md": """---
type: techContext
status: active
created: {timestamp}
---

# Tech Context

## Stack
{stack}

## Architecture
- TBD

## Dependencies
- TBD

## Configuration
- TBD

## Development Environment
- TBD

## Deployment
- TBD

## Notes
- Created via cold start
""",
    "systemPatterns.md": """---
type: systemPatterns
status: active
created: {timestamp}
---

# System Patterns

## Architecture Patterns
- TBD

## Design Patterns
- TBD

## Coding Conventions
- TBD

## Testing Patterns
- TBD

## Error Handling
- TBD

## Performance Patterns
- TBD

## Notes
- Created via cold start
""",
    "SESSIONS.md": """---
type: sessions-index
status: active
created: {timestamp}
---

# Sessions Index

This file tracks all sessions for this project.

## Sessions

| Date | Session | Summary |
|------|---------|---------|
| {timestamp} | Cold Start | Project initialized |

---

*Last updated: {timestamp}*
"""
}


def create_ill_structure(memory_path: Path) -> None:
    """Create ILL (Iterative Learning Layer) directory structure."""
    ill_path = memory_path / "ill"
    ill_path.mkdir(parents=True, exist_ok=True)
    
    # Create captures.md
    captures_content = """# ILL Captures

## Inefficiency Captures

<!-- Use format: -->
<!-- ## [YYYY-MM-DD HH:MM] | [TAG] | [FRICTION|BLOCKER] -->
<!-- **Capture**: [What was inefficient] -->
<!-- **Context**: [Task/feature] -->
<!-- **Pattern**: [What it suggests] -->

---

*Last synthesis: Never*
"""
    (ill_path / "captures.md").write_text(captures_content, encoding='utf-8')
    
    # Create wins.md
    wins_content = """# ILL Wins

## Efficiency Wins

<!-- Use format: -->
<!-- ## [YYYY-MM-DD HH:MM] | [TAG] -->
<!-- **Win**: [What worked well] -->
<!-- **Context**: [Task/feature] -->
<!-- **Pattern**: [What it reinforces] -->

---

*Last synthesis: Never*
"""
    (ill_path / "wins.md").write_text(wins_content, encoding='utf-8')
    
    # Create patterns.md
    patterns_content = """# ILL Patterns

## Synthesized Patterns

<!-- Patterns are created via synthesis, not manual entry -->

---

*Last updated: Never*
"""
    (ill_path / "patterns.md").write_text(patterns_content, encoding='utf-8')
    
    # Create changelog.md
    changelog_content = """# ILL Changelog

## Approved Changes

<!-- Changes are promoted here after human approval -->

---

*Last updated: Never*
"""
    (ill_path / "changelog.md").write_text(changelog_content, encoding='utf-8')


def cold_start(project_name: str, stack: str = "unknown", 
               description: str = "", priority: str = "setup",
               project_root: Optional[str] = None) -> Path:
    """
    Initialize a new project with cold start procedure.
    
    Args:
        project_name: Name of the project
        stack: Technology stack (frontend, backend, database, etc.)
        description: One-sentence project description
        priority: Current priority/focus
        project_root: Root directory for the project (defaults to current working directory)
    
    Returns:
        Path to the created .memory/ directory
    """
    # Set project root
    if project_root is None:
        project_root = Path.cwd()
    else:
        project_root = Path(project_root)
    
    # Set environment variable
    os.environ["HARNESS_PROJECT_ROOT"] = str(project_root)
    
    # Create .memory/ directory
    memory_path = project_root / ".memory"
    memory_path.mkdir(parents=True, exist_ok=True)
    
    # Generate timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    # Create the 5 canonical memory files
    template_vars = {
        "project_name": project_name,
        "description": description or f"Project {project_name}",
        "stack": stack,
        "priority": priority,
        "phase": priority,
        "current_focus": priority,
        "timestamp": timestamp
    }
    
    for filename, template in TEMPLATES.items():
        content = template.format(**template_vars)
        filepath = memory_path / filename
        filepath.write_text(content, encoding='utf-8')
    
    # Create ILL structure
    create_ill_structure(memory_path)
    
    return memory_path


def main():
    """CLI entry point for cold start."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Cold start a new project")
    parser.add_argument("project_name", help="Name of the project")
    parser.add_argument("--stack", default="unknown", help="Technology stack")
    parser.add_argument("--description", default="", help="Project description")
    parser.add_argument("--priority", default="setup", help="Current priority")
    parser.add_argument("--root", default=None, help="Project root directory")
    
    args = parser.parse_args()
    
    memory_path = cold_start(
        project_name=args.project_name,
        stack=args.stack,
        description=args.description,
        priority=args.priority,
        project_root=args.root
    )
    
    print(f"✅ Cold start complete: {memory_path}")
    print(f"   HARNESS_PROJECT_ROOT={os.environ.get('HARNESS_PROJECT_ROOT')}")


if __name__ == "__main__":
    main()