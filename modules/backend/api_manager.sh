#!/usr/bin/env bash
# =============================================================================
# CoreBuilderVX — Backend API Manager
# Starts/stops the Python or Node.js API engine
# =============================================================================

CBX_ROOT="${CBX_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
source "$CBX_ROOT/api/internal_api.sh"
source "$CBX_ROOT/config/default.conf" 2>/dev/null || true
[[ -f "$CBX_ROOT/config/user.conf" ]]     && source "$CBX_ROOT/config/user.conf"

PID_FILE="$CBX_TMP_DIR/api.pid"

# ---- Detect best backend ----------------------------------------------------
_pick_backend() {
    local pref="${CBX_BACKEND:-auto}"
    if [[ "$pref" == "auto" ]]; then
        if python3 -c "import flask" &>/dev/null 2>&1; then
            echo "python"
        elif command -v node &>/dev/null; then
            echo "node"
        else
            echo "none"
        fi
    else
        echo "$pref"
    fi
}

# ---- Start ------------------------------------------------------------------
api_start() {
    if [[ -f "$PID_FILE" ]] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
        cbx_warn "API already running (PID $(cat "$PID_FILE"))"
        return
    fi

    local backend; backend="$(_pick_backend)"
    cbx_info "Starting API engine (backend: $backend) on ${CBX_API_HOST}:${CBX_API_PORT}"

    mkdir -p "$CBX_TMP_DIR"

    case "$backend" in
        python)
            python3 "$CBX_ROOT/modules/backend/api.py" \
                --host "$CBX_API_HOST" --port "$CBX_API_PORT" \
                &>"$CBX_LOG_DIR/api.log" &
            echo $! > "$PID_FILE"
            ;;
        node)
            node "$CBX_ROOT/modules/backend/api.js" \
                &>"$CBX_LOG_DIR/api.log" &
            echo $! > "$PID_FILE"
            ;;
        none)
            cbx_warn "No API backend available (install flask or node)"
            return 1
            ;;
    esac

    sleep 1
    if kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
        cbx_ok "API running (PID $(cat "$PID_FILE")) → http://${CBX_API_HOST}:${CBX_API_PORT}"
    else
        cbx_error "API failed to start — check $CBX_LOG_DIR/api.log"
    fi
}

# ---- Stop -------------------------------------------------------------------
api_stop() {
    if [[ -f "$PID_FILE" ]]; then
        local pid; pid="$(cat "$PID_FILE")"
        kill "$pid" 2>/dev/null && cbx_ok "API stopped (PID $pid)" || cbx_warn "PID $pid not running"
        rm -f "$PID_FILE"
    else
        cbx_warn "API not running"
    fi
}

# ---- Status -----------------------------------------------------------------
api_status() {
    if [[ -f "$PID_FILE" ]] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
        cbx_ok "API RUNNING (PID $(cat "$PID_FILE")) → http://${CBX_API_HOST}:${CBX_API_PORT}"
    else
        cbx_warn "API STOPPED"
    fi
}

# ---- Interactive menu -------------------------------------------------------
manage_api() {
    cbx_header "Backend API Manager"
    api_status
    echo ""
    echo -e "  ${C_CYAN}1${C_NC}  Start API"
    echo -e "  ${C_CYAN}2${C_NC}  Stop API"
    echo -e "  ${C_CYAN}3${C_NC}  Restart API"
    echo -e "  ${C_CYAN}4${C_NC}  View logs"
    echo -e "  ${C_CYAN}5${C_NC}  Back"
    echo ""
    read -r -p "  Select: " choice
    case "$choice" in
        1) api_start ;;
        2) api_stop  ;;
        3) api_stop; sleep 1; api_start ;;
        4) tail -50 "$CBX_LOG_DIR/api.log" 2>/dev/null || cbx_warn "No log yet" ;;
        *) return ;;
    esac
    cbx_pause
}

# ---- Entry ------------------------------------------------------------------
case "${1:-menu}" in
    start)  api_start  ;;
    stop)   api_stop   ;;
    status) api_status ;;
    menu|*) manage_api ;;
esac
