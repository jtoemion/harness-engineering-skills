"""
ill.py — Iterative Learning Layer (ILL) operations

Capture inefficiencies and wins, synthesize patterns.
"""

import os
import re
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass
from enum import Enum


class Severity(Enum):
    """ILL capture severity levels."""
    FRICTION = "FRICTION"
    BLOCKER = "BLOCKER"


class Tag(Enum):
    """ILL capture tags."""
    DELEGATION = "delegation"
    PROMPT_QUALITY = "prompt-quality"
    SCOPE_CREEP = "scope-creep"
    CACHE = "cache"
    MEMORY = "memory"
    SUBAGENT = "subagent"
    PROTOCOL = "protocol"


@dataclass
class Capture:
    """ILL inefficiency capture entry."""
    timestamp: datetime
    tag: Tag
    severity: Severity
    description: str
    context: str
    pattern: str
    project: str = "GLOBAL"
    
    def to_markdown(self) -> str:
        """Convert to markdown format."""
        return f"""## [{self.timestamp.strftime("%Y-%m-%d %H:%M")}] | [{self.tag.value}] | [{self.severity.value}]
**Capture**: {self.description}
**Context**: {self.context}
**Pattern**: {self.pattern}
**Project**: {self.project}

---
"""


@dataclass
class Win:
    """ILL efficiency win entry."""
    timestamp: datetime
    tag: Tag
    description: str
    context: str
    pattern: str
    project: str = "GLOBAL"
    
    def to_markdown(self) -> str:
        """Convert to markdown format."""
        return f"""## [{self.timestamp.strftime("%Y-%m-%d %H:%M")}] | [{self.tag.value}]
**Win**: {self.description}
**Context**: {self.context}
**Pattern**: {self.pattern}
**Project**: {self.project}

---
"""


def get_ill_path(scope: str = "project") -> Path:
    """Get ILL directory path."""
    if scope == "global":
        root = os.environ.get("HARNESS_ROOT", Path.cwd())
        return Path(root) / ".global" / "ill"
    else:
        project_root = os.environ.get("HARNESS_PROJECT_ROOT", Path.cwd())
        return Path(project_root) / ".memory" / "ill"


def capture(description: str, tag: str = "protocol", severity: str = "FRICTION",
            context: str = "", pattern: str = "", scope: str = "project") -> None:
    """
    Capture an inefficiency to ILL captures.md.
    
    Args:
        description: What was inefficient
        tag: One of [delegation, prompt-quality, scope-creep, cache, memory, subagent, protocol]
        severity: FRICTION (minor) or BLOCKER (major)
        context: Task/feature context
        pattern: What the capture suggests
        scope: "project" (default) or "global"
    """
    try:
        tag_enum = Tag(tag.lower())
    except ValueError:
        tag_enum = Tag.PROTOCOL
    
    try:
        severity_enum = Severity(severity.upper())
    except ValueError:
        severity_enum = Severity.FRICTION
    
    capture_entry = Capture(
        timestamp=datetime.now(),
        tag=tag_enum,
        severity=severity_enum,
        description=description,
        context=context or "General work session",
        pattern=pattern or "Needs further observation",
        project="GLOBAL" if scope == "global" else os.environ.get("HARNESS_PROJECT_NAME", "PROJECT")
    )
    
    ill_path = get_ill_path(scope)
    ill_path.mkdir(parents=True, exist_ok=True)
    
    captures_file = ill_path / "captures.md"
    
    # Append to file
    with open(captures_file, "a", encoding="utf-8") as f:
        f.write(capture_entry.to_markdown())
        f.write("\n")


def win(description: str, tag: str = "protocol", context: str = "", 
        pattern: str = "", scope: str = "project") -> None:
    """
    Capture an efficiency win to ILL wins.md.
    
    Args:
        description: What worked well
        tag: One of [delegation, prompt-quality, scope-creep, cache, memory, subagent, protocol]
        context: Task/feature context
        pattern: What the win reinforces
        scope: "project" (default) or "global"
    """
    try:
        tag_enum = Tag(tag.lower())
    except ValueError:
        tag_enum = Tag.PROTOCOL
    
    win_entry = Win(
        timestamp=datetime.now(),
        tag=tag_enum,
        description=description,
        context=context or "General work session",
        pattern=pattern or "Reinforces existing practices",
        project="GLOBAL" if scope == "global" else os.environ.get("HARNESS_PROJECT_NAME", "PROJECT")
    )
    
    ill_path = get_ill_path(scope)
    ill_path.mkdir(parents=True, exist_ok=True)
    
    wins_file = ill_path / "wins.md"
    
    # Append to file
    with open(wins_file, "a", encoding="utf-8") as f:
        f.write(win_entry.to_markdown())
        f.write("\n")


