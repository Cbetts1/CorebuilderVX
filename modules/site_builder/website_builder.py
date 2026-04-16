#!/usr/bin/env python3
"""
website_builder.py — CoreBuilderVX Website Builder & Online Studio (core module).

Manages site projects stored under CBX_DATA_DIR/sites/.  Each project has a
manifest, source pages, assets, and a generated _build/ directory.

Importable class
----------------
  from modules.site_builder.website_builder import WebsiteBuilder

  builder = WebsiteBuilder()
  builder.create_project("my-site", template="landing", title="My Site")
  builder.build_project("my-site")
  builder.list_projects()

CLI usage (non-interactive)
----------------------------
  python3 website_builder.py list
  python3 website_builder.py create --name NAME [--template TMPL] [--title TITLE] [--desc DESC] [--mode MODE]
  python3 website_builder.py build  --name NAME
  python3 website_builder.py get    --name NAME
  python3 website_builder.py delete --name NAME

Modes
-----
  template  — starter page generated from a built-in template (default)
  code      — raw HTML; edit pages/index.html directly with your editor

Templates
---------
  blank      — empty HTML skeleton
  landing    — single-page hero + sections landing page
  portfolio  — project/work showcase grid
  blog       — blog index with post stubs
"""

import os
import re
import sys
import json
import shutil
import argparse
from datetime import datetime, timezone
from string import Template
from typing import Dict, List, Optional

# ── Built-in CSS shared across all templates ──────────────────────────────────

_CSS_COMMON = """\
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: 'Segoe UI', Arial, sans-serif; background: #0d1117;
       color: #e6edf3; line-height: 1.6; }
a { color: #00d4aa; text-decoration: none; }
a:hover { text-decoration: underline; }
header { background: #161b22; border-bottom: 1px solid #30363d;
         padding: 0.75rem 2rem; display: flex; align-items: center;
         justify-content: space-between; }
header h1 { color: #00d4aa; font-size: 1.3rem; }
nav a { margin-left: 1.5rem; color: #8b949e; }
nav a:hover { color: #00d4aa; }
main { max-width: 960px; margin: 0 auto; padding: 2rem 1rem; }
footer { text-align: center; padding: 2rem; color: #8b949e;
         border-top: 1px solid #30363d; margin-top: 2rem; font-size: 0.85rem; }"""

# ── Built-in HTML templates ───────────────────────────────────────────────────

