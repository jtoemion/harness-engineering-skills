import subprocess
import json
import time


class WatchBridge:
    _process: subprocess.Popen | None = None

    @classmethod
    def get(cls) -> "WatchBridge":
        if cls._process is None or cls._process.poll() is not None:
            cls._process = subprocess.Popen(
                ["node", "skills/harness/runtime/flow-watcher/flow-watcher.js"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                text=True,
                bufsize=1,
            )
        return cls()

    def watch(self, input_text: str) -> dict:
        request = json.dumps({"input": input_text}) + "\n"
        self._process.stdin.write(request)
        self._process.stdin.flush()

        result = self._read_response()
        if result is None:
            self._restart()
            return watch_fallback(input_text)
        return result

    def _read_response(self) -> dict | None:
        start = time.time()
        while time.time() - start < 10:
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
        type(self)._process = subprocess.Popen(
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
            try:
                self._process.stdin.close()
                self._process.stdout.close()
                self._process.kill()
                self._process.wait()
            except Exception:
                pass
        type(self)._process = None


def watch_fallback(input_text: str) -> dict:
    input_lower = input_text.lower()
    alerts = []

    if any(w in input_lower for w in ["complete", "done", "fixed", "working", "all set", "finished"]):
        alerts.append({"pattern_id": "claim-without-verification", "confidence": 0.7})

    if any(w in input_lower for w in ["skip", "skipping", "skip the", "skip step", "skip verification", "skip review", "skip planning"]):
        alerts.append({"pattern_id": "skip-skill-steps", "confidence": 0.7})

    if any(w in input_lower for w in ["close session", "end session", "wrapping up", "wrap up"]):
        alerts.append({"pattern_id": "skip-session-close", "confidence": 0.7})

    if any(w in input_lower for w in ["should work", "probably works", "assume it", "assume this", "this should"]):
        alerts.append({"pattern_id": "no-evidence-claim", "confidence": 0.7})

    if any(w in input_lower for w in ["--force", "force push", "hard reset", "--hard"]):
        alerts.append({"pattern_id": "force-push-risk", "confidence": 0.7})

    if not alerts:
        return {"alerts": [], "gate": "PASS", "reason": "keyword-fallback"}

    return {"alerts": alerts, "gate": "WARN", "reason": "keyword-fallback"}