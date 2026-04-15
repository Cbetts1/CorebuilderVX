"""
startup.py — Tools Center startup sequence.

Runs the following steps in order:
  1. Load settings
  2. Initialize engines
  3. Load registry
  4. Prepare UI
  5. Preload menus
  6. Preload tools
  7. Show main menu
"""

import os
import sys
import json

# Ensure the tools-center directory is on sys.path
_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)


def run():
    """Execute the full startup sequence and launch the main menu."""
    _step1_load_settings()
    _step2_init_engines()
    _step3_load_registry()
    _step4_prepare_ui()
    _step5_preload_menus()
    _step6_preload_tools()
    _step7_show_main_menu()


# ── Step 1: Load settings ──────────────────────────────────────────────────────

def _step1_load_settings():
    from engines import settings_engine
    from core import state, logger
    settings_engine.load()
    state.settings = settings_engine.all_settings()
    logger.info("Settings loaded.", echo=False)


# ── Step 2: Initialize engines ─────────────────────────────────────────────────

def _step2_init_engines():
    from core import state, logger
    from engines import (
        ui_engine,
        simulation_engine,
        virtual_storage_engine,
        cloud_engine,
        shell_engine,
        settings_engine,
        menu_engine,
        touch_engine,
    )

    # Apply colour preference from settings
    colour = state.settings.get("colour_enabled", True)
    ui_engine.enable_colour(colour)

    # Apply simulation mode preference
    if state.settings.get("simulation_mode", False):
        simulation_engine.activate()

    # Register handles in global state
    state.register_engine("ui",          ui_engine)
    state.register_engine("simulation",  simulation_engine)
    state.register_engine("virt_store",  virtual_storage_engine)
    state.register_engine("cloud",       cloud_engine)
    state.register_engine("shell",       shell_engine)
    state.register_engine("settings",    settings_engine)
    state.register_engine("menu",        menu_engine)
    state.register_engine("touch",       touch_engine)

    logger.info("Engines initialized.", echo=False)


# ── Step 3: Load registry ──────────────────────────────────────────────────────

def _step3_load_registry():
    from core import state, logger

    registry_path = os.path.join(_HERE, "core", "tool_registry.json")
    if os.path.exists(registry_path):
        with open(registry_path, encoding="utf-8") as f:
            state.registry = json.load(f)
        logger.info(f"Registry loaded: {len(state.registry)} tools.", echo=False)
    else:
        state.registry = []
        logger.warning(f"Registry not found: {registry_path}")


# ── Step 4: Prepare UI ─────────────────────────────────────────────────────────

def _step4_prepare_ui():
    from core import state, logger
    from ui import themes

    theme_name = state.settings.get("theme", "default")
    themes.set_theme(theme_name)
    logger.info(f"UI theme set to '{theme_name}'.", echo=False)


# ── Step 5: Preload menus ──────────────────────────────────────────────────────

def _step5_preload_menus():
    from core import logger
    import importlib

    menu_names = [
        "menus.main_menu",
        "menus.build_menu",
        "menus.code_menu",
        "menus.web_menu",
        "menus.program_menu",
        "menus.ai_menu",
        "menus.vm_menu",
        "menus.simulation_menu",
        "menus.virtual_storage_menu",
        "menus.cloud_menu",
        "menus.backend_menu",
        "menus.storage_menu",
        "menus.diagnostics_menu",
        "menus.network_menu",
        "menus.hardware_menu",
        "menus.templates_menu",
        "menus.learning_menu",
        "menus.shell_menu",
        "menus.settings_menu",
    ]
    for name in menu_names:
        try:
            importlib.import_module(name)
        except ImportError as exc:
            logger.warning(f"Could not preload menu '{name}': {exc}")

    logger.info("Menus preloaded.", echo=False)


# ── Step 6: Preload tools ──────────────────────────────────────────────────────

def _step6_preload_tools():
    from core import state, logger
    import importlib

    loaded = 0
    for tool in state.registry:
        handler = tool.get("handler", "")
        module_path = handler.rsplit(".", 1)[0] if "." in handler else handler
        if module_path:
            try:
                importlib.import_module(module_path)
                loaded += 1
            except ImportError:
                pass  # Silently skip; tool will report error when invoked

    logger.info(f"Tools preloaded: {loaded}/{len(state.registry)}.", echo=False)


# ── Step 7: Show main menu ─────────────────────────────────────────────────────

def _step7_show_main_menu():
    from menus import main_menu
    main_menu.show()
