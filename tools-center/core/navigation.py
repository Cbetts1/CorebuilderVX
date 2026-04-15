"""
navigation.py — Tools Center navigation stack.

Provides a simple push/pop menu stack so users can
navigate back through menus without losing context.
"""

from typing import List, Optional

_stack: List[str] = []


def push(menu_name: str):
    """Push a menu onto the navigation stack."""
    _stack.append(menu_name)


def pop() -> Optional[str]:
    """Pop the top menu from the stack. Returns None if stack is empty."""
    if _stack:
        return _stack.pop()
    return None


def current() -> Optional[str]:
    """Return the current (top) menu name without popping."""
    if _stack:
        return _stack[-1]
    return None


def previous() -> Optional[str]:
    """Return the menu below the current one, without modifying the stack."""
    if len(_stack) >= 2:
        return _stack[-2]
    return None


def depth() -> int:
    """Return the current stack depth."""
    return len(_stack)


def clear():
    """Clear the navigation stack entirely."""
    _stack.clear()


def breadcrumb(separator: str = " > ") -> str:
    """Return a breadcrumb string of the full navigation path."""
    return separator.join(_stack) if _stack else "Home"
