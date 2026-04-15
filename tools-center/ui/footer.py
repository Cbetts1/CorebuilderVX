"""
footer.py — Tools Center UI footer renderer.
"""

from engines import ui_engine as ui
from ui import themes
from core import navigation


def render():
    """Print a footer with navigation breadcrumb and a divider."""
    print(ui.hr("─", themes.get("hr")))
    crumb = navigation.breadcrumb()
    sim_tag = ""
    try:
        from engines import simulation_engine
        if simulation_engine.is_active():
            sim_tag = f"  {themes.get('warning')}[SIM]{ui.RESET}"
    except ImportError:
        pass
    print(f"  {themes.get('subtitle')}📍 {crumb}{ui.RESET}{sim_tag}")
