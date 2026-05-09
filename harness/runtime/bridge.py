import subprocess
import json
import time
import threading
import yaml


class QwenBridge:
    _process: subprocess.Popen | None = None

    @classmethod
    def get(cls) -> "QwenBridge":
        if cls._process is None or cls._process.poll() is not None:
            cls._process = subprocess.Popen(
                ["node", "skills/harness/runtime/flow-watcher/flow-watcher.js"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                text=True,
                bufsize=1,
            )
        return cls()

    def ask(self, mode: str, payload: dict) -> dict:
        request = json.dumps({"mode": mode, **payload}) + "\n"
        self._process.stdin.write(request)
        self._process.stdin.flush()

        result = self._read_response()
        if result is None:
            self._restart()
            return get_fallback_skill(payload.get("input", ""), payload.get("state", {}))
        return result

    def _read_response(self) -> dict | None:
        result = []
        start = time.time()
        while time.time() - start < 5:
            line = self._process.stdout.readline()
            if line:
                try:
                    return json.loads(line)
                except json.JSONDecodeError:
                    continue
            time.sleep(0.01)
        return None

    def _restart(self):
        if self._process and self._process.poll() is None:
            self._process.kill()
        self._process = subprocess.Popen(
            ["node", "skills/harness/runtime/flow-watcher/flow-watcher.js"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True,
            bufsize=1,
        )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._process:
            self._process.stdin.close()
            self._process.stdout.close()
            self._process.kill()
            self._process.wait()


def get_fallback_skill(input: str, state) -> dict:
    input_lower = input.lower()

    if "refactor" in input_lower or "restructure" in input_lower:
        return {"skill": "architectural-impact", "confidence": 0.7, "source": "yaml-fallback"}
    if "frontend" in input_lower or "ui" in input_lower or "css" in input_lower:
        return {"skill": "frontend-avant-garde", "confidence": 0.7, "source": "yaml-fallback"}
    if "test" in input_lower:
        return {"skill": "test-driven-development", "confidence": 0.7, "source": "yaml-fallback"}
    if "debug" in input_lower or "fix" in input_lower or "bug" in input_lower:
        return {"skill": "systematic-debugging", "confidence": 0.7, "source": "yaml-fallback"}
    if "plan" in input_lower or "design" in input_lower:
        return {"skill": "writing-plans", "confidence": 0.7, "source": "yaml-fallback"}
    if "memory" in input_lower or "vault" in input_lower:
        return {"skill": "memorybank", "confidence": 0.7, "source": "yaml-fallback"}
    if "git" in input_lower or "branch" in input_lower:
        return {"skill": "using-git-worktrees", "confidence": 0.7, "source": "yaml-fallback"}
    if "session" in input_lower or "close" in input_lower:
        return {"skill": "session-graph", "confidence": 0.7, "source": "yaml-fallback"}
    if "review" in input_lower:
        return {"skill": "requesting-code-review", "confidence": 0.7, "source": "yaml-fallback"}

    return {"skill": "karpathy-guidelines", "confidence": 0.3, "source": "yaml-fallback"}