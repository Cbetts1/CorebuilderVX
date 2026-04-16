"""
create_project.py — Create a new website project.

Prompts for a project name and template, copies the chosen template
into builds/websites/<name>, and records the entry in the project index.
"""

import os
import sys


def run():
    """Real behaviour: create a new website project from a template."""
    print("  [Website Builder] Create Project")
    _execute()


def simulate():
    """Safe dry-run behaviour: describe what would be created without writing files."""
    print("  [SIM] [Website Builder] Simulating project creation (no real changes)...")
    _cbx_root = _get_root()
    templates_dir = os.path.join(_cbx_root, "modules", "site_builder", "templates")
    websites_dir  = os.path.join(_cbx_root, "builds", "websites")
    print(f"  [SIM]   Templates source : {templates_dir}")
    print(f"  [SIM]   Projects output  : {websites_dir}")
    print("  [SIM] Simulation complete.")


def _execute():
    """Delegate to website_builder.py create_project()."""
    try:
        sys.path.insert(0, _get_root())
        from modules.site_builder.website_builder import create_project
        create_project()
    except ImportError as exc:
        print(f"  Could not load website_builder module: {exc}")


def _get_root():
    return os.environ.get(
        "CBX_ROOT",
        os.path.dirname(
            os.path.dirname(
                os.path.dirname(
                    os.path.dirname(os.path.abspath(__file__))
                )
            )
        )
    )
