#!/usr/bin/env bash
# =============================================================================
# CoreBuilderVX — Lightweight VM Simulation
# Simulates a minimal VM using shell, namespaces (if available), or stubs
# Termux-safe: falls back gracefully without root or kernel namespaces
# =============================================================================

CBX_ROOT="${CBX_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
source "$CBX_ROOT/api/internal_api.sh"
[[ -f "$CBX_ROOT/config/hardware.conf" ]] && source "$CBX_ROOT/config/hardware.conf"

run_lite_vm() {
    cbx_header "Lightweight VM"
    echo ""

    # ---- VM settings --------------------------------------------------------
    local vm_name; vm_name="$(cbx_prompt "VM name" "cbx-vm-$(date +%H%M%S)")"
    local vm_ram="${CBX_VM_RAM:-256}"
    local vm_disk="${CBX_VM_DISK:-512}"
    local vm_arch="${CBX_HW_ARCH:-aarch64}"

    echo ""
    echo -e "  ${C_BOLD}VM Configuration:${C_NC}"
    echo -e "  Name : $vm_name"
    echo -e "  RAM  : ${vm_ram}MB"
    echo -e "  Disk : ${vm_disk}MB"
    echo -e "  Arch : $vm_arch"
    echo ""

    if ! cbx_confirm "Create and start VM?"; then
        cbx_info "Cancelled"
        cbx_pause
        return
    fi

    local vm_dir="$CBX_DATA_DIR/vms/$vm_name"
    mkdir -p "$vm_dir"/{root,proc,sys,dev,tmp,etc}

    # ---- Write VM config ----------------------------------------------------
    cat > "$vm_dir/vm.conf" <<EOF
VM_NAME="$vm_name"
VM_RAM="$vm_ram"
VM_DISK="$vm_disk"
VM_ARCH="$vm_arch"
VM_CREATED="$(date '+%Y-%m-%d %H:%M:%S')"
VM_STATUS="running"
EOF

    # ---- Detect virtualisation capabilities ---------------------------------
    local virt_mode="shell"
    if command -v unshare &>/dev/null && unshare --help 2>&1 | grep -q '\-\-pid'; then
        virt_mode="unshare"
    elif command -v proot &>/dev/null; then
        virt_mode="proot"
    fi

    cbx_info "Virtualisation mode: $virt_mode"
    echo ""

    # ---- Simulate VM boot ---------------------------------------------------
    cbx_step "Allocating virtual RAM: ${vm_ram}MB..."
    sleep 0.3
    cbx_ok  "RAM allocated"

    cbx_step "Initialising virtual disk: ${vm_disk}MB..."
    # Create a sparse disk image file
    if command -v dd &>/dev/null; then
        dd if=/dev/zero bs=1M count=1 2>/dev/null \
            | head -c $((vm_disk * 1024 * 1024)) > "$vm_dir/disk.img" 2>/dev/null || true
    fi
    cbx_ok  "Virtual disk ready"

    cbx_step "Mounting virtual filesystem..."
    sleep 0.2
    cbx_ok  "Filesystems mounted"

    # ---- Start VM shell (proot / unshare / plain) ---------------------------
    local vm_shell="$vm_dir/shell.sh"
    cat > "$vm_shell" <<EOF
#!/usr/bin/env bash
# CoreBuilderVX Lite VM Shell — $vm_name
export PS1="[${vm_name}]\\$ "
export VM_NAME="$vm_name"
export VM_ROOT="$vm_dir/root"
echo ""
echo "  CoreBuilderVX Lite VM — $vm_name"
echo "  RAM: ${vm_ram}MB  Disk: ${vm_disk}MB  Arch: $vm_arch"
echo "  Type 'exit' to stop the VM"
echo ""
\${SHELL:-/bin/sh}
EOF
    chmod +x "$vm_shell"

    echo ""
    cbx_ok "VM '$vm_name' started ($virt_mode mode)"
    echo ""

    case "$virt_mode" in
        unshare) unshare --fork --pid bash "$vm_shell" ;;
        proot)   proot -r "$vm_dir/root" bash "$vm_shell" ;;
        shell)   bash "$vm_shell" ;;
    esac

    # ---- VM stopped ---------------------------------------------------------
    echo ""
    cbx_info "VM '$vm_name' stopped"
    sed -i 's/VM_STATUS="running"/VM_STATUS="stopped"/' "$vm_dir/vm.conf" 2>/dev/null || true
    cbx_build_log "VM" "Stopped: $vm_name mode=$virt_mode"
    cbx_pause
}

run_lite_vm "$@"
