"""
website_builder.py — Website Builder placeholder (Online Studio).

[PLACEHOLDER] Multi-mode offline website builder.
Replaces the legacy modules/site_builder/website_builder.py entry point.

Planned project types:
  1. Classic Website  (simple one-page or expanded multi-page)
  2. Online Hub       (AOL-style: rooms, activity, shortcuts, call hub, studio, lessons)
  3. Chat / Messaging Page
  4. Call / Contact Hub
  5. Programming Studio page
  6. Lessons / Learn to Program

All output goes to builds/websites/<user-defined-slug>/ (offline-first).
"""

import os

# Root of the Tools Center
_TC_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_BUILDS_DIR = os.path.join(os.path.dirname(_TC_ROOT), "builds", "websites")

_PROJECT_TYPES = [
    ("🌐", "Classic Website",          "classic"),
    ("🏠", "Online Hub (AOL-style)",   "hub"),
    ("💬", "Chat / Messaging Page",    "chat"),
    ("📞", "Call / Contact Hub",       "callhub"),
    ("📝", "Programming Studio Page",  "studio"),
    ("📘", "Lessons / Learn to Program","lessons"),
]


def run():
    """Interactive website builder placeholder."""
    print()
    print("  ╔══════════════════════════════════════════════════════╗")
    print("  ║        🌐  WEBSITE BUILDER  [PLACEHOLDER]           ║")
    print("  ║             Online Studio — Offline-first           ║")
    print("  ╚══════════════════════════════════════════════════════╝")
    print()
    print("  Available project types:")
    print()
    for i, (icon, label, _) in enumerate(_PROJECT_TYPES, start=1):
        print(f"    {i:>2}. {icon}  {label}")
    print()
    print("   0. ← Back")
    print()

    try:
        choice = input("  Select project type › ").strip()
    except (EOFError, KeyboardInterrupt):
        print()
        return

    if not choice.isdigit() or choice == "0":
        return

    idx = int(choice) - 1
    if not (0 <= idx < len(_PROJECT_TYPES)):
        print("  Invalid selection.")
        return

    icon, label, slug = _PROJECT_TYPES[idx]
    print(f"\n  → Selected: {icon}  {label}")
    print()
    print("  Status: PLACEHOLDER — project scaffolding not yet active.")
    print(f"  (Future output will be created in: {_BUILDS_DIR}/<your-slug>/)")
    print()
    print("  When implemented this step will:")
    print("    • Ask for a project name (slugified)")
    print("    • Ask: sample content OR empty skeleton")
    print("    • Edit metadata (title, description, author, version, tags)")
    print("    • Generate the folder structure and starter HTML/CSS")
    print("    • Prompt before starting a local preview server")
    print("    • Log the project in a local JSON index")
    print()


def simulate():
    """Simulation mode: same as run() — no file system changes."""
    run()


def list_project_types() -> list:
    """Return available project type definitions (used by tests)."""
    return list(_PROJECT_TYPES)
