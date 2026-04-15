"""
logger.py — Tools Center logging utility.

Writes timestamped log entries to storage/logs/tools_center.log
and optionally echoes them to stdout.
"""

import os
import sys
import datetime

LOG_DIR = os.path.join(os.path.dirname(__file__), "..", "storage", "logs")
LOG_FILE = os.path.join(LOG_DIR, "tools_center.log")

LEVELS = {"DEBUG": 0, "INFO": 1, "WARNING": 2, "ERROR": 3}


def _ensure_log_dir():
    os.makedirs(LOG_DIR, exist_ok=True)


def _timestamp():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def log(level: str, message: str, echo: bool = False):
    """Write a log entry at the given level."""
    _ensure_log_dir()
    level = level.upper()
    entry = f"[{_timestamp()}] [{level}] {message}"
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(entry + "\n")
    if echo:
        print(entry, file=sys.stderr if level in ("WARNING", "ERROR") else sys.stdout)


def debug(message: str, echo: bool = False):
    log("DEBUG", message, echo)


def info(message: str, echo: bool = False):
    log("INFO", message, echo)


def warning(message: str, echo: bool = True):
    log("WARNING", message, echo)


def error(message: str, echo: bool = True):
    log("ERROR", message, echo)


def get_log_path() -> str:
    """Return the absolute path to the log file."""
    return os.path.abspath(LOG_FILE)