_TEMPLATES: Dict[str, Template] = {
    "blank": Template("""\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>$title</title>
  <style>
$css
  </style>
</head>
<body>
  <header>
    <h1>$title</h1>
    <nav></nav>
  </header>
  <main>
    <p>$description</p>
  </main>
  <footer>Built with CoreBuilderVX</footer>
</body>
</html>
"""),

    "landing": Template("""\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>$title</title>
  <style>
$css
.hero { text-align: center; padding: 5rem 1rem;
        background: linear-gradient(135deg, #0d1117 0%, #161b22 100%); }
.hero h2 { font-size: 2.5rem; color: #00d4aa; margin-bottom: 1rem; }
.hero p  { font-size: 1.1rem; color: #8b949e; max-width: 580px;
           margin: 0 auto 2rem; }
.btn { display: inline-block; background: #00d4aa; color: #0d1117;
       padding: 0.75rem 2rem; border-radius: 6px; font-weight: bold; }
.btn:hover { background: #00b894; text-decoration: none; }
.features { display: grid;
            grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
            gap: 1.5rem; margin-top: 3rem; }
.feature { background: #161b22; border: 1px solid #30363d;
           border-radius: 8px; padding: 1.5rem; }
.feature h3 { color: #58a6ff; margin-bottom: 0.5rem; }
.feature p  { color: #8b949e; font-size: 0.9rem; }
  </style>
</head>
<body>
  <header>
    <h1>$title</h1>
    <nav>
      <a href="#features">Features</a>
      <a href="#about">About</a>
      <a href="#contact">Contact</a>
    </nav>
  </header>
  <section class="hero">
    <h2>$title</h2>
    <p>$description</p>
    <a class="btn" href="#features">Get Started</a>
  </section>
  <main>
    <section id="features" class="features">
      <div class="feature">
        <h3>Feature One</h3>
        <p>Describe your first feature here.</p>
      </div>
      <div class="feature">
        <h3>Feature Two</h3>
        <p>Describe your second feature here.</p>
      </div>
      <div class="feature">
        <h3>Feature Three</h3>
        <p>Describe your third feature here.</p>
      </div>
    </section>
    <section id="about" style="margin-top:3rem">
      <h2>About</h2>
      <p>Tell your story here.</p>
    </section>
    <section id="contact" style="margin-top:2rem">
      <h2>Contact</h2>
      <p>Add contact details or a form here.</p>
    </section>
  </main>
  <footer>$title &mdash; Built with CoreBuilderVX</footer>
</body>
</html>
"""),

    "portfolio": Template("""\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>$title</title>
  <style>
$css
.intro { padding: 3rem 0 2rem; }
.intro h2 { font-size: 2rem; color: #00d4aa; }
.intro p  { color: #8b949e; margin-top: 0.5rem; }
.projects { display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 1.5rem; margin-top: 2rem; }
.project-card { background: #161b22; border: 1px solid #30363d;
                border-radius: 8px; overflow: hidden;
                transition: border-color 0.2s; }
.project-card:hover { border-color: #00d4aa; }
.project-card .thumb { height: 140px; background: #21262d;
                       display: flex; align-items: center;
                       justify-content: center; font-size: 3rem; }
.project-card .info { padding: 1rem; }
.project-card h3 { color: #58a6ff; margin-bottom: 0.4rem; }
.project-card p  { color: #8b949e; font-size: 0.85rem; }
.project-card .tags { margin-top: 0.75rem; display: flex;
                      gap: 0.4rem; flex-wrap: wrap; }
.tag { background: #21262d; color: #8b949e; font-size: 0.75rem;
       padding: 2px 8px; border-radius: 12px; }
  </style>
</head>
<body>
  <header>
    <h1>$title</h1>
    <nav>
      <a href="#projects">Projects</a>
      <a href="#about">About</a>
    </nav>
  </header>
  <main>
    <section class="intro">
      <h2>$title</h2>
      <p>$description</p>
    </section>
    <section id="projects" class="projects">
      <div class="project-card">
        <div class="thumb">&#x1F680;</div>
        <div class="info">
          <h3>Project Alpha</h3>
          <p>A brief description of this project and what it achieves.</p>
          <div class="tags">
            <span class="tag">Python</span><span class="tag">API</span>
          </div>
        </div>
      </div>
      <div class="project-card">
        <div class="thumb">&#x1F6E0;</div>
        <div class="info">
          <h3>Project Beta</h3>
          <p>Another project with a short description of its purpose.</p>
          <div class="tags">
            <span class="tag">Shell</span><span class="tag">DevOps</span>
          </div>
        </div>
      </div>
      <div class="project-card">
        <div class="thumb">&#x1F310;</div>
        <div class="info">
          <h3>Project Gamma</h3>
          <p>A web-focused project showcasing your skills.</p>
          <div class="tags">
            <span class="tag">HTML</span><span class="tag">CSS</span>
          </div>
        </div>
      </div>
    </section>
    <section id="about" style="margin-top:3rem">
      <h2>About Me</h2>
      <p>Write a short bio here.</p>
    </section>
  </main>
  <footer>$title &mdash; Built with CoreBuilderVX</footer>
</body>
</html>
"""),

    "blog": Template("""\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>$title</title>
  <style>
$css
.intro { padding: 2.5rem 0 1.5rem; }
.intro h2 { font-size: 1.8rem; color: #00d4aa; }
.intro p  { color: #8b949e; margin-top: 0.5rem; }
.posts { margin-top: 1.5rem; display: flex; flex-direction: column;
         gap: 1.25rem; }
.post-card { background: #161b22; border: 1px solid #30363d;
             border-radius: 8px; padding: 1.25rem;
             display: flex; gap: 1rem; align-items: flex-start; }
.post-card:hover { border-color: #00d4aa; }
.post-meta { min-width: 90px; color: #8b949e; font-size: 0.8rem;
             padding-top: 0.25rem; }
.post-body h3 { color: #58a6ff; margin-bottom: 0.3rem; }
.post-body h3 a { color: #58a6ff; }
.post-body p  { color: #8b949e; font-size: 0.9rem; }
.post-body .tags { margin-top: 0.6rem; display: flex; gap: 0.4rem; }
.tag { background: #21262d; color: #8b949e; font-size: 0.75rem;
       padding: 2px 8px; border-radius: 12px; }
  </style>
</head>
<body>
  <header>
    <h1>$title</h1>
    <nav>
      <a href="#posts">Posts</a>
      <a href="#about">About</a>
    </nav>
  </header>
  <main>
    <section class="intro">
      <h2>$title</h2>
      <p>$description</p>
    </section>
    <section id="posts" class="posts">
      <article class="post-card">
        <div class="post-meta">2024-01-15</div>
        <div class="post-body">
          <h3><a href="#">Getting Started</a></h3>
          <p>Write the introduction to your first post here.</p>
          <div class="tags"><span class="tag">intro</span></div>
        </div>
      </article>
      <article class="post-card">
        <div class="post-meta">2024-02-01</div>
        <div class="post-body">
          <h3><a href="#">Second Post</a></h3>
          <p>Write a summary for your second post here.</p>
          <div class="tags"><span class="tag">update</span></div>
        </div>
      </article>
    </section>
    <section id="about" style="margin-top:3rem">
      <h2>About</h2>
      <p>A little about you or this blog.</p>
    </section>
  </main>
  <footer>$title &mdash; Built with CoreBuilderVX</footer>
</body>
</html>
"""),
}

