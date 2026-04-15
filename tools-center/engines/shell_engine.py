"""
shell_engine.py — Tools Center shell execution engine.

Provides safe subprocess execution, interactive shell
launching, and command history tracking.
"""

import os
import subprocess
import shlex
from typing import List, Tuple, Optional

_history: List[str] = []
_MAX_HISTORY = 200


def run_command(
    command: str,
    cwd: Optional[str] = None,
    capture: bool = True,
    timeout: int = 30,
) -> Tuple[int, str, str]:
    """
    Execute a shell command.

    :param command:  The command string to run.
    :param cwd:      Working directory (defaults to cwd of the process).
    :param capture:  If True, capture stdout/stderr; if False, inherit terminal.
    :param timeout:  Seconds before the command is killed.
    :returns:        (returncode, stdout, stderr)
    """
    _record_history(command)
    try:
        args = shlex.split(command)
        proc = subprocess.run(
            args,
            cwd=cwd,
            capture_output=capture,
            text=True,
            timeout=timeout,
        )
        return proc.returncode, proc.stdout or "", proc.stderr or ""
    except subprocess.TimeoutExpired:
        return -1, "", f"Command timed out after {timeout}s: {command}"
    except FileNotFoundError as exc:
        return -1, "", str(exc)
    except Exception as exc:  # noqa: BLE001
        return -1, "", f"Unexpected error: {exc}"


def open_interactive_shell(shell: str = None):
    """
    Replace the current process with an interactive shell session.
    The user types 'exit' to return to the Tools Center.
    """
    shell = shell or os.environ.get("SHELL", "/bin/sh")
    print(f"\n  Launching {shell}  (type 'exit' to return)\n")
    try:
        subprocess.run([shell], check=False)
    except FileNotFoundError:
        print(f"  Shell not found: {shell}")


def get_history() -> List[str]:
    """Return the list of previously run commands."""
    return list(_history)


def clear_history():
    """Clear the command history."""
    _history.clear()


# ── Private ────────────────────────────────────────────────────────────────────

def _record_history(command: str):
    if command and (not _history or _history[-1] != command):
        _history.append(command)
        if len(_history) > _MAX_HISTORY:
            _history.pop(0)
