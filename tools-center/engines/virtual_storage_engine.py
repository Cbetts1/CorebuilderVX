"""
virtual_storage_engine.py — Tools Center virtual storage engine.

Manages virtual drives (vdrives) stored under storage/vdrives/.
Each vdrive is a directory.  Provides create, delete, list, and
mount (symlink) operations.
"""

import os
import shutil
from typing import List, Optional

_BASE_DIR = os.path.join(os.path.dirname(__file__), "..", "storage", "vdrives")


def _base() -> str:
    os.makedirs(_BASE_DIR, exist_ok=True)
    return _BASE_DIR


def list_drives() -> List[str]:
    """Return a list of existing virtual drive names."""
    base = _base()
    return [
        name for name in os.listdir(base)
        if os.path.isdir(os.path.join(base, name))
    ]


def create_drive(name: str) -> str:
    """
    Create a new virtual drive directory.
    Returns the path to the new drive.
    Raises FileExistsError if the drive already exists.
    """
    path = os.path.join(_base(), name)
    if os.path.exists(path):
        raise FileExistsError(f"Virtual drive '{name}' already exists.")
    os.makedirs(path)
    return path


def delete_drive(name: str):
    """
    Delete a virtual drive and all its contents.
    Raises FileNotFoundError if the drive does not exist.
    """
    path = os.path.join(_base(), name)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Virtual drive '{name}' not found.")
    shutil.rmtree(path)


def get_drive_path(name: str) -> Optional[str]:
    """Return the filesystem path of a virtual drive, or None if it doesn't exist."""
    path = os.path.join(_base(), name)
    return path if os.path.exists(path) else None


def drive_info(name: str) -> dict:
    """Return metadata about a virtual drive."""
    path = os.path.join(_base(), name)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Virtual drive '{name}' not found.")
    total = sum(
        os.path.getsize(os.path.join(dp, f))
        for dp, _, files in os.walk(path)
        for f in files
    )
    return {
        "name": name,
        "path": path,
        "size_bytes": total,
        "files": sum(len(files) for _, _, files in os.walk(path)),
    }
