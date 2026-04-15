#!/usr/bin/env bash
# =============================================================================
# CoreBuilderVX — OS Builder: Skeleton
# Creates base directory structure and init scripts for a build
# =============================================================================

CBX_ROOT="${CBX_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
source "$CBX_ROOT/api/internal_api.sh" 2>/dev/null || true

run_skeleton() {
    local build_dir="${1:?build_dir required}"

    cbx_step "Building directory skeleton..."

    local dirs=(
        boot bin sbin lib lib64 usr/bin usr/sbin usr/lib usr/local/bin
        etc etc/init.d etc/conf.d etc/network
        var/log var/run var/tmp
        tmp home root
        proc sys dev mnt media
        srv opt
    )

    local total="${#dirs[@]}"
    local i=0

    for dir in "${dirs[@]}"; do
        mkdir -p "$build_dir/$dir"
        i=$(( i + 1 ))
        cbx_progress "$i" "$total" "$dir"
    done

    # ---- Minimal init script ------------------------------------------------
    cat > "$build_dir/etc/init.d/rc.local" <<'INITEOF'
#!/bin/sh
# CoreBuilderVX minimal init stub
echo "[INIT] CoreBuilderVX boot sequence"
echo "[INIT] Loading services..."
exit 0
INITEOF
    chmod +x "$build_dir/etc/init.d/rc.local"

    # ---- Minimal /etc/os-release -------------------------------------------
    cat > "$build_dir/etc/os-release" <<EOF
NAME="CoreBuilderVX"
VERSION="1.0"
ID=cbx
ID_LIKE=linux
PRETTY_NAME="CoreBuilderVX OS 1.0"
HOME_URL="https://github.com/Cbetts1/CorebuilderVX"
EOF

    # ---- Minimal /etc/fstab ------------------------------------------------
    cat > "$build_dir/etc/fstab" <<'EOF'
# CoreBuilderVX fstab stub
proc    /proc   proc    defaults    0 0
sysfs   /sys    sysfs   defaults    0 0
tmpfs   /tmp    tmpfs   defaults    0 0
EOF

    # ---- Placeholder kernel stub -------------------------------------------
    echo "# CoreBuilderVX kernel config stub" > "$build_dir/boot/config"
    echo "cbx-1.0.0" > "$build_dir/boot/version"

    cbx_ok "Skeleton complete → $build_dir"
}

run_skeleton "$@"
