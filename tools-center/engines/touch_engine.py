"""
touch_engine.py — Tools Center touch/input engine.

Abstracts keyboard input and (future) touch events.
Provides a consistent interface for all menus and tools.
"""

import sys
import tty
import termios
from typing import Optional

# Key constants
KEY_UP    = "UP"
KEY_DOWN  = "DOWN"
KEY_LEFT  = "LEFT"
KEY_RIGHT = "RIGHT"
KEY_ENTER = "ENTER"
KEY_ESC   = "ESC"
KEY_BACK  = "BACK"


def read_key() -> str:
    """
    Read a single keypress from stdin without echoing.
    Returns a KEY_* constant or the character itself.
    Works on POSIX terminals; falls back to input() on Windows.
    """
    if sys.platform == "win32":
        return _read_key_windows()
    return _read_key_posix()


def _read_key_posix() -> str:
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
        if ch == "\x1b":
            ch2 = sys.stdin.read(1)
            ch3 = sys.stdin.read(1)
            seq = ch2 + ch3
            mapping = {
                "[A": KEY_UP,
                "[B": KEY_DOWN,
                "[C": KEY_RIGHT,
                "[D": KEY_LEFT,
            }
            return mapping.get(seq, KEY_ESC)
        if ch in ("\r", "\n"):
            return KEY_ENTER
        if ch == "\x7f":
            return KEY_BACK
        return ch
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)


def _read_key_windows() -> str:
    try:
        import msvcrt  # type: ignore
        ch = msvcrt.getwch()
        if ch in ("\r", "\n"):
            return KEY_ENTER
        if ch == "\x1b":
            return KEY_ESC
        if ch == "\xe0":
            ch2 = msvcrt.getwch()
            mapping = {
                "H": KEY_UP,
                "P": KEY_DOWN,
                "M": KEY_RIGHT,
                "K": KEY_LEFT,
            }
            return mapping.get(ch2, KEY_ESC)
        return ch
    except ImportError:
        return input("key> ")


def prompt(text: str = "  Select › ") -> str:
    """Read a line of text input from the user."""
    try:
        return input(text).strip()
    except (EOFError, KeyboardInterrupt):
        return ""


def confirm(question: str) -> bool:
    """Ask a yes/no question. Returns True for yes."""
    answer = prompt(f"{question} [y/N] ").lower()
    return answer in ("y", "yes")
