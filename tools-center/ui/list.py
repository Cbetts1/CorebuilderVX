"""
list.py — Tools Center numbered list renderer.

Renders a vertical numbered list with icons and labels.
Used by category menus.
"""

from typing import List, Tuple
from engines import ui_engine as ui
from ui import themes

Item = Tuple[str, str]  # (icon, label)


def render(items: List[Item], start: int = 1):
    """
    Print a numbered vertical list of items.

    :param items: List of (icon, label) tuples.
    :param start: Starting number (default 1).
    """
    colour = themes.get("item")
    for i, (icon, label) in enumerate(items, start=start):
        line = f"  {i:>2}. {icon}  {label}"
        print(f"{colour}{line}{ui.RESET}")
    print()
