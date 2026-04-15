# CoreBuilderVX — Usage Guide

## Quick Start

```bash
# 1. Clone (or already have the repo)
cd CoreBuilderVX

# 2. Install dependencies (Termux / Linux / macOS)
bash install.sh

# 3. Launch
./core.sh
# or if symlink was created:
cbx
```

---

## CLI Commands

```
./core.sh [command] [options]
```

| Command | Description |
|---------|-------------|
| `menu` | Launch interactive menu (default) |
| `build` | OS Builder |
| `test` | OS Tester (integrity by default) |
| `test service` | Service test only |
| `test boot` | Boot test only |
| `test all` | All tests |
| `sim` | Boot Simulator |
| `vcloud` | Vcloud Builder |
| `vm` | Lightweight VM |
| `ai` | Local AI Runner |
| `hardware` | Show hardware profile |
| `hardware --save` | Re-detect and save hardware profile |
| `update` | Self-upgrade from GitHub |
| `frontend` | Serve operator cockpit UI |
| `help` | Show help |
| `--version` | Print version |

---

## Interactive Menu

Run `./core.sh` and use the number keys or letters shown:

```
  1  OS Builder          — Construct OS layers & blueprints
  2  OS Tester           — Integrity, service & boot tests
  3  Boot Simulator      — Simulate OS boot sequence
  4  Vcloud Builder      — Virtual cloud environments
  5  Lightweight VM      — Spin up local VM simulation
  6  Local AI Runner     — Run small AI models locally
  7  Operator Cockpit    — Launch frontend UI
  8  Hardware Profile    — View/refresh hardware info
  9  Backend API         — Start/stop API engine
  U  Self-Upgrade        — Update CoreBuilderVX
  W  Setup Wizard        — First-time configuration
  Q  Quit
```

---

## Environment Variables

All settings can be overridden via environment variables before running:

```bash
CBX_API_PORT=9000 CBX_OS_TYPE=full ./core.sh build
```

Key variables (see `config/default.conf` for full list):

| Variable | Default | Description |
|----------|---------|-------------|
| `CBX_ROOT` | auto | Root directory of CoreBuilderVX |
| `CBX_BACKEND` | auto | API backend: auto/python/node/none |
| `CBX_API_PORT` | 8765 | API server port |
| `CBX_OS_TYPE` | minimal | Build type: minimal/standard/full |
| `CBX_OS_ARCH` | auto | Target architecture |
| `CBX_AI_MODEL` | none | AI model to use |
| `CBX_NO_COLOR` | 0 | Disable colour output |
| `CBX_LOG_LEVEL` | info | Log level: debug/info/warn/error |

---

## Operator Cockpit UI

Start the API backend and frontend server:

```bash
# Start API
./core.sh menu → option 9 → Start
# or directly:
bash modules/backend/api_manager.sh start

# Start cockpit UI
./core.sh frontend
# Open: http://127.0.0.1:8766/cockpit.html
```

---

## Build Output

Builds are saved to `builds/<name>/`:

```
builds/
└── cbx-build-20240101-120000/
    ├── manifest.json   ← build metadata
    ├── boot/           ← bootloader stubs
    ├── bin/            ← binary stubs
    ├── etc/            ← config files
    │   ├── os-release
    │   ├── fstab
    │   └── init.d/
    ├── var/
    └── ...
```

---

## Adding a Custom Module

1. Create `modules/mymodule/run.sh`:
```bash
#!/usr/bin/env bash
CBX_ROOT="${CBX_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
source "$CBX_ROOT/api/internal_api.sh"
cbx_header "My Module"
cbx_info "Hello from my module!"
cbx_pause
```

2. Add to `menus/main_menu.sh`:
```bash
echo -e "  ${C_CYAN}M${C_NC}  My Module"
# ...
m) source "$CBX_ROOT/modules/mymodule/run.sh" ;;
```

3. Add to `core.sh`:
```bash
mymodule) source "$CBX_ROOT/modules/mymodule/run.sh" "$@" ;;
```

That's it — plug and play.
