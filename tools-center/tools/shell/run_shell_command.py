"""
run_shell_command.py — Run Shell Command tool.

Runs a one-off shell command.
"""


def run():
    """Real behaviour: Runs a one-off shell command."""
    print("  [Run Shell Command] Running...")
    _execute()
    print("  [Run Shell Command] Done.")

def simulate():
    """Safe dry-run behaviour: Runs a one-off shell command."""
    print("  [SIM] [Run Shell Command] Simulating (no real changes)...")
    print("  [SIM] [Run Shell Command] Simulation complete.")


def _execute():
    """Core implementation placeholder for Run Shell Command."""
    # TODO: implement Run Shell Command
    pass
