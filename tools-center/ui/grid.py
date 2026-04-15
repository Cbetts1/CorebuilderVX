"""
grid.py — Tools Center 2-column grid renderer.

Renders a list of (icon, label) pairs in a 2-column grid,
used by the main menu panel.
"""

from typing import List, Tuple
from engines import ui_engine as ui
from ui import themes

Cell = Tuple[str, str]  # (icon, label)


def render(cells: List[Cell], col_width: int = 26):
    """
    Print cells in a 2-column grid layout.

    :param cells:     List of (icon, label) tuples.
    :param col_width: Character width of each column.
    """
    colour = themes.get("item")
    for i in range(0, len(cells), 2):
        left = _fmt(cells[i], col_width, colour)
        if i + 1 < len(cells):
            right = _fmt(cells[i + 1], col_width, colour)
        else:
            right = ""
        print(f"  {left}  {right}")
    print()


def _fmt(cell: Cell, width: int, colour: str) -> str:
    icon, label = cell
    text = f"{icon}  {label}"
    padded = text.ljust(width)
    return f"{colour}{padded}{ui.RESET}"
