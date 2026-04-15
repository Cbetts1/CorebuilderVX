"""
main.py — Tools Center entry point.

Run with:
    python main.py
    python main.py --simulate
    python main.py --no-colour
    python main.py --debug
"""

import sys
import os

# Ensure tools-center is importable
_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)


def _parse_args():
    args = sys.argv[1:]
    if "--help" in args or "-h" in args:
        print(__doc__)
        sys.exit(0)
    if "--simulate" in args:
        os.environ["TC_SIMULATE"] = "1"
    if "--no-colour" in args or "--no-color" in args:
        os.environ["TC_NO_COLOUR"] = "1"
    if "--debug" in args:
        os.environ["TC_DEBUG"] = "1"


def _apply_env_overrides():
    """Override settings from environment variables before startup."""
    from engines import settings_engine
    settings_engine.load()
    if os.environ.get("TC_SIMULATE") == "1":
        settings_engine.set("simulation_mode", True)
    if os.environ.get("TC_NO_COLOUR") == "1":
        settings_engine.set("colour_enabled", False)
    if os.environ.get("TC_DEBUG") == "1":
        settings_engine.set("debug_mode", True)


if __name__ == "__main__":
    _parse_args()
    _apply_env_overrides()

    from startup import run
    try:
        run()
    except KeyboardInterrupt:
        print("\n\n  Tools Center exited.  Goodbye! ⏻\n")
        sys.exit(0)
