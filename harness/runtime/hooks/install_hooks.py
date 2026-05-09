#!/usr/bin/env python3
"""Install pre-commit hooks for harness enforcement."""
import os
import shutil
import stat
from pathlib import Path

HOOK_SOURCE = Path(__file__).parent / "pre-commit"
HOOK_DEST = Path(".git/hooks/pre-commit")


def install_hooks():
    if not HOOK_SOURCE.exists():
        print(f"ERROR: {HOOK_SOURCE} not found")
        return False

    dest_dir = HOOK_DEST.parent
    if not dest_dir.exists():
        print("ERROR: .git/hooks directory not found")
        return False

    shutil.copy(HOOK_SOURCE, HOOK_DEST)
    os.chmod(HOOK_DEST, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)

    print(f"Installed: {HOOK_DEST}")
    return True


if __name__ == "__main__":
    install_hooks()
