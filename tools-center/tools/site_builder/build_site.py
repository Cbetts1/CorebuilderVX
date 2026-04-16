"""
build_site.py — Website Builder: Build Site tool.

Lists projects, prompts the user to pick one, then generates the static output.
"""

import os
import sys


def run():
    """Real behaviour: select a project and generate its static HTML output."""
    try:
        from modules.site_builder.website_builder import WebsiteBuilder
    except ImportError:
        _add_cbx_root()
        from modules.site_builder.website_builder import WebsiteBuilder

    builder  = WebsiteBuilder()
    projects = builder.list_projects()

    print()
    if not projects:
        print("  No site projects found. Use 'Create New Site' first.")
        return

    print("  Available sites:")
    names = [p["name"] for p in projects]
    for i, n in enumerate(names, 1):
        tmpl = projects[i - 1].get("template", "?")
        lb   = projects[i - 1].get("last_build") or "never"
        if lb != "never":
            lb = lb[:16]
        print(f"    {i:>2}. {n:<22} [{tmpl}]  last built: {lb}")
    print()

    choice = input("  Select site number (or type name): ").strip()
    if choice.isdigit():
        idx = int(choice) - 1
        if 0 <= idx < len(names):
            name = names[idx]
        else:
            print("  Invalid selection.")
            return
    else:
        name = choice

    if not name:
        print("  Cancelled.")
        return

    print(f"\n  Building '{name}'...")
    try:
        build_dir = builder.build_project(name)
        print(f"  ✓ Build complete.")
        print(f"    Output: {build_dir}")
        print()
        print("  Use 'Preview Site' to serve it or open index.html directly.")
    except FileNotFoundError as exc:
        print(f"  ✗ {exc}")


def simulate():
    """Dry-run: describe what build_project would do, without writing files."""
    print("  [SIM] Build Site — would select a project and copy pages/ to _build/.")
    print("  [SIM] Would update manifest.json with last_build timestamp.")
    print("  [SIM] No changes made.")


def _add_cbx_root():
    here     = os.path.dirname(os.path.abspath(__file__))
    cbx_root = os.path.dirname(os.path.dirname(os.path.dirname(here)))
    if cbx_root not in sys.path:
        sys.path.insert(0, cbx_root)
