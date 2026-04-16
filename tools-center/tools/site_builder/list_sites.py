"""
list_sites.py — Website Builder: List Sites tool.

Displays all existing site projects with status information.
"""

import os
import sys


def run():
    """Real behaviour: list all site projects in a formatted table."""
    try:
        from modules.site_builder.website_builder import WebsiteBuilder
    except ImportError:
        _add_cbx_root()
        from modules.site_builder.website_builder import WebsiteBuilder

    builder  = WebsiteBuilder()
    projects = builder.list_projects()

    print()
    if not projects:
        print("  No site projects found.")
        print("  Use 'Create New Site' to get started.")
        return

    print(f"  {'Name':<22} {'Template':<12} {'Mode':<10} {'Last Build':<22} {'Title'}")
    print(f"  {'─'*22} {'─'*12} {'─'*10} {'─'*22} {'─'*20}")
    for p in projects:
        lb = p.get("last_build") or "never"
        if lb != "never":
            lb = lb[:16]
        title = p.get("title", "")[:20]
        print(
            f"  {p['name']:<22} {p.get('template','?'):<12} "
            f"{p.get('mode','?'):<10} {lb:<22} {title}"
        )
    print()
    print(f"  {len(projects)} project(s).")


def simulate():
    """Dry-run: would list site projects (read-only, safe to run)."""
    run()


def _add_cbx_root():
    here     = os.path.dirname(os.path.abspath(__file__))
    cbx_root = os.path.dirname(os.path.dirname(os.path.dirname(here)))
    if cbx_root not in sys.path:
        sys.path.insert(0, cbx_root)