AVAILABLE_TEMPLATES: List[str] = list(_TEMPLATES.keys())
AVAILABLE_MODES: List[str] = ["template", "code"]


# ── WebsiteBuilder class ───────────────────────────────────────────────────────

class WebsiteBuilder:
    """
    Core website builder — manages site projects end-to-end.

    Project layout under sites_dir/<name>/:
      manifest.json   — project metadata
      pages/          — source HTML pages (edited directly in 'code' mode)
      assets/         — static assets (CSS overrides, images, JS)
      _build/         — generated static output ready to serve
    """

    def __init__(self, data_dir: Optional[str] = None):
        if data_dir is None:
            cbx_root = os.environ.get(
                "CBX_ROOT",
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            )
            data_dir = os.path.join(cbx_root, "data")
        self.sites_dir = os.path.join(data_dir, "sites")

    # ── Project CRUD ────────────────────────────────────────────────────────────

    def create_project(
        self,
        name: str,
        template: str = "landing",
        title: str = "",
        description: str = "",
        mode: str = "template",
    ) -> dict:
        """
        Create a new site project directory with manifest and starter page.

        Returns the project manifest dict.
        Raises ValueError for bad inputs, FileExistsError if name is taken.
        """
        name = self._safe_name(name)
        if not name:
            raise ValueError(
                "Project name must contain only letters, numbers, hyphens, or underscores."
            )
        if template not in AVAILABLE_TEMPLATES:
            raise ValueError(
                f"Unknown template '{template}'. Available: {AVAILABLE_TEMPLATES}"
            )
        if mode not in AVAILABLE_MODES:
            raise ValueError(
                f"Unknown mode '{mode}'. Available: {AVAILABLE_MODES}"
            )

        project_dir = os.path.join(self.sites_dir, name)
        if os.path.exists(project_dir):
            raise FileExistsError(f"Project '{name}' already exists.")

        os.makedirs(os.path.join(project_dir, "pages"),  exist_ok=True)
        os.makedirs(os.path.join(project_dir, "assets"), exist_ok=True)
        os.makedirs(os.path.join(project_dir, "_build"), exist_ok=True)

        title       = title or name.replace("-", " ").replace("_", " ").title()
        description = description or f"{title} — built with CoreBuilderVX Website Builder."

        manifest = {
            "name":        name,
            "template":    template,
            "mode":        mode,
            "title":       title,
            "description": description,
            "created_at":  datetime.now(timezone.utc).isoformat(),
            "updated_at":  datetime.now(timezone.utc).isoformat(),
            "last_build":  None,
            "pages":       ["index"],
        }
        self._write_manifest(name, manifest)

        page_html = _TEMPLATES[template].substitute(
            title=title,
            description=description,
            css=_CSS_COMMON,
        )
        with open(
            os.path.join(project_dir, "pages", "index.html"), "w", encoding="utf-8"
        ) as fh:
            fh.write(page_html)

        return manifest

    def list_projects(self) -> List[dict]:
        """Return project manifests sorted newest-first by created_at."""
        if not os.path.isdir(self.sites_dir):
            return []
        projects = []
        for entry in sorted(os.listdir(self.sites_dir)):
            manifest_path = os.path.join(self.sites_dir, entry, "manifest.json")
            if os.path.isfile(manifest_path):
                try:
                    with open(manifest_path, encoding="utf-8") as fh:
                        projects.append(json.load(fh))
                except Exception:
                    pass
        projects.sort(key=lambda p: p.get("created_at", ""), reverse=True)
        return projects

    def get_project(self, name: str) -> dict:
        """Return a project manifest. Raises FileNotFoundError if absent."""
        name = self._safe_name(name)
        path = os.path.join(self.sites_dir, name, "manifest.json")
        if not os.path.isfile(path):
            raise FileNotFoundError(f"Project '{name}' not found.")
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)

    def delete_project(self, name: str) -> None:
        """Delete a project and all its files."""
        name = self._safe_name(name)
        project_dir = os.path.join(self.sites_dir, name)
        if not os.path.isdir(project_dir):
            raise FileNotFoundError(f"Project '{name}' not found.")
        shutil.rmtree(project_dir)

    # ── Build ───────────────────────────────────────────────────────────────────

    def build_project(self, name: str) -> str:
        """
        Generate the static site into _build/.

        Copies pages/*.html → _build/ and assets/ → _build/assets/.
        Returns the absolute path to the _build/ directory.
        """
        name        = self._safe_name(name)
        project_dir = self._project_dir(name)
        build_dir   = os.path.join(project_dir, "_build")

        if os.path.exists(build_dir):
            shutil.rmtree(build_dir)
        os.makedirs(build_dir)

        pages_dir = os.path.join(project_dir, "pages")
        if os.path.isdir(pages_dir):
            for fname in os.listdir(pages_dir):
                if fname.endswith(".html"):
                    shutil.copy2(
                        os.path.join(pages_dir, fname),
                        os.path.join(build_dir, fname),
                    )

        assets_src = os.path.join(project_dir, "assets")
        if os.path.isdir(assets_src) and os.listdir(assets_src):
            shutil.copytree(assets_src, os.path.join(build_dir, "assets"))

        manifest = self.get_project(name)
        manifest["updated_at"] = datetime.now(timezone.utc).isoformat()
        manifest["last_build"] = datetime.now(timezone.utc).isoformat()
        self._write_manifest(name, manifest)

        return build_dir

    # ── Preview ─────────────────────────────────────────────────────────────────

    def get_preview_path(self, name: str) -> str:
        """Return the absolute path to a project's _build/ directory."""
        name = self._safe_name(name)
        return os.path.join(self._project_dir(name), "_build")

    # ── Private helpers ─────────────────────────────────────────────────────────

    @staticmethod
    def _safe_name(name: str) -> str:
        """Strip unsafe characters; allow only alphanumerics, hyphens, underscores."""
        return re.sub(r"[^a-zA-Z0-9_\-]", "", name.strip())

    def _project_dir(self, name: str) -> str:
        path = os.path.join(self.sites_dir, name)
        if not os.path.isdir(path):
            raise FileNotFoundError(f"Project '{name}' not found.")
        return path

    def _write_manifest(self, name: str, manifest: dict) -> None:
        path = os.path.join(self.sites_dir, name, "manifest.json")
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(manifest, fh, indent=2)


