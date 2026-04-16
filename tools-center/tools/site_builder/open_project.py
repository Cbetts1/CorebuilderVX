"""
open_project.py — Open / inspect an existing website project.

Lists all projects stored in builds/websites/index.json and
displays the selected project's metadata and file listing.
"""

import os
import sys


def run():
    """Real behaviour: open and inspect an existing website project."""
    print("  [Website Builder] Open Project")
    _execute()


def simulate():
    """Safe dry-run: list projects without modifying anything."""
    print("  [SIM] [Website Builder] Simulating open project (no real changes)...")
    try:
        sys.path.insert(0, _get_root())
        from modules.site_builder.website_builder import list_projects
        list_projects()
    except ImportError as exc:
        print(f"  [SIM] Could not load website_builder module: {exc}")
    print("  [SIM] Simulation complete.")


def _execute():
    """Delegate to website_builder.py open_project()."""
    try:
        sys.path.insert(0, _get_root())
        from modules.site_builder.website_builder import open_project
        open_project()
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
