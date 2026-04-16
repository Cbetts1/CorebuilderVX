"""
template_loader.py — List and inspect available website templates.

Reads the templates directory at modules/site_builder/templates/ and
displays a formatted list of template names and their index.html sizes.
"""

import os


def run():
    """Real behaviour: list all available website templates."""
    print("  [Website Builder] Template Loader")
    _execute()


def simulate():
    """Simulation not supported — falls back to run() (read-only operation)."""
    run()


def _execute():
    """List templates from the templates directory."""
    templates_dir = os.path.join(_get_root(), "modules", "site_builder", "templates")
    if not os.path.isdir(templates_dir):
        print(f"  Templates directory not found: {templates_dir}")
        return

    entries = sorted(
        name for name in os.listdir(templates_dir)
        if os.path.isdir(os.path.join(templates_dir, name))
    )
    if not entries:
        print("  No templates found.")
        return

    print(f"\n  {'#':<4} {'Template':<28} {'Files'}")
    print("  " + "─" * 48)
    for i, name in enumerate(entries, 1):
        tdir  = os.path.join(templates_dir, name)
        files = os.listdir(tdir)
        print(f"  {i:<4} {name:<28} {', '.join(files)}")
    print()


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
