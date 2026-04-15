"""
run_code.py — Run Code tool.

Executes source code in a subprocess.
"""


def run():
    """Real behaviour: Executes source code in a subprocess."""
    print("  [Run Code] Running...")
    _execute()
    print("  [Run Code] Done.")

def simulate():
    """Safe dry-run behaviour: Executes source code in a subprocess."""
    print("  [SIM] [Run Code] Simulating (no real changes)...")
    print("  [SIM] [Run Code] Simulation complete.")


def _execute():
    """Core implementation placeholder for Run Code."""
    # TODO: implement Run Code
    pass
