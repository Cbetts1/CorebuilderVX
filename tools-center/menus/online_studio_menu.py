"""
online_studio_menu.py — Website Builder & Online Studio menu.

Top-level menu for the new Online Studio system.
Replaces the old website builder entry point with a stable,
placeholder-first, fully offline multi-mode workflow.
"""

from engines import menu_engine
from core import navigation


def show():
    """Display the Website Builder & Online Studio menu."""
    navigation.push("Website Builder & Online Studio")

    items = _build_items()
    menu_engine.show_menu(
        title="🌐  Website Builder & Online Studio",
        items=items,
        breadcrumb=navigation.breadcrumb(),
        back_fn=_go_back,
    )

    navigation.pop()


def _build_items():
    """Return the fixed list of Online Studio tools."""
    return [
        ("🌐", "Website Builder",     _run_website_builder),
        ("📝", "Program Editor",      _run_program_editor),
        ("📞", "Web Calling & Texting", _run_web_calling_texting),
    ]


# ── Tool launchers ─────────────────────────────────────────────────────────────

def _run_website_builder():
    from tools.online_studio import website_builder
    website_builder.run()


def _run_program_editor():
    from tools.online_studio import program_editor
    program_editor.run()


def _run_web_calling_texting():
    from tools.online_studio import web_calling_texting
    web_calling_texting.run()


def _go_back():
    pass  # navigation.pop() is called in show() after menu_engine returns
