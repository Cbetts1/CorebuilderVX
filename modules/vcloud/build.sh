#!/usr/bin/env bash
# =============================================================================
# CoreBuilderVX — Vcloud Builder
# Creates virtual cloud environment blueprints and configs
# =============================================================================

CBX_ROOT="${CBX_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
source "$CBX_ROOT/api/internal_api.sh"
[[ -f "$CBX_ROOT/config/hardware.conf" ]] && source "$CBX_ROOT/config/hardware.conf"

run_vcloud_builder() {
    cbx_header "Vcloud Builder"
    echo ""

    # ---- Select cloud type --------------------------------------------------
    echo -e "  Cloud environment types:"
    echo -e "  ${C_CYAN}1${C_NC}  Mini-cloud (single-node, phone/RPi)"
    echo -e "  ${C_CYAN}2${C_NC}  Dev cloud  (3-node cluster)"
    echo -e "  ${C_CYAN}3${C_NC}  Full cloud (multi-node + load balancer)"
    echo -e "  ${C_CYAN}4${C_NC}  Custom"
    echo ""
    read -r -p "  Select [1]: " cloud_choice

    local cloud_type nodes
    case "${cloud_choice:-1}" in
        2) cloud_type="dev";  nodes=3  ;;
        3) cloud_type="full"; nodes=5  ;;
        4)
            cloud_type="custom"
            nodes="$(cbx_prompt "Number of nodes" "2")"
            ;;
        *) cloud_type="mini"; nodes=1  ;;
    esac

    local cloud_name
    cloud_name="$(cbx_prompt "Cloud name" "vcloud-$(date +%Y%m%d)")"
    local cloud_dir="$CBX_DATA_DIR/vclouds/$cloud_name"
    mkdir -p "$cloud_dir"

    cbx_info "Building $cloud_type cloud: $cloud_name ($nodes nodes)"
    echo ""

    # ---- Generate node configs ----------------------------------------------
    for i in $(seq 1 "$nodes"); do
        local node_dir="$cloud_dir/node-$i"
        mkdir -p "$node_dir"/{etc,var,run}

        cat > "$node_dir/etc/node.conf" <<EOF
# CoreBuilderVX Vcloud Node Config
NODE_ID="$i"
NODE_NAME="${cloud_name}-node-$i"
NODE_ROLE="$([ $i -eq 1 ] && echo master || echo worker)"
NODE_IP="10.0.0.$((i + 10))"
NODE_PORT="$((8800 + i))"
CLOUD_NAME="$cloud_name"
CLOUD_TYPE="$cloud_type"
EOF

        cat > "$node_dir/run.sh" <<EOF
#!/usr/bin/env bash
# Start node-$i simulation
source "$CBX_ROOT/api/internal_api.sh"
source "$node_dir/etc/node.conf"
cbx_info "Node \$NODE_NAME (\$NODE_ROLE) starting at \$NODE_IP:\$NODE_PORT"
echo "Node \$NODE_NAME ready" > "$node_dir/run/status"
cbx_ok "Node \$NODE_NAME online"
EOF
        chmod +x "$node_dir/run.sh"

        cbx_ok "  Node $i: ${cloud_name}-node-$i (10.0.0.$((i + 10)))"
        sleep 0.1
    done

    # ---- Generate cloud manifest --------------------------------------------
    cat > "$cloud_dir/cloud.json" <<EOF
{
  "name": "$cloud_name",
  "type": "$cloud_type",
  "nodes": $nodes,
  "created": "$(date -u '+%Y-%m-%dT%H:%M:%SZ')",
  "network": "10.0.0.0/24",
  "status": "ready",
  "built_by": "CoreBuilderVX v${CBX_VERSION:-1.0.0}"
}
EOF

    # ---- Generate start-all script ------------------------------------------
    cat > "$cloud_dir/start-all.sh" <<EOF
#!/usr/bin/env bash
# Start all nodes in $cloud_name
CBX_ROOT="${CBX_ROOT}"
source "\$CBX_ROOT/api/internal_api.sh"
cbx_header "Vcloud: $cloud_name"
for i in \$(seq 1 $nodes); do
    bash "$cloud_dir/node-\$i/run.sh"
done
cbx_ok "All $nodes node(s) started"
EOF
    chmod +x "$cloud_dir/start-all.sh"

    echo ""
    cbx_ok "Vcloud built: $cloud_dir"
    echo -e "  ${C_DIM}Run: $cloud_dir/start-all.sh${C_NC}"
    echo ""

    if cbx_confirm "Start the cloud now?"; then
        bash "$cloud_dir/start-all.sh"
    fi

    cbx_build_log "VCLOUD" "Built: $cloud_name type=$cloud_type nodes=$nodes"
    cbx_pause
}

run_vcloud_builder "$@"
