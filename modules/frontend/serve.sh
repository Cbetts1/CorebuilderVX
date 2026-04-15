#!/usr/bin/env bash
# =============================================================================
# CoreBuilderVX — Frontend Server
# Serves the operator cockpit UI via a local HTTP server
# Works in Termux with Python or Node.js
# =============================================================================

CBX_ROOT="${CBX_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
source "$CBX_ROOT/api/internal_api.sh"
source "$CBX_ROOT/config/default.conf" 2>/dev/null || true

FRONTEND_DIR="$CBX_ROOT/modules/frontend"
FRONTEND_PORT="${CBX_FRONTEND_PORT:-8766}"
PID_FILE="$CBX_TMP_DIR/frontend.pid"

serve_frontend() {
    cbx_header "Operator Cockpit"
    cbx_info "Serving: $FRONTEND_DIR"
    cbx_info "URL:     http://127.0.0.1:${FRONTEND_PORT}"
    echo ""

    mkdir -p "$CBX_TMP_DIR"

    if python3 -c "import http.server" &>/dev/null 2>&1; then
        cbx_info "Starting Python HTTP server (port ${FRONTEND_PORT})..."
        echo ""
        echo -e "  ${C_DIM}Press Ctrl+C to stop${C_NC}"
        echo ""
        cbx_info "Open in browser: http://127.0.0.1:${FRONTEND_PORT}/cockpit.html"
        cd "$FRONTEND_DIR"
        python3 -m http.server "$FRONTEND_PORT" --bind 127.0.0.1

    elif command -v node &>/dev/null; then
        cbx_info "Starting Node.js HTTP server (port ${FRONTEND_PORT})..."
        node -e "
const http = require('http');
const fs   = require('fs');
const path = require('path');
const mime = { '.html':'text/html', '.css':'text/css', '.js':'application/javascript' };
http.createServer((req, res) => {
  let fp = path.join('${FRONTEND_DIR}', req.url === '/' ? '/cockpit.html' : req.url);
  if (fs.existsSync(fp)) {
    const ct = mime[path.extname(fp)] || 'text/plain';
    res.writeHead(200, {'Content-Type': ct});
    fs.createReadStream(fp).pipe(res);
  } else {
    res.writeHead(404); res.end('Not found');
  }
}).listen(${FRONTEND_PORT}, '127.0.0.1', () => {
  console.log('Cockpit at http://127.0.0.1:${FRONTEND_PORT}/cockpit.html');
});
"
    else
        cbx_warn "No HTTP server available (need python3 or node)"
        cbx_info "Open this file directly in a browser:"
        echo "  $FRONTEND_DIR/cockpit.html"
        cbx_pause
    fi
}

serve_frontend "$@"
