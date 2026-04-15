#!/usr/bin/env bash
# =============================================================================
# CoreBuilderVX — Boot Simulator
# Simulates an OS boot sequence in the terminal (Termux-safe)
# =============================================================================

CBX_ROOT="${CBX_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
source "$CBX_ROOT/api/internal_api.sh"
[[ -f "$CBX_ROOT/config/hardware.conf" ]] && source "$CBX_ROOT/config/hardware.conf"

DELAY="${CBX_BOOTSIM_DELAY:-0.2}"
STEPS="${CBX_BOOTSIM_STEPS:-10}"

_boot_msg() {
    local level="$1"; shift
    printf "  [%s]  %s\n" "$level" "$*"
    sleep "$DELAY"
}

_ok()   { echo -e "  ${C_GREEN}[  OK  ]${C_NC}  $*"; sleep "$DELAY"; }
_fail() { echo -e "  ${C_RED}[FAILED]${C_NC}  $*"; sleep "$DELAY"; }
_info() { echo -e "  ${C_CYAN}[ INFO ]${C_NC}  $*"; sleep "$DELAY"; }

run_boot_simulator() {
    local build_target="${1:-}"

    clear
    cbx_header "Boot Simulator"

    if [[ -z "$build_target" ]]; then
        # Try to use latest build or simulate generic
        build_target="$(find "$CBX_BUILD_DIR" -mindepth 1 -maxdepth 1 -type d 2>/dev/null \
            | sort -r | head -1)"
    fi

    local build_name="generic-cbx"
    [[ -n "$build_target" ]] && build_name="$(basename "$build_target")"

    echo -e "\n${C_BOLD}  Simulating boot: $build_name${C_NC}"
    echo -e "  ${C_DIM}Device: ${CBX_HW_TIER:-?} | ${CBX_HW_RAM_MB:-?}MB RAM | ${CBX_HW_CPU_CORES:-?} cores${C_NC}"
    echo ""
    sleep 0.5

    # ---- Stage 1: BIOS/UEFI --------------------------------------------------
    echo -e "${C_DIM}"
    echo "  CoreBuilderVX BIOS v1.0.0"
    echo "  Checking memory... $(( ${CBX_HW_RAM_MB:-512} ))MB OK"
    echo "  CPU: ${CBX_HW_CPU_MODEL:-unknown}"
    echo "  Detecting boot device..."
    echo -e "${C_NC}"
    sleep "$DELAY"

    # ---- Stage 2: Bootloader -------------------------------------------------
    _info "Loading bootloader..."
    _ok   "GRUB/CBX-Boot stub loaded"
    _info "Reading kernel config..."
    _ok   "Kernel: cbx-1.0.0-${CBX_HW_ARCH:-aarch64}"

    # ---- Stage 3: Kernel init ------------------------------------------------
    echo ""
    _info "Kernel starting..."
    _ok   "Decompressing kernel image"
    _ok   "Initialising memory allocator"
    _ok   "CPU[0..$(( ${CBX_HW_CPU_CORES:-1} - 1 ))] online"
    _ok   "Mounting root filesystem"
    _ok   "Loading device drivers"

    # ---- Stage 4: Init/systemd stubs ----------------------------------------
    echo ""
    _info "Starting init system..."
    _ok   "sysfs mounted"
    _ok   "proc mounted"
    _ok   "tmpfs mounted"

    local services=(networking syslog cron sshd)
    for svc in "${services[@]}"; do
        _ok "Starting $svc service"
    done

    # ---- Stage 5: User space ------------------------------------------------
    echo ""
    _info "Bringing up user space..."
    _ok   "Loading CBX modules"
    _ok   "Hardware detection complete"
    _ok   "API engine ready (port ${CBX_API_PORT:-8765})"
    _ok   "Operator cockpit available"

    # ---- Done ----------------------------------------------------------------
    echo ""
    echo -e "  ${C_BOLD}${C_GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${C_NC}"
    echo -e "  ${C_BOLD}${C_GREEN}  CoreBuilderVX Boot Complete${C_NC}"
    echo -e "  ${C_BOLD}${C_GREEN}  $(date '+%Y-%m-%d %H:%M:%S')${C_NC}"
    echo -e "  ${C_BOLD}${C_GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${C_NC}"
    echo ""

    cbx_build_log "BOOTSIM" "Simulated boot: $build_name"
    cbx_pause
}

run_boot_simulator "$@"
