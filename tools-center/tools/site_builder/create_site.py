"""
create_site.py — Website Builder: Create New Site tool.

Interactively prompts for project details and creates a new site project.
"""

import os
import sys


def run():
    """Real behaviour: prompt for details and create a new site project."""
    print("  ─── Website Builder — New Site ───────────────────────────────")
    print()

    name = input("  Site name (slug, e.g. my-portfolio): ").strip()
    if not name:
        print("  Name is required. Cancelled.")
        return

    try:
        from modules.site_builder.website_builder import (
            AVAILABLE_TEMPLATES, AVAILABLE_MODES, WebsiteBuilder,
        )
    except ImportError:
        _add_cbx_root()
        from modules.site_builder.website_builder import (
            AVAILABLE_TEMPLATES, AVAILABLE_MODES, WebsiteBuilder,
        )

    tmpl_list = ", ".join(AVAILABLE_TEMPLATES)
    template  = input(f"  Template [{tmpl_list}] (default: landing): ").strip() or "landing"
    title     = input(f"  Site title (default: {name}): ").strip()
    desc      = input("  Description (optional): ").strip()
    mode      = input("  Mode [template/code] (default: template): ").strip() or "template"

    try:
        builder  = WebsiteBuilder()
        manifest = builder.create_project(
            name,
            template=template,
            title=title,
            description=desc,
            mode=mode,
        )
        print()
        print(f"  ✓ Site '{manifest['name']}' created.")
        print(f"    Template : {manifest['template']}")
        print(f"    Mode     : {manifest['mode']}")
        print(f"    Title    : {manifest['title']}")
        print(f"    Pages    : {manifest['pages']}")
        print()
        print("  Use 'Build Site' to generate the static output.")
    except (ValueError, FileExistsError) as exc:
        print(f"  ✗ {exc}")


def simulate():
    """Dry-run: describe what would be created without touching the filesystem."""
    print("  [SIM] Create New Site — would prompt for name, template, title, description.")
    print("  [SIM] Would create: data/sites/<name>/pages/index.html + manifest.json")
    print("  [SIM] No changes made.")


def _add_cbx_root():
    """Add the repo root to sys.path so modules.site_builder is importable."""
    here     = os.path.dirname(os.path.abspath(__file__))
    cbx_root = os.path.dirname(os.path.dirname(os.path.dirname(here)))
    if cbx_root not in sys.path:
        sys.path.insert(0, cbx_root)
