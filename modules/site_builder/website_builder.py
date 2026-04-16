#!/usr/bin/env python3
"""
website_builder.py — CoreBuilderVX Website Builder & Online Studio

Main entry point for the site builder module. Can be invoked:
  - Directly:  python3 modules/site_builder/website_builder.py
  - Via shell: source modules/site_builder/website_builder.py (not applicable)
  - Via API:   POST /api/v1/run { "command": "site_create" | "site_open" | "site_preview" }

Modes:
  create   — Create a new website project from a template
  open     — List and open an existing website project
  preview  — Start a local HTTP preview server (port 8000)
  list     — List all website projects
"""

import os
import sys
import json
import shutil
import subprocess
from datetime import datetime

CBX_ROOT = os.environ.get(
    "CBX_ROOT",
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

TEMPLATES_DIR = os.path.join(CBX_ROOT, "modules", "site_builder", "templates")
WEBSITES_DIR  = os.path.join(CBX_ROOT, "builds", "websites")
INDEX_FILE    = os.path.join(WEBSITES_DIR, "index.json")
PREVIEW_PORT  = int(os.environ.get("CBX_PREVIEW_PORT", "8000"))

TEMPLATE_NAMES = [
    "classic",
    "online_hub",
    "chat_page",
    "call_hub",
    "programming_studio",
    "lessons",
]


# ── Helpers ────────────────────────────────────────────────────────────────────

def _ensure_dirs():
    os.makedirs(WEBSITES_DIR, exist_ok=True)
    if not os.path.exists(INDEX_FILE):
        _save_index([])


def _load_index():
    if os.path.exists(INDEX_FILE):
        with open(INDEX_FILE, encoding="utf-8") as f:
            return json.load(f)
    return []


def _save_index(projects):
    os.makedirs(WEBSITES_DIR, exist_ok=True)
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(projects, f, indent=2)


def _add_to_index(name, template, path):
    projects = _load_index()
    projects.append({
        "name":       name,
        "template":   template,
        "path":       path,
        "created_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "status":     "active",
    })
    _save_index(projects)


# ── Actions ────────────────────────────────────────────────────────────────────

def create_project(name=None, template=None):
    """Create a new website project from a template."""
    _ensure_dirs()

    if not name:
        name = input("  Project name: ").strip()
    if not name:
        print("  Error: project name required.")
        return None

    safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in name)

    if not template:
        print("\n  Available templates:")
        for i, t in enumerate(TEMPLATE_NAMES, 1):
            print(f"    {i}. {t}")
        choice = input("  Choose template [1]: ").strip() or "1"
        try:
            template = TEMPLATE_NAMES[int(choice) - 1]
        except (ValueError, IndexError):
            template = TEMPLATE_NAMES[0]

    src = os.path.join(TEMPLATES_DIR, template)
    dst = os.path.join(WEBSITES_DIR, safe_name)

    if os.path.exists(dst):
        print(f"  Error: project '{safe_name}' already exists at {dst}")
        return None

    if not os.path.isdir(src):
        print(f"  Error: template '{template}' not found at {src}")
        return None

    shutil.copytree(src, dst)

    # Write per-project manifest
    manifest = {
        "name":       safe_name,
        "template":   template,
        "created_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "status":     "active",
    }
    with open(os.path.join(dst, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    _add_to_index(safe_name, template, dst)

    print(f"\n  ✓ Project '{safe_name}' created at {dst}")
    print(f"    Template : {template}")
    print(f"    Preview  : python3 {__file__} preview {safe_name}\n")
    return dst


def list_projects():
    """List all website projects."""
    _ensure_dirs()
    projects = _load_index()
    if not projects:
        print("  No website projects yet. Run: create")
        return projects
    print(f"\n  {'#':<4} {'Name':<24} {'Template':<22} {'Created':<22} Status")
    print("  " + "─" * 78)
    for i, p in enumerate(projects, 1):
        print(f"  {i:<4} {p.get('name','?'):<24} {p.get('template','?'):<22} "
              f"{p.get('created_at','?')[:16]:<22} {p.get('status','?')}")
    print()
    return projects


def open_project(name=None):
    """Open (inspect) an existing project."""
    _ensure_dirs()
    projects = _load_index()
    if not projects:
        print("  No projects found. Create one first.")
        return

    if not name:
        list_projects()
        choice = input("  Select project #: ").strip()
        try:
            project = projects[int(choice) - 1]
        except (ValueError, IndexError):
            print("  Invalid selection.")
            return
    else:
        project = next((p for p in projects if p["name"] == name), None)
        if not project:
            print(f"  Project '{name}' not found.")
            return

    path = project.get("path", os.path.join(WEBSITES_DIR, project["name"]))
    print(f"\n  Project  : {project['name']}")
    print(f"  Template : {project.get('template', '?')}")
    print(f"  Path     : {path}")
    print(f"  Created  : {project.get('created_at', '?')}")

    if os.path.isdir(path):
        files = os.listdir(path)
        print(f"  Files    : {', '.join(files)}")
    else:
        print("  Warning  : project directory not found on disk.")
    print()
    return project


def start_preview(name=None, port=None):
    """Start a local HTTP preview server for a project."""
    _ensure_dirs()
    port = port or PREVIEW_PORT

    if name:
        project_dir = os.path.join(WEBSITES_DIR, name)
    else:
        projects = _load_index()
        if not projects:
            print("  No projects found. Create one first.")
            return
        list_projects()
        choice = input("  Select project # to preview: ").strip()
        try:
            project = projects[int(choice) - 1]
            project_dir = project.get("path", os.path.join(WEBSITES_DIR, project["name"]))
        except (ValueError, IndexError):
            print("  Invalid selection.")
            return

    if not os.path.isdir(project_dir):
        print(f"  Error: project directory not found: {project_dir}")
        return

    print(f"\n  Starting preview server for: {project_dir}")
    print(f"  URL: http://127.0.0.1:{port}/index.html")
    print("  Press Ctrl+C to stop.\n")

    try:
        subprocess.run(
            [sys.executable, "-m", "http.server", str(port), "--bind", "127.0.0.1"],
            cwd=project_dir,
        )
    except KeyboardInterrupt:
        print("\n  Preview server stopped.")


# ── CLI ────────────────────────────────────────────────────────────────────────

def interactive_menu():
    """Interactive CLI menu for the website builder."""
    _ensure_dirs()
    while True:
        print("\n  ╔══════════════════════════════════╗")
        print("  ║  Website Builder & Online Studio ║")
        print("  ╚══════════════════════════════════╝")
        print("   1. Create new project")
        print("   2. Open / inspect project")
        print("   3. List all projects")
        print("   4. Start preview server")
        print("   0. Back")
        print()
        choice = input("  Select › ").strip()
        if choice == "1":
            create_project()
        elif choice == "2":
            open_project()
        elif choice == "3":
            list_projects()
        elif choice == "4":
            start_preview()
        elif choice in ("0", "q", "quit", "exit"):
            break
        else:
            print("  Invalid selection.")


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        interactive_menu()
    elif args[0] == "create":
        create_project(name=args[1] if len(args) > 1 else None,
                       template=args[2] if len(args) > 2 else None)
    elif args[0] == "open":
        open_project(name=args[1] if len(args) > 1 else None)
    elif args[0] == "list":
        list_projects()
    elif args[0] == "preview":
        start_preview(name=args[1] if len(args) > 1 else None,
                      port=int(args[2]) if len(args) > 2 else None)
    else:
        print(f"  Unknown command: {args[0]}")
        print("  Usage: website_builder.py [create|open|list|preview] [name] [template]")
        sys.exit(1)
