"""
preview_server.py — Start a local HTTP preview server for a website project.

Serves the selected project directory on port 8000 (CBX_PREVIEW_PORT)
using Python's built-in http.server — no extra dependencies required.
"""

import os
import sys


def run():
    """Real behaviour: start the preview server for a selected project."""
    print("  [Website Builder] Preview Server")
    _execute()


def simulate():
    """Safe dry-run: show what would be served without starting a server."""
    print("  [SIM] [Website Builder] Simulating preview server (no real changes)...")
    port = int(os.environ.get("CBX_PREVIEW_PORT", "8000"))
    websites_dir = os.path.join(_get_root(), "builds", "websites")
    print(f"  [SIM]   Would serve from : {websites_dir}/<project>")
    print(f"  [SIM]   Preview URL      : http://127.0.0.1:{port}/index.html")
    print("  [SIM] Simulation complete.")


def _execute():
    """Delegate to website_builder.py start_preview()."""
    try:
        sys.path.insert(0, _get_root())
        from modules.site_builder.website_builder import start_preview
        start_preview()
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