# ── Convenience factory ────────────────────────────────────────────────────────

def get_builder() -> WebsiteBuilder:
    """Return a WebsiteBuilder using the CBX_ROOT data directory."""
    return WebsiteBuilder()


# ── CLI entry point ────────────────────────────────────────────────────────────

def _cli():
    parser = argparse.ArgumentParser(
        prog="website_builder.py",
        description="CoreBuilderVX Website Builder CLI",
    )
    sub = parser.add_subparsers(dest="action", required=True)

    # list
    sub.add_parser("list", help="List all site projects")

    # create
    p_create = sub.add_parser("create", help="Create a new site project")
    p_create.add_argument("--name",     required=True, help="Project name (slug)")
    p_create.add_argument("--template", default="landing",
                          choices=AVAILABLE_TEMPLATES, help="Starter template")
    p_create.add_argument("--title",    default="", help="Site title")
    p_create.add_argument("--desc",     default="", help="Site description")
    p_create.add_argument("--mode",     default="template",
                          choices=AVAILABLE_MODES, help="Editing mode")

    # build
    p_build = sub.add_parser("build", help="Build a site to static HTML")
    p_build.add_argument("--name", required=True, help="Project name")

    # get
    p_get = sub.add_parser("get", help="Print a project manifest")
    p_get.add_argument("--name", required=True, help="Project name")

    # delete
    p_del = sub.add_parser("delete", help="Delete a project")
    p_del.add_argument("--name", required=True, help="Project name")

    args = parser.parse_args()
    builder = WebsiteBuilder()

    if args.action == "list":
        projects = builder.list_projects()
        if not projects:
            print("No site projects found.")
            return
        print(f"{'Name':<22} {'Template':<12} {'Mode':<10} {'Last Build'}")
        print(f"{'-'*22} {'-'*12} {'-'*10} {'-'*20}")
        for p in projects:
            lb = p.get("last_build") or "never"
            if lb != "never":
                lb = lb[:16]
            print(f"{p['name']:<22} {p.get('template','?'):<12} "
                  f"{p.get('mode','?'):<10} {lb}")

    elif args.action == "create":
        try:
            m = builder.create_project(
                args.name,
                template=args.template,
                title=args.title,
                description=args.desc,
                mode=args.mode,
            )
            print(json.dumps(m, indent=2))
        except (ValueError, FileExistsError) as exc:
            print(f"Error: {exc}", file=sys.stderr)
            sys.exit(1)

    elif args.action == "build":
        try:
            build_dir = builder.build_project(args.name)
            print(f"Build complete: {build_dir}")
        except FileNotFoundError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            sys.exit(1)

    elif args.action == "get":
        try:
            print(json.dumps(builder.get_project(args.name), indent=2))
        except FileNotFoundError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            sys.exit(1)

    elif args.action == "delete":
        try:
            builder.delete_project(args.name)
            print(f"Project '{args.name}' deleted.")
        except FileNotFoundError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    _cli()
