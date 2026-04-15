#!/usr/bin/env bash
# =============================================================================
# CoreBuilderVX — Build Wizard
# Interactive wizard for OS/project build configuration
# =============================================================================

CBX_ROOT="${CBX_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
source "$CBX_ROOT/api/internal_api.sh"
[[ -f "$CBX_ROOT/config/hardware.conf" ]] && source "$CBX_ROOT/config/hardware.conf"

build_wizard() {
    clear
    cbx_banner "Build Wizard"
    cbx_header "OS / Project Builder"
    echo ""

    # ---- Choose build type --------------------------------------------------
    cbx_step "Step 1 — Build Type"
    echo -e "  ${C_CYAN}1${C_NC}  Minimal OS skeleton    (fastest, ~10MB)"
    echo -e "  ${C_CYAN}2${C_NC}  Standard OS build      (balanced, ~50MB)"
    echo -e "  ${C_CYAN}3${C_NC}  Full OS build          (all modules, ~200MB)"
    echo -e "  ${C_CYAN}4${C_NC}  Custom blueprint"
    echo ""
    read -r -p "  Select [1]: " type_choice
    case "${type_choice:-1}" in
        2) BUILD_TYPE="standard"  ;;
        3) BUILD_TYPE="full"      ;;
        4) BUILD_TYPE="custom"    ;;
        *) BUILD_TYPE="minimal"   ;;
    esac
    cbx_ok "Build type: $BUILD_TYPE"
    echo ""

    # ---- Target architecture ------------------------------------------------
    cbx_step "Step 2 — Target Architecture"
    local current_arch="${CBX_HW_ARCH:-auto}"
    echo -e "  ${C_CYAN}1${C_NC}  Auto (current: $current_arch)"
    echo -e "  ${C_CYAN}2${C_NC}  aarch64 (ARM 64-bit)"
    echo -e "  ${C_CYAN}3${C_NC}  x86_64  (Intel/AMD 64-bit)"
    echo -e "  ${C_CYAN}4${C_NC}  armv7   (ARM 32-bit)"
    echo ""
    read -r -p "  Select [1]: " arch_choice
    case "${arch_choice:-1}" in
        2) TARGET_ARCH="aarch64" ;;
        3) TARGET_ARCH="x86_64"  ;;
        4) TARGET_ARCH="armv7"   ;;
        *) TARGET_ARCH="$current_arch" ;;
    esac
    cbx_ok "Target arch: $TARGET_ARCH"
    echo ""

    # ---- Build name ---------------------------------------------------------
    cbx_step "Step 3 — Build Name"
    local build_name
    build_name="$(cbx_prompt "Build name" "cbx-build-$(date +%Y%m%d)")"
    echo ""

    # ---- Module selection (full/custom) ------------------------------------
    local selected_modules="base networking filesystem"
    if [[ "$BUILD_TYPE" == "custom" ]]; then
        cbx_step "Step 4 — Select Modules"
        echo -e "  Available modules (space-separated selection):"
        echo -e "  ${C_DIM}base networking filesystem services ui ai vm vcloud${C_NC}"
        read -r -p "  Modules [base networking filesystem]: " mod_input
        selected_modules="${mod_input:-base networking filesystem}"
    fi

    # ---- Confirm and build --------------------------------------------------
    echo ""
    cbx_header "Build Summary"
    echo -e "  Name     : ${C_BOLD}$build_name${C_NC}"
    echo -e "  Type     : ${C_BOLD}$BUILD_TYPE${C_NC}"
    echo -e "  Arch     : ${C_BOLD}$TARGET_ARCH${C_NC}"
    echo -e "  Modules  : ${C_BOLD}$selected_modules${C_NC}"
    echo ""

    if cbx_confirm "Start build now?"; then
        export CBX_OS_TYPE="$BUILD_TYPE"
        export CBX_OS_ARCH="$TARGET_ARCH"
        export CBX_BUILD_NAME="$build_name"
        export CBX_BUILD_MODULES="$selected_modules"
        source "$CBX_ROOT/modules/os_builder/blueprint.sh"
    else
        cbx_info "Build cancelled."
        cbx_pause
    fi
}

build_wizard
