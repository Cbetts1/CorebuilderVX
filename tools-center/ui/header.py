"""
header.py — Tools Center UI header renderer.
"""

from engines import ui_engine as ui
from ui import themes


def render(title: str = "TOOLS CENTER", breadcrumb: str = ""):
    """Print the full page header: box title + optional breadcrumb."""
    ui.clear()
    _print_box(title)
    if breadcrumb:
        crumb_line = f"  {themes.get('subtitle')}{breadcrumb}{ui.RESET}"
        print(crumb_line)
    print(ui.hr("─", themes.get("hr")))


def _print_box(title: str):
    colour = themes.get("title")
    subtitle = "All tools. One place. No clutter."
    lines = [title, subtitle]
    box = ui.box(lines)
    for line in box.split("\n"):
        print(ui.centre(f"{colour}{line}{ui.RESET}"))
    print()
