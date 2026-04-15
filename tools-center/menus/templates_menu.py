"""
templates_menu.py — Tools Center Templates menu.

Loads tools from the registry for the 'templates' group,
renders a numbered list, and dispatches to tool handlers.
"""

from engines import menu_engine
from core import navigation, state
from ui import icons


def show():
    """Display the Templates menu."""
    navigation.push("Templates")

    items = _build_items()
    menu_engine.show_menu(
        title="📁  Templates",
        items=items,
        breadcrumb=navigation.breadcrumb(),
        back_fn=_go_back,
    )

    navigation.pop()


def _build_items():
    """Return list of (icon, label, handler_fn) from registry for this group."""
    tools = [t for t in state.registry if t.get("group") == "templates"]
    result = []
    for tool in tools:
        icon  = tool.get("icon", icons.get("templates"))
        label = tool.get("label", tool["id"])
        fn    = _make_handler(tool)
        result.append((icon, label, fn))
    # Fallback: hard-coded items if registry is empty
    if not result:
        result = _fallback_items()
    return result


def _make_handler(tool: dict):
    """Return a callable that runs or simulates the tool."""
    def handler():
        from engines import simulation_engine
        if simulation_engine.is_active() and tool.get("supports_simulation"):
            _import_and_call(tool["handler"], "simulate")
        else:
            _import_and_call(tool["handler"], "run")
    return handler


def _import_and_call(handler_path: str, fn_name: str):
    import importlib
    parts = handler_path.rsplit(".", 1)
    if len(parts) != 2:
        print(f"  Invalid handler: {handler_path}")
        return
    module_path, _ = parts
    try:
        mod = importlib.import_module(module_path)
        fn  = getattr(mod, fn_name, None)
        if fn:
            fn()
        else:
            print(f"  {fn_name}() not found in {module_path}")
    except ImportError as exc:
        print(f"  Could not import {module_path}: {exc}")


def _fallback_items():
    """Hard-coded fallback items used when registry is unavailable."""
    return [
        ("{}", "List Templates", lambda: print("  Running: List Templates")),
        ("{}", "Apply Template", lambda: print("  Running: Apply Template")),
    ]


def _go_back():
    pass  # navigation.pop() is called in show() after menu_engine returns
