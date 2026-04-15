"""
simulation_engine.py — Tools Center simulation engine.

When simulation mode is active, tools call simulate()
instead of run().  This engine tracks simulation state,
records events, and prints safe "dry-run" output.
"""

import datetime
from typing import List, Dict, Any

_active: bool = False
_events: List[Dict[str, Any]] = []


def activate():
    """Turn simulation mode on."""
    global _active
    _active = True
    _record("engine", "Simulation mode ACTIVATED")


def deactivate():
    """Turn simulation mode off."""
    global _active
    _active = False
    _record("engine", "Simulation mode DEACTIVATED")


def is_active() -> bool:
    """Return True if simulation mode is currently on."""
    return _active


def record_event(tool_id: str, description: str, data: Dict[str, Any] = None):
    """Record a simulation event from a tool."""
    _record(tool_id, description, data or {})


def get_events() -> List[Dict[str, Any]]:
    """Return the full list of recorded simulation events."""
    return list(_events)


def clear_events():
    """Clear the event log."""
    _events.clear()


def print_summary():
    """Print a summary of all simulation events to stdout."""
    if not _events:
        print("  [Simulation] No events recorded.")
        return
    print(f"\n  [Simulation] {len(_events)} event(s) recorded:")
    for e in _events:
        ts = e["timestamp"]
        src = e["source"]
        desc = e["description"]
        print(f"    {ts}  [{src}]  {desc}")
    print()


# ── Private ────────────────────────────────────────────────────────────────────

def _record(source: str, description: str, data: Dict[str, Any] = None):
    _events.append({
        "timestamp": datetime.datetime.now().strftime("%H:%M:%S"),
        "source": source,
        "description": description,
        "data": data or {},
    })
