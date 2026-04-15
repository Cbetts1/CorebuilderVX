# CoreBuilderVX — Architecture Overview

## What Is CoreBuilderVX?

CoreBuilderVX is an **adaptive, local-first build engine** that constructs OS
layers, full-stack applications, virtual environments, and lightweight AI
systems directly on any device — starting with a Samsung Galaxy S21 FE running
Termux, scaling up to desktop or server hardware.

It is **not an app or APK**. It is a shell tool with plug-and-play modules.

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    core.sh  (entrypoint)                    │
│            Reads hardware profile, routes commands          │
└──────────────┬────────────────────────────┬─────────────────┘
               │                            │
    ┌──────────▼──────────┐    ┌────────────▼────────────────┐
    │  menus/main_menu.sh │    │  api/internal_api.sh         │
    │  Interactive TUI    │    │  Logging, colours, helpers   │
    └──────────┬──────────┘    └─────────────────────────────┘
               │
   ┌───────────┼───────────────────────────────────────┐
   │           │                                       │
   ▼           ▼                                       ▼
modules/    modules/                             modules/
hardware/   os_builder/    os_tester/  boot_sim/  vcloud/
detect.sh   blueprint.sh   integrity  simulate   build.sh
            skeleton.sh    services   
            modules.sh     boot_test  
   │
   ▼
modules/vm/   modules/ai_runner/   modules/updater/
lite_vm.sh    local_ai.sh          self_upgrade.sh

   │
   ▼
modules/backend/            modules/frontend/
api.py  api.js              cockpit.html/css/js
(REST API)                  (Operator Cockpit UI)
```

---

## Layer Descriptions

| Layer | Files | Purpose |
|-------|-------|---------|
| Entrypoint | `core.sh` | Routes CLI commands to modules |
| Config | `config/` | Runtime and hardware configuration |
| Hardware | `modules/hardware/` | Auto-detects CPU, RAM, arch, tier |
| OS Builder | `modules/os_builder/` | Constructs OS directory trees + manifests |
| OS Tester | `modules/os_tester/` | Validates build integrity, services, boot |
| Boot Sim | `modules/boot_sim/` | Simulates boot sequence in terminal |
| Vcloud | `modules/vcloud/` | Creates multi-node virtual cloud configs |
| VM | `modules/vm/` | Lightweight VM shell (unshare / proot) |
| AI Runner | `modules/ai_runner/` | Routes to ollama / llama.cpp / gpt4all |
| Backend API | `modules/backend/` | Flask (Python) or plain Node.js REST API |
| Frontend | `modules/frontend/` | HTML/CSS/JS operator cockpit |
| Internal API | `api/internal_api.sh` | Shared helpers for all shell modules |
| Menus | `menus/` | Interactive TUI menus + wizards |
| Updater | `modules/updater/` | Git-based self-upgrade |

---

## Adaptive Hardware Tiers

CoreBuilderVX auto-tunes itself to the host hardware:

| Tier | Example | VM RAM | AI Tokens | Boot Delay |
|------|---------|--------|-----------|------------|
| phone | S21 FE/Termux | 128MB | 64 | 0.5s |
| rpi | Raspberry Pi | 128MB | 64 | 0.5s |
| laptop | General laptop | 512MB | 256 | 0.1s |
| desktop | Desktop/workstation | 2048MB | 512 | 0.05s |
| server | Server | 2048MB | 512 | 0.05s |

---

## Plug-and-Play Modules

All modules are standalone bash scripts that can be:
- Sourced from `core.sh` via menu
- Called directly: `bash modules/os_builder/blueprint.sh`
- Invoked via the REST API: `POST /api/v1/run {"command":"build"}`
- Triggered from the cockpit UI

New modules can be added by:
1. Creating a script in `modules/<name>/`
2. Adding an entry in `menus/main_menu.sh`
3. Registering the command in `core.sh` and `modules/backend/api.py`

---

## Data Flow

```
User input (shell / UI)
        │
        ▼
core.sh → load config → load hardware profile
        │
        ▼
module script runs → uses internal_api.sh helpers
        │
        ▼
writes to builds/ or data/ directory
        │
        ▼
REST API exposes results → cockpit.js fetches & renders
```
