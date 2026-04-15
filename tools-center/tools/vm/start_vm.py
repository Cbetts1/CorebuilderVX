"""
start_vm.py — Start VM tool.

Starts a lightweight virtual machine.
"""


def run():
    """Real behaviour: Starts a lightweight virtual machine."""
    print("  [Start VM] Running...")
    _execute()
    print("  [Start VM] Done.")

def simulate():
    """Safe dry-run behaviour: Starts a lightweight virtual machine."""
    print("  [SIM] [Start VM] Simulating (no real changes)...")
    print("  [SIM] [Start VM] Simulation complete.")


def _execute():
    """Core implementation placeholder for Start VM."""
    # TODO: implement Start VM
    pass
