#!/usr/bin/env bash
# =============================================================================
# CoreBuilderVX — OS Tester: Boot Test
# Validates the boot sequence simulation of a build
# =============================================================================

CBX_ROOT="${CBX_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
source "$CBX_ROOT/api/internal_api.sh"

run_boot_test() {
    local target="${1:-}"
    local pass=0 fail=0

    cbx_header "OS Tester — Boot Test"

    if [[ -z "$target" ]]; then
        target="$(find "$CBX_BUILD_DIR" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | sort -r | head -1)"
        [[ -z "$target" ]] && { cbx_warn "No builds found"; cbx_pause; return; }
    fi

    cbx_info "Boot-testing: $(basename "$target")"
    echo ""

    # ---- Stage 1: BIOS/bootloader stub check --------------------------------
    cbx_step "Stage 1 — Bootloader check"
    if [[ -f "$target/boot/version" ]]; then
        local ver; ver="$(cat "$target/boot/version" 2>/dev/null)"
        cbx_ok "  Boot version: $ver"
        pass=$(( pass + 1 ))
    else
        cbx_fail "  boot/version missing"
        fail=$(( fail + 1 ))
    fi

    # ---- Stage 2: Init system check -----------------------------------------
    cbx_step "Stage 2 — Init system"
    if [[ -f "$target/etc/init.d/rc.local" ]]; then
        cbx_ok "  rc.local found"
        # Dry-run syntax check
        if bash -n "$target/etc/init.d/rc.local" 2>/dev/null; then
            cbx_ok "  rc.local syntax OK"
            pass=$(( pass + 1 ))
        else
            cbx_fail "  rc.local has syntax errors"
            fail=$(( fail + 1 ))
        fi
    else
        cbx_fail "  rc.local missing"
        fail=$(( fail + 1 ))
    fi

    # ---- Stage 3: OS release check ------------------------------------------
    cbx_step "Stage 3 — OS identity"
    if [[ -f "$target/etc/os-release" ]]; then
        local os_name; os_name="$(grep PRETTY_NAME "$target/etc/os-release" | cut -d'"' -f2)"
        cbx_ok "  OS: $os_name"
        pass=$(( pass + 1 ))
    else
        cbx_fail "  /etc/os-release missing"
        fail=$(( fail + 1 ))
    fi

    # ---- Stage 4: Filesystem mount points -----------------------------------
    cbx_step "Stage 4 — Filesystem mounts"
    for mp in proc sys tmp; do
        if [[ -d "$target/$mp" ]]; then
            cbx_ok "  /$mp present"
            pass=$(( pass + 1 ))
        else
            cbx_fail "  /$mp missing"
            fail=$(( fail + 1 ))
        fi
    done

    # ---- Summary ------------------------------------------------------------
    echo ""
    cbx_header "Boot Test Results"
    echo -e "  ${C_GREEN}PASS: $pass${C_NC}   ${C_RED}FAIL: $fail${C_NC}"
    if [[ $fail -eq 0 ]]; then
        cbx_ok "Boot test PASSED"
    else
        cbx_warn "Boot test has $fail failure(s)"
    fi

    cbx_build_log "TESTER" "Boot: build=$(basename "$target") pass=$pass fail=$fail"
    echo ""
    cbx_pause
}

run_boot_test "$@"
