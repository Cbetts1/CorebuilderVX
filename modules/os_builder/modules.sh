#!/usr/bin/env bash
# =============================================================================
# CoreBuilderVX — OS Builder: Module Loader
# Installs selected modules into the build directory
# =============================================================================

CBX_ROOT="${CBX_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
source "$CBX_ROOT/api/internal_api.sh" 2>/dev/null || true

# ---- Module definitions (plug-and-play) -------------------------------------
module_base() {
    local dir="$1"
    cbx_step "Module: base"
    # Minimal shell tools stubs
    for cmd in sh ash bash ls cat echo grep sed awk; do
        echo "#!/bin/sh" > "$dir/bin/$cmd.stub"
    done
    cbx_ok "base: shell stubs created"
}

module_networking() {
    local dir="$1"
    cbx_step "Module: networking"
    cat > "$dir/etc/network/interfaces" <<'EOF'
# CoreBuilderVX network interfaces stub
auto lo
iface lo inet loopback
EOF
    cat > "$dir/etc/resolv.conf" <<'EOF'
nameserver 1.1.1.1
nameserver 8.8.8.8
EOF
    cbx_ok "networking: config files written"
}

module_filesystem() {
    local dir="$1"
    cbx_step "Module: filesystem"
    cat > "$dir/etc/fstab.extra" <<'EOF'
# Extended fstab entries for filesystem module
tmpfs   /dev/shm    tmpfs   defaults    0 0
devpts  /dev/pts    devpts  defaults    0 0
EOF
    cbx_ok "filesystem: fstab extended"
}

module_services() {
    local dir="$1"
    cbx_step "Module: services"
    mkdir -p "$dir/etc/init.d"
    for svc in sshd cron syslog; do
        cat > "$dir/etc/init.d/$svc" <<EOF
#!/bin/sh
# $svc service stub — CoreBuilderVX
case "\$1" in
    start)   echo "Starting $svc..." ;;
    stop)    echo "Stopping $svc..." ;;
    restart) \$0 stop; \$0 start    ;;
    status)  echo "$svc status: stub" ;;
esac
EOF
        chmod +x "$dir/etc/init.d/$svc"
    done
    cbx_ok "services: sshd, cron, syslog stubs"
}

module_ui() {
    local dir="$1"
    cbx_step "Module: ui"
    mkdir -p "$dir/usr/share/cbx-ui"
    cp "$CBX_ROOT/modules/frontend/cockpit.html" "$dir/usr/share/cbx-ui/" 2>/dev/null \
        || echo "<!-- CBX UI placeholder -->" > "$dir/usr/share/cbx-ui/cockpit.html"
    cbx_ok "ui: cockpit installed"
}

module_ai() {
    local dir="$1"
    cbx_step "Module: ai"
    mkdir -p "$dir/opt/cbx-ai"
    cp "$CBX_ROOT/modules/ai_runner/local_ai.sh" "$dir/opt/cbx-ai/" 2>/dev/null \
        || echo "# AI runner placeholder" > "$dir/opt/cbx-ai/local_ai.sh"
    cbx_ok "ai: runner stub installed"
}

module_vm() {
    local dir="$1"
    cbx_step "Module: vm"
    mkdir -p "$dir/opt/cbx-vm"
    cp "$CBX_ROOT/modules/vm/lite_vm.sh" "$dir/opt/cbx-vm/" 2>/dev/null \
        || echo "# VM placeholder" > "$dir/opt/cbx-vm/lite_vm.sh"
    cbx_ok "vm: lite_vm installed"
}

module_vcloud() {
    local dir="$1"
    cbx_step "Module: vcloud"
    mkdir -p "$dir/opt/cbx-vcloud"
    cp "$CBX_ROOT/modules/vcloud/build.sh" "$dir/opt/cbx-vcloud/" 2>/dev/null \
        || echo "# Vcloud placeholder" > "$dir/opt/cbx-vcloud/build.sh"
    cbx_ok "vcloud: builder installed"
}

# ---- Main -------------------------------------------------------------------
run_modules() {
    local build_dir="${1:?build_dir required}"
    local modules_str="${2:-base networking filesystem}"

    cbx_step "Loading modules: $modules_str"
    echo ""

    for mod in $modules_str; do
        if declare -f "module_${mod}" > /dev/null 2>&1; then
            "module_${mod}" "$build_dir"
        else
            cbx_warn "Unknown module: $mod (skipped)"
        fi
    done

    cbx_ok "All modules loaded"
}

run_modules "$@"
