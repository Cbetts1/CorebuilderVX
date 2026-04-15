# CoreBuilderVX — Modules Reference

## Overview

All modules live under `modules/<name>/` and are plug-and-play shell scripts.
Each module can be run standalone, via the menu, or via the REST API.

---

## Hardware Detection — `modules/hardware/detect.sh`

Detects and reports: arch, CPU cores/model, RAM, disk, OS, kernel, env, display,
GPU, battery, network. Auto-tunes VM/AI settings by tier.

```bash
# Show hardware profile
./core.sh hardware

# Save/refresh hardware profile
./core.sh hardware --save
# or
bash modules/hardware/detect.sh --save
```

**Output tiers:** `phone | rpi | laptop | desktop | server`

---

## OS Builder — `modules/os_builder/`

### blueprint.sh
Main orchestrator. Reads `CBX_OS_TYPE`, `CBX_OS_ARCH`, `CBX_BUILD_NAME`,
`CBX_BUILD_MODULES` and drives the full build pipeline.

### skeleton.sh
Creates the base OS directory tree:
`boot/ bin/ sbin/ lib/ etc/ var/ tmp/ home/ proc/ sys/ dev/`
Writes init stub, `os-release`, `fstab`.

### modules.sh
Plug-and-play module loader. Supported modules:

| Module | What it adds |
|--------|-------------|
| `base` | Shell command stubs |
| `networking` | `/etc/network/interfaces`, `resolv.conf` |
| `filesystem` | Extended fstab entries |
| `services` | sshd, cron, syslog init stubs |
| `ui` | Cockpit HTML to `/usr/share/cbx-ui/` |
| `ai` | AI runner to `/opt/cbx-ai/` |
| `vm` | VM script to `/opt/cbx-vm/` |
| `vcloud` | Vcloud script to `/opt/cbx-vcloud/` |

---

## OS Tester — `modules/os_tester/`

### integrity.sh
Checks build directory structure, required files, manifest, init scripts.

### services.sh
Validates service scripts: executable, have start/stop/status handlers.

### boot_test.sh
Validates boot sequence: bootloader version, init syntax, OS identity,
mount point directories.

```bash
./core.sh test            # integrity (default)
./core.sh test service    # service tests
./core.sh test boot       # boot tests
./core.sh test all        # all three
```

---

## Boot Simulator — `modules/boot_sim/simulate.sh`

Simulates a full OS boot sequence in the terminal with configurable speed.

```bash
./core.sh sim
# Adjust speed:
CBX_BOOTSIM_DELAY=0.05 ./core.sh sim   # fast
CBX_BOOTSIM_DELAY=1    ./core.sh sim   # slow
```

---

## Vcloud Builder — `modules/vcloud/build.sh`

Creates multi-node virtual cloud environment configs.

Types: `mini` (1 node), `dev` (3 nodes), `full` (5 nodes), `custom`

Output: `data/vclouds/<name>/`
- Per-node `node-N/etc/node.conf`
- Per-node `node-N/run.sh`
- `cloud.json` manifest
- `start-all.sh` launcher

```bash
./core.sh vcloud
```

---

## Lightweight VM — `modules/vm/lite_vm.sh`

Simulates a VM using the best available method:
1. `unshare --pid` (Linux kernel namespaces)
2. `proot` (Termux-friendly chroot)
3. Plain bash subshell (fallback)

VM state saved to `data/vms/<name>/`

```bash
./core.sh vm
```

---

## Local AI Runner — `modules/ai_runner/local_ai.sh`

Auto-detects and uses the best available AI backend:

| Backend | Detection | Notes |
|---------|-----------|-------|
| `ollama` | `command -v ollama` | Best for Termux |
| `llama.cpp` | `command -v llama-cli` | Compiled binary |
| `llama_cpp_python` | `python3 -c "import llama_cpp"` | Python binding |
| `transformers` | `python3 -c "import transformers"` | Hugging Face |
| `gpt4all` | `python3 -c "import gpt4all"` | Easy to install |
| `stub` | fallback | Demo mode, no real model |

```bash
./core.sh ai
# Set preferred model:
CBX_AI_MODEL=llama3.2 ./core.sh ai
```

---

## Backend API — `modules/backend/`

### api.py (Python/Flask)
Full REST API. Endpoints:
- `GET /api/v1/status` — health check
- `GET /api/v1/hardware` — hardware profile
- `GET /api/v1/builds` — list builds
- `GET /api/v1/builds/<name>` — build detail
- `GET /api/v1/modules` — list modules
- `GET /api/v1/logs` — recent log entries
- `POST /api/v1/run` — run a whitelisted command

### api.js (Node.js)
Same API implemented in pure Node.js (no npm deps required).

### api_manager.sh
Start/stop/status shell wrapper.

```bash
# Via menu: option 9
# Or directly:
bash modules/backend/api_manager.sh start
bash modules/backend/api_manager.sh stop
bash modules/backend/api_manager.sh status
```

---

## Operator Cockpit — `modules/frontend/`

| File | Purpose |
|------|---------|
| `cockpit.html` | Main UI page |
| `cockpit.css` | Adaptive dark theme styles |
| `cockpit.js` | API integration and interactivity |
| `serve.sh` | Local HTTP server launcher |

Served via `./core.sh frontend` → `http://127.0.0.1:8766/cockpit.html`

---

## Updater — `modules/updater/self_upgrade.sh`

Fetches latest changes from GitHub and applies them in-place.
Backs up `config/` and `data/` before updating.

```bash
./core.sh update
```

---

## Internal API — `api/internal_api.sh`

Shared helper library sourced by all modules. Provides:

| Function | Description |
|----------|-------------|
| `cbx_info msg` | Green info log |
| `cbx_warn msg` | Yellow warning |
| `cbx_error msg` | Red error (stderr) |
| `cbx_debug msg` | Dim debug (if log level=debug) |
| `cbx_step msg` | Cyan step indicator |
| `cbx_ok msg` | Green ✓ success |
| `cbx_fail msg` | Red ✗ failure |
| `cbx_banner title` | ASCII art banner |
| `cbx_header title` | Section header box |
| `cbx_confirm prompt` | Yes/no prompt |
| `cbx_prompt prompt default` | Value prompt |
| `cbx_spinner_start msg` | Start spinner |
| `cbx_spinner_stop` | Stop spinner |
| `cbx_progress n total label` | Progress bar |
| `cbx_require cmd` | Assert command exists |
| `cbx_build_log tag msg` | Write to build log |
| `cbx_check_disk mb` | Assert disk space |
| `cbx_load_module path` | Source a module safely |
| `cbx_pause` | Press-any-key pause |
