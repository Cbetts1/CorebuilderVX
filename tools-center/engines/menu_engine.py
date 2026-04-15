"""
menu_engine.py — Tools Center menu rendering engine.

Displays numbered menus, reads user selection,
and dispatches to the appropriate handler.
"""

from typing import List, Callable, Optional, Tuple
from ui import header as ui_header, footer as ui_footer


MenuItem = Tuple[str, str, Callable]  # (icon, label, handler_fn)


def show_menu(
    title: str,
    items: List[MenuItem],
    breadcrumb: str = "",
    back_fn: Optional[Callable] = None,
) -> None:
    """
    Render a numbered menu and loop until the user exits or goes back.

    :param title:      Menu title shown in the header.
    :param items:      List of (icon, label, handler_fn) tuples.
    :param breadcrumb: Navigation breadcrumb string.
    :param back_fn:    Callable invoked when the user chooses 'back'.
    """
    while True:
        ui_header.render(title, breadcrumb)
        _render_items(items)
        _render_footer(back_fn)

        choice = _prompt()

        if choice == "0":
            if back_fn:
                back_fn()
            return

        if choice.isdigit():
            index = int(choice) - 1
            if 0 <= index < len(items):
                icon, label, fn = items[index]
                print(f"\n  → Running: {icon} {label}\n")
                try:
                    fn()
                except Exception as exc:  # noqa: BLE001
                    print(f"  ✗ Error: {exc}")
                input("\n  Press Enter to continue…")
            else:
                print("  Invalid selection.")
        else:
            print("  Please enter a number.")


def _render_items(items: List[MenuItem]):
    """Print the numbered list of menu items."""
    print()
    for i, (icon, label, _) in enumerate(items, start=1):
        print(f"  {i:>2}. {icon}  {label}")
    print()


def _render_footer(back_fn: Optional[Callable]):
    """Print navigation footer."""
    if back_fn:
        print("   0. ← Back")
    ui_footer.render()


def _prompt() -> str:
    """Read a single line of input from the user."""
    try:
        return input("  Select › ").strip()
    except (EOFError, KeyboardInterrupt):
        return "0"
