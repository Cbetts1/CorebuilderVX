#!/usr/bin/env bash
# =============================================================================
# CoreBuilderVX — OS Builder: Blueprint
# Orchestrates the OS skeleton build pipeline
# =============================================================================

CBX_ROOT="${CBX_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
source "$CBX_ROOT/api/internal_api.sh"
[[ -f "$CBX_ROOT/config/hardware.conf" ]] && source "$CBX_ROOT/config/hardware.conf"

run_os_builder() {
    local build_type="${CBX_OS_TYPE:-minimal}"
    local arch="${CBX_OS_ARCH:-$(uname -m)}"
    local build_name="${CBX_BUILD_NAME:-cbx-build-$(date +%Y%m%d-%H%M%S)}"
    local build_dir="$CBX_BUILD_DIR/$build_name"
    local modules="${CBX_BUILD_MODULES:-base networking filesystem}"

    cbx_header "OS Builder — Blueprint"
    cbx_info "Build: $build_name | Type: $build_type | Arch: $arch"

    # Disk check
    local min_mb=50
    [[ "$build_type" == "full" ]] && min_mb=200
    cbx_check_disk "$min_mb" || { cbx_warn "Continuing anyway..."; }

    mkdir -p "$build_dir"
    cbx_build_log "BUILDER" "Started: $build_name type=$build_type arch=$arch"

    # ---- Run skeleton -------------------------------------------------------
    source "$CBX_ROOT/modules/os_builder/skeleton.sh" "$build_dir"

    # ---- Load modules -------------------------------------------------------
    source "$CBX_ROOT/modules/os_builder/modules.sh" "$build_dir" "$modules"

    # ---- Write manifest -----------------------------------------------------
    cat > "$build_dir/manifest.json" <<EOF
{
  "name": "$build_name",
  "type": "$build_type",
  "arch": "$arch",
  "modules": "$(echo $modules | tr ' ' ',')",
  "built_by": "CoreBuilderVX v${CBX_VERSION:-1.0.0}",
  "built_at": "$(date -u '+%Y-%m-%dT%H:%M:%SZ')",
  "hw_tier": "${CBX_HW_TIER:-unknown}",
  "status": "complete"
}
EOF

    cbx_build_log "BUILDER" "Completed: $build_name → $build_dir"
    echo ""
    cbx_ok "Build complete: $build_dir"
    echo -e "  ${C_DIM}Manifest: $build_dir/manifest.json${C_NC}"
    echo ""
    cbx_pause
}

run_os_builder "$@"
