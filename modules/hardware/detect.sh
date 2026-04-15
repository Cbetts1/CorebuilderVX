#!/usr/bin/env bash
# =============================================================================
# CoreBuilderVX — Hardware Detection Module
# Detects CPU, RAM, disk, OS, environment, display, battery, network
# Safe in Termux — uses only POSIX-compatible commands
# =============================================================================
set -euo pipefail

CBX_ROOT="${CBX_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
source "$CBX_ROOT/api/internal_api.sh" 2>/dev/null || true

SAVE_PROFILE=0
[[ "${1:-}" == "--save" ]] && SAVE_PROFILE=1

# ---- Helpers -----------------------------------------------------------------
_read_first() { head -n1 "$1" 2>/dev/null || echo "unknown"; }
_cmd()        { command -v "$1" &>/dev/null; }

# ---- Architecture ------------------------------------------------------------
detect_arch() {
    local arch
    arch="$(uname -m 2>/dev/null || echo unknown)"
    case "$arch" in
        aarch64|arm64)  echo "aarch64" ;;
        armv7*)         echo "armv7"   ;;
        x86_64|amd64)  echo "x86_64"  ;;
        i*86)           echo "x86"     ;;
        *)              echo "$arch"   ;;
    esac
}

# ---- CPU ---------------------------------------------------------------------
detect_cpu_cores() {
    nproc 2>/dev/null \
        || grep -c '^processor' /proc/cpuinfo 2>/dev/null \
        || sysctl -n hw.ncpu 2>/dev/null \
        || echo "1"
}

detect_cpu_model() {
    if [[ -f /proc/cpuinfo ]]; then
        grep -m1 'model name\|Hardware\|Processor' /proc/cpuinfo \
            | sed 's/.*: //' | tr -s ' ' || echo "unknown"
    elif _cmd sysctl; then
        sysctl -n machdep.cpu.brand_string 2>/dev/null || echo "unknown"
    else
        echo "unknown"
    fi
}

# ---- RAM ---------------------------------------------------------------------
detect_ram_mb() {
    if [[ -f /proc/meminfo ]]; then
        awk '/MemTotal/{printf "%d", $2/1024}' /proc/meminfo
    elif _cmd sysctl; then
        sysctl -n hw.memsize 2>/dev/null | awk '{printf "%d", $1/1048576}' \
            || echo "0"
    else
        echo "0"
    fi
}

# ---- Disk free ---------------------------------------------------------------
detect_disk_free_mb() {
    df -m "$CBX_ROOT" 2>/dev/null \
        | awk 'NR==2{print $4}' \
        || echo "0"
}

# ---- OS & Kernel -------------------------------------------------------------
detect_os() {
    if [[ -f /etc/os-release ]]; then
        grep '^PRETTY_NAME' /etc/os-release | cut -d'"' -f2
    elif [[ "$(uname)" == "Darwin" ]]; then
        sw_vers -productVersion 2>/dev/null | awk '{print "macOS "$1}'
    else
        uname -s 2>/dev/null || echo "unknown"
    fi
}

detect_kernel() {
    uname -r 2>/dev/null || echo "unknown"
}

# ---- Environment type --------------------------------------------------------
detect_env() {
    if [[ -d /data/data/com.termux ]]; then
        echo "termux"
    elif grep -qi microsoft /proc/version 2>/dev/null; then
        echo "wsl"
    elif [[ "$(uname)" == "Darwin" ]]; then
        echo "macos"
    elif [[ -f /proc/1/cgroup ]] && grep -q docker /proc/1/cgroup 2>/dev/null; then
        echo "docker"
    else
        echo "linux"
    fi
}

# ---- Display -----------------------------------------------------------------
detect_display() {
    if [[ -n "${DISPLAY:-}" ]]; then
        echo "x11"
    elif [[ -n "${WAYLAND_DISPLAY:-}" ]]; then
        echo "wayland"
    elif _cmd termux-info 2>/dev/null; then
        echo "termux-x11"
    else
        echo "none"
    fi
}

# ---- GPU (basic) -------------------------------------------------------------
detect_gpu() {
    if _cmd lspci; then
        lspci 2>/dev/null | grep -i 'vga\|3d\|display' | head -1 \
            | sed 's/.*: //' | cut -c1-40 || echo "none"
    elif [[ -f /proc/cpuinfo ]]; then
        grep -i 'gpu\|graphics' /proc/cpuinfo 2>/dev/null | head -1 \
            | sed 's/.*: //' || echo "none"
    else
        echo "none"
    fi
}

