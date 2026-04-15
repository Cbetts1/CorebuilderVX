"""
stop_vm.py — Stop VM tool.

Stops a running virtual machine.
"""


def run():
    """Real behaviour: Stops a running virtual machine."""
    print("  [Stop VM] Running...")
    _execute()
    print("  [Stop VM] Done.")

def simulate():
    """Safe dry-run behaviour: Stops a running virtual machine."""
    print("  [SIM] [Stop VM] Simulating (no real changes)...")
    print("  [SIM] [Stop VM] Simulation complete.")


def _execute():
    """Core implementation placeholder for Stop VM."""
    # TODO: implement Stop VM
    pass
