# CoreBuilderVX

**Adaptive, local‑first build engine** — runs on your phone today, scales to any hardware.  
Designed for operator‑grade workflows in **Termux** and any POSIX shell. Not an app — it's a tool.

---

## Quick Start (Termux / Any Shell)

```bash
# Clone
git clone https://github.com/Cbetts1/CorebuilderVX
cd CorebuilderVX

# Install dependencies (auto-detects Termux / Linux / macOS)
bash install.sh

# Launch
./core.sh          # interactive menu
cbx                # if symlink was created
cbx build          # OS builder direct
cbx hardware       # show hardware profile
cbx ai             # local AI runner
```

---

## What's Inside

| Module | Command | Description |
|--------|---------|-------------|
| **OS Builder** | `cbx build` | Constructs OS directory trees, skeletons, manifests |
| **OS Tester** | `cbx test` | Integrity, service, and boot tests |
| **Boot Simulator** | `cbx sim` | Simulates OS boot sequence in terminal |
| **Vcloud Builder** | `cbx vcloud` | Creates multi-node virtual cloud environments |
| **Lightweight VM** | `cbx vm` | Shell VM (unshare / proot / plain bash) |
| **Local AI Runner** | `cbx ai` | Runs ollama / llama.cpp / gpt4all / transformers |
| **Backend API** | `cbx menu → 9` | Flask (Python) or Node.js REST API |
| **Operator Cockpit** | `cbx frontend` | HTML/CSS/JS dashboard at localhost:8766 |
| **Hardware Detection** | `cbx hardware` | Auto-detects arch, RAM, tier, and tunes settings |
| **Self-Upgrade** | `cbx update` | Git-based in-place update |

---

## Folder Structure

```
CoreBuilderVX/
├── core.sh                    ← Main entrypoint
├── install.sh                 ← Dependency installer
├── config/
│   ├── default.conf           ← Default settings
│   └── hardware.conf          ← Auto-generated hardware profile
├── modules/
│   ├── hardware/detect.sh     ← Hardware detection
│   ├── os_builder/            ← blueprint, skeleton, modules
│   ├── os_tester/             ← integrity, services, boot_test
│   ├── boot_sim/simulate.sh   ← Boot simulator
│   ├── vcloud/build.sh        ← Vcloud builder
│   ├── vm/lite_vm.sh          ← Lightweight VM
│   ├── ai_runner/local_ai.sh  ← Local AI runner
│   ├── backend/               ← api.py + api.js + api_manager.sh
│   ├── frontend/              ← cockpit.html + cockpit.css + cockpit.js
│   └── updater/self_upgrade.sh
├── menus/
│   ├── main_menu.sh
│   └── wizards/               ← setup_wizard, build_wizard
├── api/internal_api.sh        ← Shared logging/UI helpers
└── docs/                      ← architecture, modules, usage, termux_setup
```

---

## Adaptive Hardware Tiers

CoreBuilderVX auto-detects your device and tunes itself:

| Tier | Example | VM RAM | AI Tokens |
|------|---------|--------|-----------|
| **phone** | S21 FE / Termux | 128MB | 64 |
| **rpi** | Raspberry Pi | 128MB | 64 |
| **laptop** | Any laptop | 512MB | 256 |
| **desktop/server** | Desktop | 2048MB | 512 |

---

## Plug-and-Play Modules

Every module is a standalone shell script. Add your own:
1. Create `modules/mymodule/run.sh`
2. Add to `menus/main_menu.sh`
3. Add to `core.sh`

See [docs/modules.md](docs/modules.md) for the full API reference.

---

## Documentation

| Doc | Description |
|-----|-------------|
| [docs/termux_setup.md](docs/termux_setup.md) | Full Termux / Android setup guide |
| [docs/usage.md](docs/usage.md) | CLI commands, env vars, examples |
| [docs/modules.md](docs/modules.md) | All modules documented |
| [docs/architecture.md](docs/architecture.md) | System architecture overview |

---

## Primary Target

**Samsung Galaxy S21 FE running Termux** — but works on any POSIX shell environment.