# ---- Battery (Termux / Linux) ------------------------------------------------
detect_battery() {
    # Termux
    if _cmd termux-battery-status; then
        local status
        status="$(termux-battery-status 2>/dev/null | grep -o '"status": "[^"]*"' \
            | cut -d'"' -f4 | tr '[:upper:]' '[:lower:]')" 2>/dev/null || true
        [[ -n "$status" ]] && echo "$status" && return
    fi
    # Linux sysfs
    local bat
    bat="$(ls /sys/class/power_supply/BAT*/status 2>/dev/null | head -1)"
    if [[ -n "$bat" ]]; then
        cat "$bat" 2>/dev/null | tr '[:upper:]' '[:lower:]' || echo "unknown"
    else
        echo "unknown"
    fi
}

# ---- Network -----------------------------------------------------------------
detect_network() {
    if _cmd ip; then
        ip route 2>/dev/null | grep -q 'default' && echo "connected" || echo "none"
    elif _cmd ifconfig; then
        ifconfig 2>/dev/null | grep -q 'inet ' && echo "connected" || echo "none"
    else
        echo "unknown"
    fi
}

# ---- Tier (phone / rpi / laptop / desktop / server) -------------------------
detect_tier() {
    local ram_mb="$1" env="$2" cores="$3"
    if [[ "$env" == "termux" ]]; then
        echo "phone"
    elif [[ "$ram_mb" -le 1024 && "$cores" -le 4 ]]; then
        echo "rpi"
    elif [[ "$ram_mb" -le 8192 && "$cores" -le 8 ]]; then
        echo "laptop"
    elif [[ "$ram_mb" -gt 8192 && "$cores" -gt 8 ]]; then
        echo "server"
    else
        echo "desktop"
    fi
}

# ---- Apply adaptive tuning based on tier ------------------------------------
apply_tuning() {
    local tier="$1" ram_mb="$2"
    case "$tier" in
        phone|rpi)
            CBX_VM_RAM="128"
            CBX_VM_DISK="256"
            CBX_AI_MAX_TOKENS="64"
            CBX_BOOTSIM_DELAY="0.5"
            ;;
        laptop)
            CBX_VM_RAM="512"
            CBX_VM_DISK="1024"
            CBX_AI_MAX_TOKENS="256"
            CBX_BOOTSIM_DELAY="0.1"
            ;;
        desktop|server)
            CBX_VM_RAM="2048"
            CBX_VM_DISK="4096"
            CBX_AI_MAX_TOKENS="512"
            CBX_BOOTSIM_DELAY="0.05"
            ;;
    esac
}

# ---- Main detection ----------------------------------------------------------
main() {
    local arch cpu_cores cpu_model ram_mb disk_free_mb os kernel env \
          display gpu battery network tier

    arch="$(detect_arch)"
    cpu_cores="$(detect_cpu_cores)"
    cpu_model="$(detect_cpu_model)"
    ram_mb="$(detect_ram_mb)"
    disk_free_mb="$(detect_disk_free_mb)"
    os="$(detect_os)"
    kernel="$(detect_kernel)"
    env="$(detect_env)"
    display="$(detect_display)"
    gpu="$(detect_gpu)"
    battery="$(detect_battery)"
    network="$(detect_network)"
    tier="$(detect_tier "$ram_mb" "$env" "$cpu_cores")"

    apply_tuning "$tier" "$ram_mb"

    if [[ "$SAVE_PROFILE" -eq 1 ]]; then
        cat > "$CBX_ROOT/config/hardware.conf" <<EOF
# CoreBuilderVX Hardware Profile
# Auto-generated $(date '+%Y-%m-%d %H:%M:%S')
CBX_HW_ARCH="$arch"
CBX_HW_CPU_CORES="$cpu_cores"
CBX_HW_CPU_MODEL="$cpu_model"
CBX_HW_RAM_MB="$ram_mb"
CBX_HW_DISK_FREE_MB="$disk_free_mb"
CBX_HW_OS="$os"
CBX_HW_KERNEL="$kernel"
CBX_HW_ENV="$env"
CBX_HW_DISPLAY="$display"
CBX_HW_GPU="$gpu"
CBX_HW_BATTERY="$battery"
CBX_HW_NETWORK="$network"
CBX_HW_TIER="$tier"
CBX_HW_PROFILE_DATE="$(date '+%Y-%m-%d %H:%M:%S')"

# Adaptive tuning (auto-set by tier: $tier)
CBX_VM_RAM="${CBX_VM_RAM:-256}"
CBX_VM_DISK="${CBX_VM_DISK:-512}"
CBX_AI_MAX_TOKENS="${CBX_AI_MAX_TOKENS:-128}"
CBX_BOOTSIM_DELAY="${CBX_BOOTSIM_DELAY:-0.2}"
EOF
        echo "[CBX] Hardware profile saved → config/hardware.conf"
    else
        # Pretty print
        echo ""
        echo "╔══════════════════════════════════════╗"
        echo "║      CoreBuilderVX Hardware Profile  ║"
        echo "╠══════════════════════════════════════╣"
        printf "║  %-12s : %-21s ║\n" "Arch"      "$arch"
        printf "║  %-12s : %-21s ║\n" "CPU Cores"  "$cpu_cores"
        printf "║  %-12s : %-21s ║\n" "CPU Model"  "$(echo "$cpu_model" | cut -c1-21)"
        printf "║  %-12s : %-21s ║\n" "RAM"        "${ram_mb} MB"
        printf "║  %-12s : %-21s ║\n" "Disk Free"  "${disk_free_mb} MB"
        printf "║  %-12s : %-21s ║\n" "OS"         "$(echo "$os" | cut -c1-21)"
        printf "║  %-12s : %-21s ║\n" "Kernel"     "$(echo "$kernel" | cut -c1-21)"
        printf "║  %-12s : %-21s ║\n" "Env"        "$env"
        printf "║  %-12s : %-21s ║\n" "Display"    "$display"
        printf "║  %-12s : %-21s ║\n" "Battery"    "$battery"
        printf "║  %-12s : %-21s ║\n" "Network"    "$network"
        printf "║  %-12s : %-21s ║\n" "Tier"       "$tier"
        echo "╚══════════════════════════════════════╝"
    fi
}

main "$@"
