"""
web_calling_texting.py — Web Calling & Texting placeholder (Online Studio).

[PLACEHOLDER] Quick-action call/text/email hub.
Works fully offline — uses tel:, sms:, and mailto: links.
"""


_CONTACT_INFO = {
    "phone":  "555-000-0000",
    "sms":    "555-000-0000",
    "email":  "contact@example.local",
    "map":    "123 Main St, Anytown, USA",
}


def run():
    """Display the Web Calling & Texting placeholder hub."""
    print()
    print("  ╔══════════════════════════════════════════════════════╗")
    print("  ║    📞  WEB CALLING & TEXTING  [PLACEHOLDER]         ║")
    print("  ╚══════════════════════════════════════════════════════╝")
    print()
    print("  Quick-action contact hub (offline-first):")
    print()
    print(f"  📞  Call now   → tel:{_CONTACT_INFO['phone']}")
    print(f"  💬  Text now   → sms:{_CONTACT_INFO['sms']}")
    print(f"  ✉️   Email now  → mailto:{_CONTACT_INFO['email']}")
    print(f"  🗺️   Location   → {_CONTACT_INFO['map']}")
    print()
    print("  ─────────────────────────────────────────────────────")
    print("  Copy contact info:")
    print(f"    Phone : {_CONTACT_INFO['phone']}")
    print(f"    SMS   : {_CONTACT_INFO['sms']}")
    print(f"    Email : {_CONTACT_INFO['email']}")
    print(f"    Map   : {_CONTACT_INFO['map']}")
    print()
    print("  Status: PLACEHOLDER — live calling/texting not yet wired.")
    print("          Replace contact details in web_calling_texting.py.")
    print()


def simulate():
    """Simulation mode: same output as run() — read-only stub."""
    run()


def get_contact_info() -> dict:
    """Return the contact info dict (used by tests and other tools)."""
    return dict(_CONTACT_INFO)
