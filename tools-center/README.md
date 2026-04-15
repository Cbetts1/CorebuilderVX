# Tools Center

> **Modular, menu-driven, engine-based tool hub.**  
> All tools. One place. No clutter.

---

## Quick Start

```bash
cd tools-center
python main.py
```

### CLI options

```bash
python main.py --simulate     # Dry-run mode (no real changes)
python main.py --no-colour    # Disable ANSI colours
python main.py --debug        # Verbose debug logging
```

---

## Main Panel

```
╔══════════════════════════════════════╗
║            TOOLS CENTER             ║
║  All tools. One place. No clutter.  ║
╚══════════════════════════════════════╝

  🛠️  Build Tools          💻  Code Tools
  🌐  Web Tools             📦  Program Tools
  ⚙️  AI Tools              🖥️  VM Tools
  🎛️  Simulation Tools      💾  Virtual Storage
  ☁️  Cloud Tools           🔌  Backend Tools
  📂  Storage Tools         🩺  Diagnostics
  📡  Network Tools         🔧  Hardware Tools
  📁  Templates             📘  Learning
  >_  Shell Tools           ⚙️  Settings
  ⏻  Exit
```

---

## Tool Groups

| Icon | Group           | Tools                                    |
|------|-----------------|------------------------------------------|
| 🛠️  | Build           | Compile Project, Generate Makefile       |
| 💻  | Code            | Run Code, Lint Code, Format Code         |
| 🌐  | Web             | Start Web Server, Build Static Site      |
| 📦  | Program         | Install Package, List Packages           |
| ⚙️  | AI              | Run AI Model, List AI Models             |
| 🖥️  | VM              | Start VM, Stop VM                        |
| 🎛️  | Simulation      | Run Simulation, List Simulations         |
| 💾  | Virtual Storage | Create Virtual Drive, List Virtual Drives|
| ☁️  | Cloud           | Deploy to Cloud, Cloud Status            |
| 🔌  | Backend         | Start API Server, Test Endpoint          |
| 📂  | Storage         | List Files, Backup Files                 |
| 🩺  | Diagnostics     | Run Diagnostics, Check System Health     |
| 📡  | Network         | Ping Host, Scan Ports                    |
| 🔧  | Hardware        | Detect Hardware, Benchmark CPU           |
| 📁  | Templates       | List Templates, Apply Template           |
| 📘  | Learning        | Start Lesson, List Lessons               |
| >_  | Shell           | Open Shell, Run Shell Command            |
| ⚙️  | Settings        | View Settings, Edit a Setting            |

---

## Requirements

- Python 3.8+
- No external dependencies (stdlib only)

---

## Extending

### Add a tool

1. Add an entry to `core/tool_registry.json`
2. Create `tools/<group>/<tool_id>.py` implementing `run()` and `simulate()`
3. Done — the menu auto-discovers tools from the registry

### Add a group

1. Create `tools/<group>/` directory and `__init__.py`
2. Add tools as above
3. Create `menus/<group>_menu.py` using any existing menu as a template
4. Wire it into `menus/main_menu.py`

---

## Settings

Stored in `settings/settings.json`:

| Key                    | Default     | Description                        |
|------------------------|-------------|------------------------------------|
| `theme`                | `"default"` | UI colour theme                    |
| `simulation_mode`      | `false`     | Start in simulation mode           |
| `colour_enabled`       | `true`      | ANSI colour output                 |
| `debug_mode`           | `false`     | Verbose logging                    |
| `default_shell`        | `"/bin/sh"` | Shell used by shell tools          |
| `log_level`            | `"INFO"`    | Logger verbosity                   |
| `cloud_provider`       | `"local"`   | Cloud backend                      |
| `vdrive_default_size_mb`| `512`      | Default virtual drive size (MB)    |
| `ai_model`             | `"llama"`   | AI model name                      |
| `editor`               | `"nano"`    | Text editor command                |

---

## Logs

- `storage/logs/tools_center.log` — application log  
- `cloud/logs/cloud.log` — cloud deployment log
