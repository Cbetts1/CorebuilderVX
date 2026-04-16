#!/usr/bin/env python3
"""
CoreBuilderVX — Python API Engine (Flask)
Lightweight REST API for the CBX tool
"""

import os
import sys
import json
import subprocess
import argparse
from datetime import datetime

try:
    from flask import Flask, jsonify, request
    from flask_cors import CORS
except ImportError:
    print("[CBX-API] Flask not installed. Run: pip3 install flask flask-cors")
    sys.exit(1)

app = Flask(__name__)
CORS(app)

CBX_ROOT = os.environ.get("CBX_ROOT", os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))


def load_config():
    """Load hardware profile if available."""
    conf = {"version": "1.0.0", "env": "unknown", "tier": "unknown"}
    hw_conf = os.path.join(CBX_ROOT, "config", "hardware.conf")
    if os.path.exists(hw_conf):
        with open(hw_conf) as f:
            for line in f:
                line = line.strip()
                if line.startswith("CBX_HW_") and "=" in line:
                    key, _, val = line.partition("=")
                    conf[key.strip()] = val.strip().strip('"')
    return conf


# ---- Routes -----------------------------------------------------------------

@app.route("/api/v1/status", methods=["GET"])
def status():
    """Health check."""
    return jsonify({
        "status": "ok",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "cbx_root": CBX_ROOT,
    })


@app.route("/api/v1/hardware", methods=["GET"])
def hardware():
    """Return hardware profile."""
    return jsonify(load_config())


@app.route("/api/v1/builds", methods=["GET"])
def list_builds():
    """List available builds."""
    builds_dir = os.path.join(CBX_ROOT, "builds")
    builds = []
    if os.path.isdir(builds_dir):
        for name in sorted(os.listdir(builds_dir), reverse=True):
            build_path = os.path.join(builds_dir, name)
            manifest_path = os.path.join(build_path, "manifest.json")
            if os.path.isdir(build_path):
                manifest = {}
                if os.path.exists(manifest_path):
                    try:
                        with open(manifest_path) as f:
                            manifest = json.load(f)
                    except Exception:
                        pass
                builds.append({"name": name, "path": build_path, **manifest})
    return jsonify({"builds": builds, "count": len(builds)})


@app.route("/api/v1/builds/<build_name>", methods=["GET"])
def get_build(build_name):
    """Get details of a specific build."""
    # Sanitise build_name: allow only alphanumerics, hyphens and underscores
    safe_name = os.path.basename(build_name)
    if not safe_name or not all(c.isalnum() or c in "-_." for c in safe_name):
        return jsonify({"error": "Invalid build name"}), 400
    builds_dir = os.path.join(CBX_ROOT, "builds")
    manifest_path = os.path.realpath(os.path.join(builds_dir, safe_name, "manifest.json"))
    # Guard against path traversal — CoreBuilderVX is POSIX-only (Termux/Linux/macOS)
    if not manifest_path.startswith(os.path.realpath(builds_dir) + os.sep):
        return jsonify({"error": "Invalid build path"}), 400
    if not os.path.exists(manifest_path):
        return jsonify({"error": "Build not found"}), 404
    with open(manifest_path) as f:
        return jsonify(json.load(f))


@app.route("/api/v1/modules", methods=["GET"])
def list_modules():
    """List available plug-and-play modules."""
    modules_dir = os.path.join(CBX_ROOT, "modules")
    modules = []
    if os.path.isdir(modules_dir):
        for name in sorted(os.listdir(modules_dir)):
            mod_path = os.path.join(modules_dir, name)
            if os.path.isdir(mod_path):
                scripts = [f for f in os.listdir(mod_path) if f.endswith(".sh")]
                modules.append({"name": name, "scripts": scripts})
    return jsonify({"modules": modules})


@app.route("/api/v1/sites", methods=["GET"])
def list_sites():
    """Return all website projects from the project index."""
    index_path = os.path.join(CBX_ROOT, "builds", "websites", "index.json")
    projects = []
    if os.path.exists(index_path):
        with open(index_path, encoding="utf-8") as f:
            try:
                projects = json.load(f)
            except Exception:
                projects = []
    return jsonify({"sites": projects, "count": len(projects)})


