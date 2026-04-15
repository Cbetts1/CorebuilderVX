"""
build_static_site.py — Build Static Site tool.

Builds a static HTML site.
"""


def run():
    """Real behaviour: Builds a static HTML site."""
    print("  [Build Static Site] Running...")
    _execute()
    print("  [Build Static Site] Done.")

def simulate():
    """Safe dry-run behaviour: Builds a static HTML site."""
    print("  [SIM] [Build Static Site] Simulating (no real changes)...")
    print("  [SIM] [Build Static Site] Simulation complete.")


def _execute():
    """Core implementation placeholder for Build Static Site."""
    # TODO: implement Build Static Site
    pass