def count_since_synthesis(scope: str = "project") -> int:
    """
    Count captures since last synthesis.
    
    Args:
        scope: "project" (default) or "global"
    
    Returns:
        Number of captures since last synthesis
    """
    ill_path = get_ill_path(scope)
    captures_file = ill_path / "captures.md"
    
    if not captures_file.exists():
        return 0
    
    content = captures_file.read_text(encoding="utf-8")
    
    # Count capture entries
    capture_pattern = r'^## \[\d{4}-\d{2}-\d{2}'
    captures = re.findall(capture_pattern, content, re.MULTILINE)
    
    # Find last synthesis marker
    synthesis_marker = content.find("*Last synthesis:")
    if synthesis_marker == -1:
        return len(captures)
    
    # Count captures after synthesis marker
    content_after = content[synthesis_marker:]
    captures_after = re.findall(capture_pattern, content_after, re.MULTILINE)
    
    return len(captures_after)


def synthesize(scope: str = "project") -> Dict[str, Any]:
    """
    Synthesize ILL captures into structured analysis.
    
    Args:
        scope: "project" (default) or "global"
    
    Returns:
        Dict with synthesis results and path to written synthesis.md
    """
    ill_path = get_ill_path(scope)
    
    # Read captures
    captures_file = ill_path / "captures.md"
    wins_file = ill_path / "wins.md"
    
    captures = []
    wins = []
    
    if captures_file.exists():
        content = captures_file.read_text(encoding="utf-8")
        # Parse captures (simplified)
        capture_blocks = re.split(r'\n## ', content)
        for block in capture_blocks[1:]:  # Skip header
            captures.append(block)
    
    if wins_file.exists():
        content = wins_file.read_text(encoding="utf-8")
        win_blocks = re.split(r'\n## ', content)
        for block in win_blocks[1:]:
            wins.append(block)
    
    # Generate synthesis
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    synthesis_content = f"""# ILL Synthesis

**Generated**: {timestamp}
**Scope**: {scope}

## Summary

- Total captures: {len(captures)}
- Total wins: {len(wins)}
- Captures since last synthesis: {count_since_synthesis(scope)}

## Patterns Identified

<!-- To be filled after analysis -->

### By Tag

- delegation: TBD
- prompt-quality: TBD
- scope-creep: TBD
- cache: TBD
- memory: TBD
- subagent: TBD
- protocol: TBD

## Recommendations

<!-- Synthesized recommendations -->

## Proposed Changes

<!-- Changes to be promoted -->

---

*Next synthesis triggered at: 3+ new captures*
"""
    
    # Write synthesis.md
    synthesis_file = ill_path / "synthesis.md"
    synthesis_file.write_text(synthesis_content, encoding="utf-8")
    
    # Update captures with last synthesis timestamp
    if captures_file.exists():
        with open(captures_file, "a", encoding="utf-8") as f:
            f.write(f"\n*Last synthesis: {timestamp}*\n")
    
    return {
        "synthesis_path": str(synthesis_file),
        "captures_count": len(captures),
        "wins_count": len(wins),
        "scope": scope,
        "timestamp": timestamp
    }


if __name__ == "__main__":
    # CLI for testing
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python ill.py <command> [args]")
        print("Commands: capture, win, count, synthesize")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "capture":
        capture(
            description=sys.argv[2] if len(sys.argv) > 2 else "Test capture",
            tag=sys.argv[3] if len(sys.argv) > 3 else "protocol",
            severity=sys.argv[4] if len(sys.argv) > 4 else "FRICTION"
        )
        print("✅ Capture logged")
    
    elif command == "win":
        win(
            description=sys.argv[2] if len(sys.argv) > 2 else "Test win",
            tag=sys.argv[3] if len(sys.argv) > 3 else "protocol"
        )
        print("✅ Win logged")
    
    elif command == "count":
        scope = sys.argv[2] if len(sys.argv) > 2 else "project"
        count = count_since_synthesis(scope)
        print(f"Captures since last synthesis: {count}")
    
    elif command == "synthesize":
        scope = sys.argv[2] if len(sys.argv) > 2 else "project"
        result = synthesize(scope)
        print(f"✅ Synthesis complete")
        print(f"   Path: {result['synthesis_path']}")
        print(f"   Captures: {result['captures_count']}")
        print(f"   Wins: {result['wins_count']}")
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)