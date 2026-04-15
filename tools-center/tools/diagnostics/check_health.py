"""
check_health.py — Check System Health tool.

Reports CPU, RAM, and disk health.
"""


def run():
    """Real behaviour: Reports CPU, RAM, and disk health."""
    print("  [Check System Health] Running...")
    _execute()
    print("  [Check System Health] Done.")

def simulate():
    """Simulation not supported for this tool — falls back to run()."""
    run()


def _execute():
    """Core implementation placeholder for Check System Health."""
    # TODO: implement Check System Health
    pass
