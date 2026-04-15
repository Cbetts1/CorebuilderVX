# CoreBuilderVX — Termux Setup Guide

This guide covers everything needed to run CoreBuilderVX on a
**Samsung Galaxy S21 FE** (or any Android device) using **Termux**.

---

## 1. Install Termux

- Download from [F-Droid](https://f-droid.org/packages/com.termux/) (recommended)
- **Do NOT use the Play Store version** — it is outdated and unsupported

---

## 2. Initial Termux Setup

Open Termux and run:

```bash
# Update package list
pkg update && pkg upgrade -y

# Install essential tools
pkg install -y git curl wget python nodejs openssh jq busybox

# Optional: prettier shell
pkg install -y zsh
```

---

## 3. Clone / Get CoreBuilderVX

```bash
# Clone from GitHub
git clone https://github.com/Cbetts1/CorebuilderVX
cd CorebuilderVX
```

---

## 4. Run the Installer

```bash
bash install.sh
```

This will:
- Detect your Termux environment
- Install required packages
- Install Python deps (flask, flask-cors) if pip available
- Detect and save your hardware profile
- Create a `cbx` symlink in `$PREFIX/bin`

---

## 5. Launch CoreBuilderVX

```bash
# Full path
./core.sh

# Or via symlink (if install.sh succeeded)
cbx

# Direct command examples
cbx build
cbx hardware
cbx ai
```

---

## 6. Termux-Specific Notes

### Storage access
If you want to save builds to shared storage:
```bash
termux-setup-storage
# Then use: CBX_BUILD_DIR=~/storage/shared/cbx-builds ./core.sh
```

### Running the Cockpit UI
```bash
# Start API (keep this running)
cbx menu → 9 → Start

# Start frontend server
cbx frontend
# Open in Android browser: http://127.0.0.1:8766/cockpit.html
```

### Persistent sessions
Use **tmux** to keep sessions alive when the screen turns off:
```bash
pkg install tmux
tmux new -s cbx
./core.sh
# Detach: Ctrl+B then D
# Reattach: tmux attach -t cbx
```

### VM mode in Termux
The Lite VM uses `proot` if available for better isolation:
```bash
pkg install proot
cbx vm
```

### AI in Termux
For best results, install **ollama**:
```bash
pkg install ollama
ollama pull llama3.2   # ~2GB, requires good storage
cbx ai
```
For very low RAM devices, use a tiny model:
```bash
ollama pull phi3:mini  # ~2.3GB
ollama pull tinyllama  # ~637MB
```

---

## 7. Troubleshooting

| Problem | Solution |
|---------|----------|
| `permission denied` on scripts | `find . -name "*.sh" -exec chmod +x {} \;` |
| `python3: not found` | `pkg install python` |
| `node: not found` | `pkg install nodejs` |
| `flask not found` | `pip install flask flask-cors` |
| `git: not found` | `pkg install git` |
| API won't start | Check `logs/api.log` |
| Colours broken | `export CBX_NO_COLOR=1` |
| UI not loading | Make sure API is running first |

---

## 8. Recommended Termux Packages

```bash
pkg install -y \
  git curl wget \
  python nodejs \
  jq busybox \
  tmux \
  proot \
  openssh \
  termux-api
```

Install `termux-api` companion app for battery/network detection:
- [F-Droid: Termux:API](https://f-droid.org/packages/com.termux.api/)
