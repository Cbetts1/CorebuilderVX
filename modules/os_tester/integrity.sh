#!/usr/bin/env bash
# =============================================================================
# CoreBuilderVX — OS Tester: Integrity Check
# Validates build output structure, files, and checksums
# =============================================================================

CBX_ROOT="${CBX_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
source "$CBX_ROOT/api/internal_api.sh"
[[ -f "$CBX_ROOT/config/hardware.conf" ]] && source "$CBX_ROOT/config/hardware.conf"

run_integrity() {
    local target="${1:-}"
    local pass=0 fail=0

    cbx_header "OS Tester — Integrity Check"

    # ---- Select build to test -----------------------------------------------
    if [[ -z "$target" ]]; then
        local builds=()
        while IFS= read -r d; do
            builds+=("$d")
        done < <(find "$CBX_BUILD_DIR" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | sort -r)

        if [[ ${#builds[@]} -eq 0 ]]; then
            cbx_warn "No builds found in $CBX_BUILD_DIR"
            cbx_info "Run the OS Builder first (menu option 1)"
            cbx_pause
            return
        fi

        echo -e "  Available builds:"
        local i=1
        for b in "${builds[@]}"; do
            echo -e "  ${C_CYAN}$i${C_NC}  $(basename "$b")"
            i=$(( i + 1 ))
        done
        echo ""
        read -r -p "  Select build [1]: " sel
        local idx=$(( ${sel:-1} - 1 ))
        target="${builds[$idx]}"
    fi

    cbx_info "Testing: $(basename "$target")"
    echo ""

    # ---- Required directory checks ------------------------------------------
    local required_dirs=(boot bin sbin etc var tmp)
    cbx_step "Directory structure:"
    for dir in "${required_dirs[@]}"; do
        if [[ -d "$target/$dir" ]]; then
            cbx_ok "  $dir/"
            pass=$(( pass + 1 ))
        else
            cbx_fail "  $dir/ MISSING"
            fail=$(( fail + 1 ))
        fi
    done

    # ---- Required file checks -----------------------------------------------
    local required_files=(etc/os-release etc/fstab boot/version)
    cbx_step "Required files:"
    for f in "${required_files[@]}"; do
        if [[ -f "$target/$f" ]]; then
            cbx_ok "  $f"
            pass=$(( pass + 1 ))
        else
            cbx_fail "  $f MISSING"
            fail=$(( fail + 1 ))
        fi
    done

    # ---- Manifest check -----------------------------------------------------
    cbx_step "Manifest:"
    if [[ -f "$target/manifest.json" ]]; then
        cbx_ok "  manifest.json present"
        if command -v jq &>/dev/null; then
            local status
            status="$(jq -r '.status' "$target/manifest.json" 2>/dev/null || echo 'unknown')"
            [[ "$status" == "complete" ]] && cbx_ok "  status: $status" || cbx_fail "  status: $status"
        fi
        pass=$(( pass + 1 ))
    else
        cbx_fail "  manifest.json MISSING"
        fail=$(( fail + 1 ))
    fi

    # ---- Init script check --------------------------------------------------
    cbx_step "Init scripts:"
    if [[ -f "$target/etc/init.d/rc.local" && -x "$target/etc/init.d/rc.local" ]]; then
        cbx_ok "  rc.local present and executable"
        pass=$(( pass + 1 ))
    else
        cbx_fail "  rc.local missing or not executable"
        fail=$(( fail + 1 ))
    fi

    # ---- Summary ------------------------------------------------------------
    echo ""
    cbx_header "Test Results"
    echo -e "  ${C_GREEN}PASS: $pass${C_NC}   ${C_RED}FAIL: $fail${C_NC}"
    echo ""
    if [[ $fail -eq 0 ]]; then
        cbx_ok "All integrity checks passed"
    else
        cbx_warn "$fail check(s) failed — review build output"
    fi

    # Log results
    cbx_build_log "TESTER" "Integrity: build=$(basename "$target") pass=$pass fail=$fail"

    echo ""
    cbx_pause
}

# Also run service and boot tests if invoked with sub-commands
case "${1:-integrity}" in
    service) source "$CBX_ROOT/modules/os_tester/services.sh" "${@:2}" ;;
    boot)    source "$CBX_ROOT/modules/os_tester/boot_test.sh" "${@:2}" ;;
    all)
        run_integrity "${2:-}"
        source "$CBX_ROOT/modules/os_tester/services.sh" "${2:-}"
        source "$CBX_ROOT/modules/os_tester/boot_test.sh" "${2:-}"
        ;;
    *)       run_integrity "${@}" ;;
esac
