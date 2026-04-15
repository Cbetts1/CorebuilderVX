"""
benchmark_cpu.py — Benchmark CPU tool.

Runs a quick CPU benchmark.
"""


def run():
    """Real behaviour: Runs a quick CPU benchmark."""
    print("  [Benchmark CPU] Running...")
    _execute()
    print("  [Benchmark CPU] Done.")

def simulate():
    """Safe dry-run behaviour: Runs a quick CPU benchmark."""
    print("  [SIM] [Benchmark CPU] Simulating (no real changes)...")
    print("  [SIM] [Benchmark CPU] Simulation complete.")


def _execute():
    """Core implementation placeholder for Benchmark CPU."""
    # TODO: implement Benchmark CPU
    pass
