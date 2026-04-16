"""
virtual_storage_menu.py — Tools Center Virtual Storage menu.

Loads tools from the registry for the 'virtual_storage' group,
renders a numbered list, and dispatches to tool handlers.
"""

from engines import menu_engine
from core import navigation, state
from ui import icons


def show():
    """Display the Virtual Storage menu."""
    navigation.push("Virtual Storage")

    items = _build_items()
    menu_engine.show_menu(
        title="💾  Virtual Storage",
        items=items,
        breadcrumb=navigation.breadcrumb(),
        back_fn=_go_back,
    )

    navigation.pop()


def _build_items():
    """Return list of (icon, label, handler_fn) from registry for this group."""
    tools = [t for t in state.registry if t.get("group") == "virtual_storage"]
    result = []
    for tool in tools:
        icon  = tool.get("icon", icons.get("virtual_storage"))
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
    """Import handler_path as a module and call fn_name() on it."""
    import importlib
    try:
        mod = importlib.import_module(handler_path)
        fn  = getattr(mod, fn_name, None)
        if fn:
            fn()
        else:
            print(f"  {fn_name}() not found in {handler_path}")
    except ImportError as exc:
        print(f"  Could not import {handler_path}: {exc}")


def _fallback_items():
    """Hard-coded fallback items used when registry is unavailable."""
    return [
        ("{}", "Create Virtual Drive", lambda: print("  Running: Create Virtual Drive")),
        ("{}", "List Virtual Drives", lambda: print("  Running: List Virtual Drives")),
    ]


def _go_back():
    pass  # navigation.pop() is called in show() after menu_engine returns
