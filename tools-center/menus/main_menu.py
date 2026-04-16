"""
main_menu.py — Tools Center main menu.

Entry point after startup.  Renders the 2-column grid of
all tool groups and dispatches to the appropriate category menu.
"""

from ui import header, grid
from ui import themes
from engines import ui_engine as ui
from core import navigation, state


def show():
    """Display the main menu and handle navigation."""
    navigation.clear()
    navigation.push("Main Menu")

    ENTRIES = [
        ("🛠️",  "Build Tools",                      _go_build),
        ("💻",  "Code Tools",                       _go_code),
        ("🌐",  "Web Tools",                        _go_web),
        ("🖥️",  "Website Builder & Online Studio",  _go_site_builder),
        ("📦",  "Program Tools",      _go_program),
        ("⚙️",  "AI Tools",           _go_ai),
        ("🖥️",  "VM Tools",           _go_vm),
        ("🎛️",  "Simulation Tools",   _go_simulation),
        ("💾",  "Virtual Storage",    _go_virtual_storage),
        ("☁️",  "Cloud Tools",        _go_cloud),
        ("🔌",  "Backend Tools",      _go_backend),
        ("📂",  "Storage Tools",      _go_storage),
        ("🩺",  "Diagnostics",        _go_diagnostics),
        ("📡",  "Network Tools",      _go_network),
        ("🔧",  "Hardware Tools",     _go_hardware),
        ("📁",  "Templates",          _go_templates),
        ("📘",  "Learning",           _go_learning),
        (">_",  "Shell Tools",        _go_shell),
        ("⚙️",  "Settings",           _go_settings),
    ]

    while True:
        header.render("TOOLS CENTER", navigation.breadcrumb())

        cells = [(icon, label) for icon, label, _ in ENTRIES]
        grid.render(cells)

        sim_status = ""
        try:
            from engines import simulation_engine
            if simulation_engine.is_active():
                sim_status = f"  {themes.get('warning')}[SIMULATION MODE ON]{ui.RESET}\n"
        except ImportError:
            pass

        if sim_status:
            print(sim_status)

        print(f"  {themes.get('item')}⏻  Exit{ui.RESET}")
        print(ui.hr("─", themes.get("hr")))

        try:
            choice = input("  Select › ").strip()
        except (EOFError, KeyboardInterrupt):
            break

        if not choice.isdigit():
            continue

        idx = int(choice) - 1
        if 0 <= idx < len(ENTRIES):
            _, _, fn = ENTRIES[idx]
            fn()
        elif int(choice) == len(ENTRIES) + 1 or choice == "0":
            break


# ── Navigation helpers ─────────────────────────────────────────────────────────

def _go_build():
    from menus import build_menu
    build_menu.show()

def _go_code():
    from menus import code_menu
    code_menu.show()

def _go_web():
    from menus import web_menu
    web_menu.show()

def _go_site_builder():
    from menus import site_builder_menu
    site_builder_menu.show()

def _go_program():
    from menus import program_menu
    program_menu.show()

def _go_ai():
    from menus import ai_menu
    ai_menu.show()

def _go_vm():
    from menus import vm_menu
    vm_menu.show()

def _go_simulation():
    from menus import simulation_menu
    simulation_menu.show()

def _go_virtual_storage():
    from menus import virtual_storage_menu
    virtual_storage_menu.show()

def _go_cloud():
    from menus import cloud_menu
    cloud_menu.show()

def _go_backend():
    from menus import backend_menu
    backend_menu.show()

def _go_storage():
    from menus import storage_menu
    storage_menu.show()

def _go_diagnostics():
    from menus import diagnostics_menu
    diagnostics_menu.show()

def _go_network():
    from menus import network_menu
    network_menu.show()

def _go_hardware():
    from menus import hardware_menu
    hardware_menu.show()

def _go_templates():
    from menus import templates_menu
    templates_menu.show()

def _go_learning():
    from menus import learning_menu
    learning_menu.show()

def _go_shell():
    from menus import shell_menu
    shell_menu.show()

def _go_settings():
    from menus import settings_menu
    settings_menu.show()