@app.route("/api/v1/sites/templates", methods=["GET"])
def list_site_templates():
    """Return all available website templates."""
    templates_dir = os.path.join(CBX_ROOT, "modules", "site_builder", "templates")
    templates = []
    if os.path.isdir(templates_dir):
        for name in sorted(os.listdir(templates_dir)):
            tpath = os.path.join(templates_dir, name)
            if os.path.isdir(tpath):
                files = os.listdir(tpath)
                templates.append({"name": name, "files": files})
    return jsonify({"templates": templates})


@app.route("/api/v1/logs", methods=["GET"])
def get_logs():
    """Return recent build log entries."""
    log_path = os.path.join(CBX_ROOT, "builds", "build.log")
    lines = []
    if os.path.exists(log_path):
        with open(log_path) as f:
            lines = f.readlines()[-100:]
    return jsonify({"log": [l.rstrip() for l in lines]})


@app.route("/api/v1/run", methods=["POST"])
def run_command():
    """Run a safe CBX module command (whitelist-only)."""
    data = request.get_json(force=True, silent=True) or {}
    allowed = {"hardware", "build", "test", "sim", "vcloud", "vm", "update",
               "site_create", "site_open", "site_preview"}
    cmd = data.get("command", "")
    if cmd not in allowed:
        return jsonify({"error": f"Command not allowed: {cmd}"}), 400

    site_builder = os.path.join(CBX_ROOT, "modules", "site_builder", "website_builder.py")

    script_map = {
        "hardware":     os.path.join(CBX_ROOT, "modules", "hardware",   "detect.sh"),
        "build":        os.path.join(CBX_ROOT, "modules", "os_builder", "blueprint.sh"),
        "test":         os.path.join(CBX_ROOT, "modules", "os_tester",  "integrity.sh"),
        "sim":          os.path.join(CBX_ROOT, "modules", "boot_sim",   "simulate.sh"),
        "vcloud":       os.path.join(CBX_ROOT, "modules", "vcloud",     "build.sh"),
        "vm":           os.path.join(CBX_ROOT, "modules", "vm",         "lite_vm.sh"),
        "update":       os.path.join(CBX_ROOT, "modules", "updater",    "self_upgrade.sh"),
    }

    # Site builder commands are Python, not shell scripts
    if cmd in ("site_create", "site_open", "site_preview"):
        if not os.path.exists(site_builder):
            return jsonify({"error": "website_builder.py not found"}), 404
        sub_cmd = {"site_create": "create", "site_open": "open", "site_preview": "preview"}[cmd]
        extra_args = []
        if cmd == "site_create":
            name     = data.get("name", "")
            template = data.get("template", "")
            if name:
                extra_args.append(name)
            if template:
                extra_args.append(template)
        elif cmd in ("site_open", "site_preview"):
            name = data.get("name", "")
            if name:
                extra_args.append(name)
        try:
            result = subprocess.run(
                [sys.executable, site_builder, sub_cmd] + extra_args,
                capture_output=True, text=True, timeout=30,
                env={**os.environ, "CBX_ROOT": CBX_ROOT, "CBX_NO_COLOR": "1"}
            )
            return jsonify({
                "command":    cmd,
                "returncode": result.returncode,
                "stdout":     result.stdout[-4096:],
                "stderr":     result.stderr[-1024:],
            })
        except subprocess.TimeoutExpired:
            return jsonify({"error": "Command timed out"}), 504
        except Exception:
            return jsonify({"error": "Internal server error"}), 500

    script = script_map.get(cmd)
    if not script or not os.path.exists(script):
        return jsonify({"error": "Script not found"}), 404

    try:
        result = subprocess.run(
            ["bash", script],
            capture_output=True, text=True, timeout=60,
            env={**os.environ, "CBX_ROOT": CBX_ROOT, "CBX_NO_COLOR": "1"}
        )
        return jsonify({
            "command": cmd,
            "returncode": result.returncode,
            "stdout": result.stdout[-4096:],
            "stderr": result.stderr[-1024:],
        })
    except subprocess.TimeoutExpired:
        return jsonify({"error": "Command timed out"}), 504
    except Exception:
        return jsonify({"error": "Internal server error"}), 500


# ---- Entrypoint -------------------------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CoreBuilderVX API")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    print(f"[CBX-API] Starting Python backend on {args.host}:{args.port}")
    app.run(host=args.host, port=args.port, debug=args.debug)
