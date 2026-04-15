"""
test_online_studio.py — Tests for the Website Builder & Online Studio menu
and placeholder tool modules.

Run with:
    cd tools-center && python -m pytest tests/test_online_studio.py -v
or:
    cd tools-center && python tests/test_online_studio.py
"""

import importlib
import sys
import os
import io

# Ensure tools-center is on sys.path
_TC_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _TC_ROOT not in sys.path:
    sys.path.insert(0, _TC_ROOT)


# ── Helpers ────────────────────────────────────────────────────────────────────

def _capture(fn, *args, **kwargs):
    """Run fn() and return its stdout as a string."""
    buf = io.StringIO()
    old = sys.stdout
    sys.stdout = buf
    try:
        fn(*args, **kwargs)
    finally:
        sys.stdout = old
    return buf.getvalue()


# ── Tool module tests ──────────────────────────────────────────────────────────

def test_program_editor_run_does_not_raise():
    from tools.online_studio import program_editor
    out = _capture(program_editor.run)
    assert "PROGRAM EDITOR" in out or "PLACEHOLDER" in out


def test_program_editor_simulate_does_not_raise():
    from tools.online_studio import program_editor
    out = _capture(program_editor.simulate)
    assert out  # non-empty output


def test_web_calling_texting_run_does_not_raise():
    from tools.online_studio import web_calling_texting
    out = _capture(web_calling_texting.run)
    assert "WEB CALLING" in out or "PLACEHOLDER" in out


def test_web_calling_texting_has_contact_keys():
    from tools.online_studio import web_calling_texting
    info = web_calling_texting.get_contact_info()
    assert "phone" in info
    assert "sms" in info
    assert "email" in info
    assert "map" in info


def test_website_builder_run_does_not_raise_on_eof():
    """run() should handle EOFError gracefully (non-interactive environment)."""
    import builtins
    from tools.online_studio import website_builder
    # Patch input to raise EOFError simulating non-interactive
    orig_input = builtins.input
    builtins.input = lambda *a, **kw: (_ for _ in ()).throw(EOFError())
    try:
        out = _capture(website_builder.run)
    finally:
        builtins.input = orig_input
    # Should not crash; output should contain the menu header
    assert "WEBSITE BUILDER" in out or "PLACEHOLDER" in out


def test_website_builder_list_project_types():
    from tools.online_studio import website_builder
    types = website_builder.list_project_types()
    assert len(types) >= 4
    slugs = [t[2] for t in types]
    assert "classic" in slugs
    assert "hub" in slugs
    assert "chat" in slugs
    assert "callhub" in slugs


def test_website_builder_simulate_does_not_raise():
    import builtins
    from tools.online_studio import website_builder
    orig_input = builtins.input
    builtins.input = lambda *a, **kw: (_ for _ in ()).throw(EOFError())
    try:
        out = _capture(website_builder.simulate)
    finally:
        builtins.input = orig_input
    assert out  # non-empty


# ── Menu module tests ──────────────────────────────────────────────────────────

def test_online_studio_menu_importable():
    """online_studio_menu must import without errors."""
    mod = importlib.import_module("menus.online_studio_menu")
    assert hasattr(mod, "show")


def test_online_studio_menu_build_items():
    """_build_items() must return exactly 3 entries with correct labels."""
    from menus import online_studio_menu
    items = online_studio_menu._build_items()
    assert len(items) == 3
    labels = [item[1] for item in items]
    assert any("Website Builder" in lbl for lbl in labels)
    assert any("Program Editor" in lbl for lbl in labels)
    assert any("Web Calling" in lbl for lbl in labels)


# ── main_menu integration test ─────────────────────────────────────────────────

def test_main_menu_contains_online_studio_entry():
    """main_menu.py ENTRIES must include the Online Studio entry."""
    import pathlib
    src = pathlib.Path(_TC_ROOT) / "menus" / "main_menu.py"
    text = src.read_text(encoding="utf-8")
    assert "Website Builder & Online Studio" in text
    assert "_go_online_studio" in text


# ── Registry test ──────────────────────────────────────────────────────────────

def test_registry_contains_online_studio_tools():
    """tool_registry.json must contain all three online_studio tools."""
    import json, pathlib
    reg_path = pathlib.Path(_TC_ROOT) / "core" / "tool_registry.json"
    registry = json.loads(reg_path.read_text(encoding="utf-8"))
    os_tools = [t for t in registry if t.get("group") == "online_studio"]
    ids = [t["id"] for t in os_tools]
    assert "online_studio_website_builder" in ids
    assert "online_studio_program_editor" in ids
    assert "online_studio_web_calling_texting" in ids


# ── startup preload test ───────────────────────────────────────────────────────

def test_startup_preloads_online_studio_menu():
    """startup.py must list menus.online_studio_menu in its preload list."""
    import pathlib
    src = pathlib.Path(_TC_ROOT) / "startup.py"
    text = src.read_text(encoding="utf-8")
    assert "menus.online_studio_menu" in text


# ── web_menu fallback test ─────────────────────────────────────────────────────

def test_web_menu_fallback_announces_placeholder():
    """web_menu._fallback_items() must mention placeholder status."""
    from menus import web_menu
    items = web_menu._fallback_items()
    for icon, label, fn in items:
        assert "placeholder" in label.lower() or "PLACEHOLDER" in label


# ── Entrypoint ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    tests = [v for k, v in list(globals().items()) if k.startswith("test_")]
    passed = failed = 0
    for t in tests:
        try:
            t()
            print(f"  ✓  {t.__name__}")
            passed += 1
        except Exception as exc:
            print(f"  ✗  {t.__name__}: {exc}")
            failed += 1
    print()
    print(f"  {passed} passed, {failed} failed")
    if failed:
        sys.exit(1)
