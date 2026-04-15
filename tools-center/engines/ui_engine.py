"""
ui_engine.py — Tools Center UI rendering engine.

Manages terminal dimensions, colour codes, and
provides low-level print helpers used by ui/ components.
"""

import os
import shutil
from typing import Optional

# ── ANSI colour codes ──────────────────────────────────────────────────────────

RESET   = "\033[0m"
BOLD    = "\033[1m"
DIM     = "\033[2m"

BLACK   = "\033[30m"
RED     = "\033[31m"
GREEN   = "\033[32m"
YELLOW  = "\033[33m"
BLUE    = "\033[34m"
MAGENTA = "\033[35m"
CYAN    = "\033[36m"
WHITE   = "\033[37m"

BG_BLACK  = "\033[40m"
BG_BLUE   = "\033[44m"
BG_CYAN   = "\033[46m"

_colour_enabled: bool = True


def enable_colour(enabled: bool = True):
    """Enable or disable ANSI colour output."""
    global _colour_enabled
    _colour_enabled = enabled


def c(code: str, text: str) -> str:
    """Wrap text in an ANSI code, or return plain text if colour is disabled."""
    if _colour_enabled:
        return f"{code}{text}{RESET}"
    return text


def terminal_width() -> int:
    """Return the current terminal column width (default 80)."""
    size = shutil.get_terminal_size(fallback=(80, 24))
    return size.columns


def terminal_height() -> int:
    """Return the current terminal row height (default 24)."""
    size = shutil.get_terminal_size(fallback=(80, 24))
    return size.lines


def clear():
    """Clear the terminal screen."""
    os.system("cls" if os.name == "nt" else "clear")


def hr(char: str = "─", colour: Optional[str] = None) -> str:
    """Return a horizontal rule spanning the terminal width."""
    line = char * terminal_width()
    return c(colour, line) if colour else line


def centre(text: str, width: Optional[int] = None) -> str:
    """Return text centred within the given width (defaults to terminal width)."""
    w = width or terminal_width()
    return text.center(w)


def box(lines: list, padding: int = 1) -> str:
    """Render a simple Unicode box around a list of text lines."""
    w = max(len(l) for l in lines) + padding * 2
    top    = "╔" + "═" * (w + 2) + "╗"
    bottom = "╚" + "═" * (w + 2) + "╝"
    padded = [f"║ {l.ljust(w)} ║" for l in lines]
    return "\n".join([top] + padded + [bottom])
