"""
cloud_engine.py — Tools Center cloud simulation engine.

Simulates cloud deployment, status checks, and log retrieval.
All operations are local filesystem simulations under cloud/.
"""

import os
import json
import datetime
from typing import List, Dict, Any

_CLOUD_DIR = os.path.join(os.path.dirname(__file__), "..", "cloud")
_BUILDS_DIR  = os.path.join(_CLOUD_DIR, "builds")
_DEPLOY_DIR  = os.path.join(_CLOUD_DIR, "deploy")
_LOGS_DIR    = os.path.join(_CLOUD_DIR, "logs")


def _ensure_dirs():
    for d in (_BUILDS_DIR, _DEPLOY_DIR, _LOGS_DIR):
        os.makedirs(d, exist_ok=True)


def deploy(project_name: str, payload: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Simulate deploying a project to the cloud.
    Writes a deployment record to cloud/deploy/.
    Returns the deployment record.
    """
    _ensure_dirs()
    ts = datetime.datetime.now().isoformat()
    record = {
        "project": project_name,
        "deployed_at": ts,
        "status": "deployed",
        "payload": payload or {},
    }
    filename = f"{project_name}_{ts.replace(':', '-')}.json"
    path = os.path.join(_DEPLOY_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(record, f, indent=2)
    _log(f"Deployed '{project_name}' at {ts}")
    return record


def status(project_name: str = None) -> List[Dict[str, Any]]:
    """
    Return deployment status records.
    If project_name is given, filter to that project.
    """
    _ensure_dirs()
    records = []
    for fname in sorted(os.listdir(_DEPLOY_DIR)):
        if not fname.endswith(".json"):
            continue
        path = os.path.join(_DEPLOY_DIR, fname)
        with open(path, encoding="utf-8") as f:
            record = json.load(f)
        if project_name is None or record.get("project") == project_name:
            records.append(record)
    return records


def get_logs(limit: int = 50) -> List[str]:
    """Return the last `limit` lines from the cloud log."""
    _ensure_dirs()
    log_file = os.path.join(_LOGS_DIR, "cloud.log")
    if not os.path.exists(log_file):
        return []
    with open(log_file, encoding="utf-8") as f:
        lines = f.readlines()
    return [l.rstrip() for l in lines[-limit:]]


def _log(message: str):
    _ensure_dirs()
    log_file = os.path.join(_LOGS_DIR, "cloud.log")
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"[{ts}] {message}\n")
