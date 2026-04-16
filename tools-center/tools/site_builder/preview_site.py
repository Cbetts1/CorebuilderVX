"""
preview_site.py — Website Builder: Preview Site tool.

Builds the selected project then launches a local HTTP server so the site
can be viewed in a browser at http://127.0.0.1:<port>/index.html.
"""

import os
import sys
import subprocess


def run():
    """Real behaviour: build a project and start a local HTTP preview server."""
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
        print(f"    {i:>2}. {n}")
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

    port_in = input("  Preview port [8767]: ").strip()
    try:
        port = int(port_in) if port_in else 8767
        if not (1 <= port <= 65535):
            raise ValueError
    except ValueError:
        port = 8767

    print(f"\n  Building '{name}'...")
    try:
        build_dir = builder.build_project(name)
    except FileNotFoundError as exc:
        print(f"  ✗ {exc}")
        return
    print("  ✓ Build complete.")
    print()
    print(f"  Starting preview server on port {port}…")
    print(f"  Open in browser: http://127.0.0.1:{port}/index.html")
    print("  Press Ctrl+C to stop.")
    print()

    try:
        subprocess.run(
            [sys.executable, "-m", "http.server", str(port), "--bind", "127.0.0.1"],
            cwd=build_dir,
        )
    except KeyboardInterrupt:
        print("\n  Preview server stopped.")


def simulate():
    """Dry-run: describe the preview action without starting any server."""
    print("  [SIM] Preview Site — would build the selected project into _build/.")
    print("  [SIM] Would start: python3 -m http.server <port> in _build/")
    print("  [SIM] No server started.")


def _add_cbx_root():
    here     = os.path.dirname(os.path.abspath(__file__))
    cbx_root = os.path.dirname(os.path.dirname(os.path.dirname(here)))
    if cbx_root not in sys.path:
        sys.path.insert(0, cbx_root)
