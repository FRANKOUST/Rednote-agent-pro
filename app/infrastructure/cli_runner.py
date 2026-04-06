from __future__ import annotations

import subprocess
from dataclasses import dataclass
from time import sleep


@dataclass(slots=True)
class CLIRunResult:
    command: list[str]
    returncode: int
    stdout: str
    stderr: str
    timed_out: bool = False
    attempts: int = 1


def run_cli_command(command: list[str], cwd: str | None, timeout_seconds: int, max_retries: int = 0) -> CLIRunResult:
    attempt = 0
    last_error: CLIRunResult | None = None
    while attempt <= max_retries:
        attempt += 1
        try:
            completed = subprocess.run(
                command,
                cwd=cwd,
                text=True,
                capture_output=True,
                timeout=timeout_seconds,
                check=False,
            )
            result = CLIRunResult(
                command=command,
                returncode=completed.returncode,
                stdout=completed.stdout,
                stderr=completed.stderr,
                attempts=attempt,
            )
            if completed.returncode == 0:
                return result
            last_error = result
        except subprocess.TimeoutExpired as exc:
            last_error = CLIRunResult(
                command=command,
                returncode=-1,
                stdout=exc.stdout or "",
                stderr=exc.stderr or "",
                timed_out=True,
                attempts=attempt,
            )
        if attempt <= max_retries:
            sleep(min(2, attempt))
    return last_error or CLIRunResult(command=command, returncode=-1, stdout="", stderr="unknown cli failure", attempts=attempt)
