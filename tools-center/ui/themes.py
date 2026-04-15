"""
themes.py — Tools Center UI themes.

Defines colour palettes used throughout the UI.
Active theme is selected via settings.
"""

from engines import ui_engine as ui

THEMES = {
    "default": {
        "title":    ui.CYAN + ui.BOLD,
        "subtitle": ui.DIM,
        "border":   ui.BLUE,
        "item":     ui.WHITE,
        "selected": ui.GREEN + ui.BOLD,
        "error":    ui.RED,
        "warning":  ui.YELLOW,
        "success":  ui.GREEN,
        "hr":       ui.DIM,
    },
    "dark": {
        "title":    ui.MAGENTA + ui.BOLD,
        "subtitle": ui.DIM,
        "border":   ui.MAGENTA,
        "item":     ui.WHITE,
        "selected": ui.CYAN + ui.BOLD,
        "error":    ui.RED,
        "warning":  ui.YELLOW,
        "success":  ui.GREEN,
        "hr":       ui.DIM,
    },
    "plain": {
        "title":    "",
        "subtitle": "",
        "border":   "",
        "item":     "",
        "selected": "",
        "error":    "",
        "warning":  "",
        "success":  "",
        "hr":       "",
    },
}

_active_theme: str = "default"


def set_theme(name: str):
    global _active_theme
    if name in THEMES:
        _active_theme = name


def get(key: str) -> str:
    """Return the ANSI code for the given theme key."""
    return THEMES.get(_active_theme, THEMES["default"]).get(key, "")


def active_name() -> str:
    return _active_theme


def available_themes():
    return list(THEMES.keys())
