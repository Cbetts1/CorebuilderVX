# TOOLS CENTER

**Modular · Menu-driven · Engine-based**

All tools. One place. No clutter.

---

## Architecture

```
tools-center/
├── main.py              ← Entry point
├── startup.py           ← 7-step startup sequence
│
├── core/
│   ├── tool_registry.json   ← Tool definitions
│   ├── navigation.py        ← Menu stack
│   ├── state.py             ← Global runtime state
│   └── logger.py            ← File + stdout logger
│
├── engines/
│   ├── touch_engine.py          ← Keyboard/touch input
│   ├── menu_engine.py           ← Menu rendering + dispatch
│   ├── ui_engine.py             ← ANSI colours, layout helpers
│   ├── simulation_engine.py     ← Dry-run mode
│   ├── virtual_storage_engine.py← Virtual drive management
│   ├── cloud_engine.py          ← Cloud simulation
│   ├── shell_engine.py          ← Subprocess + interactive shell
│   └── settings_engine.py       ← Load/save settings.json
│
├── ui/
│   ├── header.py    ← Page header renderer
│   ├── footer.py    ← Page footer renderer
│   ├── grid.py      ← 2-column grid layout
│   ├── list.py      ← Numbered list layout
│   ├── themes.py    ← Colour palettes
│   └── icons.py     ← Emoji icon map
│
├── menus/
│   ├── main_menu.py         ← Root panel (2-column grid)
│   ├── build_menu.py
│   ├── code_menu.py
│   ├── web_menu.py
│   ├── program_menu.py
│   ├── ai_menu.py
│   ├── vm_menu.py
│   ├── simulation_menu.py
│   ├── virtual_storage_menu.py
│   ├── cloud_menu.py
│   ├── backend_menu.py
│   ├── storage_menu.py
│   ├── diagnostics_menu.py
│   ├── network_menu.py
│   ├── hardware_menu.py
│   ├── templates_menu.py
│   ├── learning_menu.py
│   ├── shell_menu.py
│   └── settings_menu.py
│
├── tools/
│   ├── build/           compile_project, generate_makefile
│   ├── code/            run_code, lint_code, format_code
│   ├── web/             start_web_server, build_static_site
│   ├── program/         install_package, list_packages
│   ├── ai/              run_ai_model, list_ai_models
│   ├── vm/              start_vm, stop_vm
│   ├── simulation/      run_simulation, list_simulations
│   ├── virtual_storage/ create_vdrive, list_vdrives
│   ├── cloud/           cloud_deploy, cloud_status
│   ├── backend/         start_api_server, test_endpoint
│   ├── storage/         list_files, backup_files
│   ├── diagnostics/     run_diagnostics, check_health
│   ├── network/         ping_host, scan_ports
│   ├── hardware/        detect_hardware, benchmark_cpu
│   ├── templates/       list_templates, apply_template
│   ├── learning/        start_lesson, list_lessons
│   └── shell/           open_shell, run_shell_command
│
├── settings/
│   └── settings.json
│
├── storage/
│   ├── vdrives/
│   └── logs/
│
└── cloud/
    ├── builds/
    ├── deploy/
    └── logs/
```

---

## Startup Sequence

```
startup.py
  1. Load settings       → engines/settings_engine.py
  2. Init engines        → all engines/
  3. Load registry       → core/tool_registry.json
  4. Prepare UI          → ui/themes.py
  5. Preload menus       → menus/
  6. Preload tools       → tools/
  7. Show main menu      → menus/main_menu.py
```

---

## Tool Registry

Every tool is declared in `core/tool_registry.json`:

```json
{
  "id": "run_code",
  "group": "code",
  "label": "Run Code",
  "icon": "💻",
  "handler": "tools.code.run_code",
  "supports_simulation": true
}
```

---

## Adding a New Tool

1. Add entry to `core/tool_registry.json`
2. Create `tools/<group>/<id>.py` with `run()` and `simulate()`
3. No menu changes needed — menus load from the registry automatically

---

## Simulation Mode

Run with `--simulate` to enable dry-run mode:

```bash
python main.py --simulate
```

When active, tools that support simulation call `simulate()` instead of `run()`.
A `[SIM]` badge is shown in the footer and main menu.

---

## Themes

| Theme   | Description         |
|---------|---------------------|
| default | Cyan/blue on dark   |
| dark    | Magenta/cyan on dark|
| plain   | No colour output    |

Change via Settings menu or `settings/settings.json`.

---

## CLI Flags

| Flag           | Effect                        |
|----------------|-------------------------------|
| `--simulate`   | Enable simulation mode        |
| `--no-colour`  | Disable ANSI colour output    |
| `--debug`      | Enable debug logging          |
| `--help`       | Show help                     |
