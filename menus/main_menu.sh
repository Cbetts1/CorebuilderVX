#!/usr/bin/env bash
# =============================================================================
# CoreBuilderVX — Main Menu
# =============================================================================

CBX_ROOT="${CBX_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
source "$CBX_ROOT/api/internal_api.sh"
source "$CBX_ROOT/config/default.conf" 2>/dev/null || true
[[ -f "$CBX_ROOT/config/hardware.conf" ]] && source "$CBX_ROOT/config/hardware.conf"

# ---- Menu renderer -----------------------------------------------------------
_render_menu() {
    clear
    cbx_banner "v${CBX_VERSION:-1.0.0}  |  Tier: ${CBX_HW_TIER:-?}  |  Env: ${CBX_HW_ENV:-?}"
    echo -e "${C_BOLD}  MAIN MENU${C_NC}"
    echo ""
    echo -e "  ${C_CYAN}1${C_NC}  OS Builder          — Construct OS layers & blueprints"
    echo -e "  ${C_CYAN}2${C_NC}  OS Tester           — Integrity, service & boot tests"
    echo -e "  ${C_CYAN}3${C_NC}  Boot Simulator      — Simulate OS boot sequence"
    echo -e "  ${C_CYAN}4${C_NC}  Vcloud Builder      — Virtual cloud environments"
    echo -e "  ${C_CYAN}5${C_NC}  Lightweight VM      — Spin up local VM simulation"
    echo -e "  ${C_CYAN}6${C_NC}  Local AI Runner     — Run small AI models locally"
    echo -e "  ${C_CYAN}7${C_NC}  Operator Cockpit    — Launch frontend UI"
    echo -e "  ${C_CYAN}8${C_NC}  Hardware Profile    — View/refresh hardware info"
    echo -e "  ${C_CYAN}9${C_NC}  Backend API         — Start/stop API engine"
    echo -e "  ${C_CYAN}S${C_NC}  Website Builder     — Build & preview websites"
    echo -e "  ${C_CYAN}U${C_NC}  Self-Upgrade        — Update CoreBuilderVX"
    echo -e "  ${C_CYAN}W${C_NC}  Setup Wizard        — First-time configuration"
    echo -e "  ${C_CYAN}Q${C_NC}  Quit"
    echo ""

    # Status line
    local hw_tier="${CBX_HW_TIER:-unknown}"
    local hw_ram="${CBX_HW_RAM_MB:-?} MB RAM"
    local hw_cores="${CBX_HW_CPU_CORES:-?} cores"
    echo -e "  ${C_DIM}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${C_NC}"
    echo -e "  ${C_DIM}HW: ${hw_tier} | ${hw_ram} | ${hw_cores} | $(date '+%H:%M')${C_NC}"
    echo ""
}

# ---- Main loop ---------------------------------------------------------------
main_menu() {
    while true; do
        _render_menu
        read -r -p "$(echo -e "  ${C_BOLD}Select option:${C_NC} ")" choice

        case "${choice,,}" in
            1) source "$CBX_ROOT/menus/wizards/build_wizard.sh"     ;;
            2) source "$CBX_ROOT/modules/os_tester/integrity.sh"    ;;
            3) source "$CBX_ROOT/modules/boot_sim/simulate.sh"      ;;
            4) source "$CBX_ROOT/modules/vcloud/build.sh"           ;;
            5) source "$CBX_ROOT/modules/vm/lite_vm.sh"             ;;
            6) source "$CBX_ROOT/modules/ai_runner/local_ai.sh"     ;;
            7) source "$CBX_ROOT/modules/frontend/serve.sh"         ;;
            8)
                "$CBX_ROOT/modules/hardware/detect.sh"
                cbx_pause
                ;;
            9) source "$CBX_ROOT/modules/backend/api_manager.sh"    ;;
            s) source "$CBX_ROOT/modules/site_builder/website_builder.sh" ;;
            u) source "$CBX_ROOT/modules/updater/self_upgrade.sh"   ;;
            w) source "$CBX_ROOT/menus/wizards/setup_wizard.sh"     ;;
            q|quit|exit)
                echo -e "\n${C_CYAN}Goodbye.${C_NC}\n"
                exit 0
                ;;
            *)
                cbx_warn "Unknown option: $choice"
                sleep 1
                ;;
        esac
    done
}

main_menu
