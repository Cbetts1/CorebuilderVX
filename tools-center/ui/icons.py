"""
icons.py — Tools Center icon map.

Maps group/tool IDs to emoji icons.
"""

ICONS = {
    # Groups
    "build":           "🛠️",
    "code":            "💻",
    "web":             "🌐",
    "program":         "📦",
    "ai":              "⚙️",
    "vm":              "🖥️",
    "simulation":      "🎛️",
    "virtual_storage": "💾",
    "cloud":           "☁️",
    "backend":         "🔌",
    "storage":         "📂",
    "diagnostics":     "🩺",
    "network":         "📡",
    "hardware":        "🔧",
    "templates":       "📁",
    "learning":        "📘",
    "shell":           ">_",
    "settings":        "⚙️",
    "exit":            "⏻",
    # Common actions
    "run":             "▶️",
    "stop":            "⏹️",
    "list":            "📋",
    "create":          "✨",
    "delete":          "🗑️",
    "deploy":          "🚀",
    "status":          "📊",
    "info":            "ℹ️",
    "back":            "←",
    "ok":              "✔️",
    "error":           "✗",
    "warn":            "⚠️",
}


def get(key: str, fallback: str = "•") -> str:
    """Return the icon for a given key, or fallback if not found."""
    return ICONS.get(key, fallback)
