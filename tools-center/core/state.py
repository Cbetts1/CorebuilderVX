"""
state.py — Tools Center global state container.

Holds runtime state: simulation mode flag, active tool,
current user, loaded registry, and engine handles.
"""

from typing import Any, Dict, Optional

# ── Runtime flags ──────────────────────────────────────────────────────────────

simulation_mode: bool = False
debug_mode: bool = False

# ── Active context ─────────────────────────────────────────────────────────────

active_tool: Optional[str] = None
active_menu: Optional[str] = None

# ── Loaded data ────────────────────────────────────────────────────────────────

registry: list = []       # loaded from tool_registry.json
settings: dict = {}       # loaded from settings/settings.json

# ── Engine handles ─────────────────────────────────────────────────────────────

engines: Dict[str, Any] = {}


# ── Helpers ────────────────────────────────────────────────────────────────────

def set_simulation(enabled: bool):
    global simulation_mode
    simulation_mode = enabled


def set_active_tool(tool_id: Optional[str]):
    global active_tool
    active_tool = tool_id


def set_active_menu(menu_name: Optional[str]):
    global active_menu
    active_menu = menu_name


def register_engine(name: str, instance: Any):
    engines[name] = instance


def get_engine(name: str) -> Optional[Any]:
    return engines.get(name)


def reset():
    """Reset runtime state (useful for testing)."""
    global simulation_mode, debug_mode, active_tool, active_menu, registry, settings
    simulation_mode = False
    debug_mode = False
    active_tool = None
    active_menu = None
    registry = []
    settings = {}
    engines.clear()
