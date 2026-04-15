#!/usr/bin/env bash
# =============================================================================
# CoreBuilderVX — OS Tester: Service Tests
# Tests init scripts and service stubs in a build
# =============================================================================

CBX_ROOT="${CBX_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
source "$CBX_ROOT/api/internal_api.sh"

run_service_tests() {
    local target="${1:-}"
    local pass=0 fail=0

    cbx_header "OS Tester — Service Tests"

    if [[ -z "$target" ]]; then
        cbx_warn "No build target specified — checking latest build"
        target="$(find "$CBX_BUILD_DIR" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | sort -r | head -1)"
        [[ -z "$target" ]] && { cbx_warn "No builds found"; cbx_pause; return; }
    fi

    cbx_info "Testing services in: $(basename "$target")"
    echo ""

    local init_dir="$target/etc/init.d"
    if [[ ! -d "$init_dir" ]]; then
        cbx_fail "init.d directory not found"
        cbx_pause
        return
    fi

    local services=()
    while IFS= read -r svc; do
        services+=("$svc")
    done < <(find "$init_dir" -type f -executable 2>/dev/null)

    if [[ ${#services[@]} -eq 0 ]]; then
        cbx_warn "No executable service scripts found"
        cbx_pause
        return
    fi

    for svc in "${services[@]}"; do
        local svc_name; svc_name="$(basename "$svc")"
        cbx_step "Testing service: $svc_name"

        # Check file exists and is executable
        if [[ -x "$svc" ]]; then
            cbx_ok "  $svc_name: executable ✓"
            pass=$(( pass + 1 ))
        else
            cbx_fail "  $svc_name: not executable"
            fail=$(( fail + 1 ))
        fi

        # Check the script has required case arms
        if grep -q 'start\|stop\|status' "$svc" 2>/dev/null; then
            cbx_ok "  $svc_name: has start/stop/status handlers"
            pass=$(( pass + 1 ))
        else
            cbx_warn "  $svc_name: missing service control handlers"
        fi
    done

    echo ""
    echo -e "  ${C_GREEN}PASS: $pass${C_NC}   ${C_RED}FAIL: $fail${C_NC}"
    cbx_build_log "TESTER" "Services: build=$(basename "$target") pass=$pass fail=$fail"
    echo ""
    cbx_pause
}

run_service_tests "$@"
