#!/usr/bin/env bash
# =============================================================================
# CoreBuilderVX — Website Builder & Online Studio (shell interface)
# Provides an interactive menu for creating, building, and previewing sites.
# Delegates to modules/site_builder/website_builder.py for all operations.
# =============================================================================

CBX_ROOT="${CBX_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
source "$CBX_ROOT/api/internal_api.sh"
source "$CBX_ROOT/config/default.conf" 2>/dev/null || true

CBX_WB_PY="$CBX_ROOT/modules/site_builder/website_builder.py"
CBX_PREVIEW_PORT="${CBX_PREVIEW_PORT:-8767}"

# ---- Require Python ----------------------------------------------------------
_require_python() {
    if ! python3 --version &>/dev/null 2>&1; then
        cbx_error "Python 3 is required for the Website Builder."
        cbx_info  "Install with: pkg install python (Termux) or apt install python3"
        return 1
    fi
}

# ---- Run website_builder.py helper ------------------------------------------
_wb() {
    python3 "$CBX_WB_PY" "$@"
}

# ---- List sites --------------------------------------------------------------
_list_sites() {
    cbx_header "Website Builder — My Sites"
    _wb list
    echo ""
    cbx_pause
}

# ---- Create new site ---------------------------------------------------------
_create_site() {
    cbx_header "Website Builder — New Site"
    echo ""
    echo -e "  Templates: ${C_CYAN}blank${C_NC}, ${C_CYAN}landing${C_NC}, ${C_CYAN}portfolio${C_NC}, ${C_CYAN}blog${C_NC}"
    echo -e "  Modes:     ${C_CYAN}template${C_NC} (starter HTML generated), ${C_CYAN}code${C_NC} (edit raw HTML)"
    echo ""

    local name; name="$(cbx_prompt "Site name (slug, e.g. my-portfolio)")"
    [[ -z "$name" ]] && { cbx_warn "Name required. Cancelled."; cbx_pause; return; }

    local template; template="$(cbx_prompt "Template" "landing")"
    local title;    title="$(cbx_prompt "Site title" "$name")"
    local desc;     desc="$(cbx_prompt "Description (optional)" "")"
    local mode;     mode="$(cbx_prompt "Mode (template/code)" "template")"

    echo ""
    cbx_info "Creating site '$name'..."

    local out
    out="$(_wb create --name "$name" --template "${template:-landing}" \
                      --title "${title:-$name}" --desc "${desc:-}" \
                      --mode "${mode:-template}" 2>&1)"
    local rc=$?

    if [[ $rc -eq 0 ]]; then
        cbx_ok "Site '$name' created."
        echo ""
        echo -e "  ${C_DIM}Pages directory:  $CBX_DATA_DIR/sites/$name/pages/${C_NC}"
        echo -e "  ${C_DIM}Run 'Build Site' to generate the static output.${C_NC}"
    else
        cbx_error "Failed to create site: $out"
    fi
    echo ""
    cbx_pause
}

# ---- Build site --------------------------------------------------------------
_build_site() {
    cbx_header "Website Builder — Build Site"
    echo ""
    cbx_info "Available sites:"
    _wb list
    echo ""

    local name; name="$(cbx_prompt "Site name to build")"
    [[ -z "$name" ]] && { cbx_warn "Name required. Cancelled."; cbx_pause; return; }

    cbx_info "Building '$name'..."
    local out; out="$(_wb build --name "$name" 2>&1)"
    local rc=$?

    if [[ $rc -eq 0 ]]; then
        cbx_ok "$out"
        echo ""
        echo -e "  ${C_DIM}Use 'Preview Site' to serve the output in a browser.${C_NC}"
    else
        cbx_error "$out"
    fi
    echo ""
    cbx_pause
}

# ---- Preview site ------------------------------------------------------------
_preview_site() {
    cbx_header "Website Builder — Preview Site"
    echo ""
    cbx_info "Available sites:"
    _wb list
    echo ""

    local name; name="$(cbx_prompt "Site name to preview")"
    [[ -z "$name" ]] && { cbx_warn "Name required. Cancelled."; cbx_pause; return; }

    local port_in; port_in="$(cbx_prompt "Preview port" "$CBX_PREVIEW_PORT")"
    local port="${port_in:-$CBX_PREVIEW_PORT}"

    cbx_info "Building '$name' before preview..."
    local build_out; build_out="$(_wb build --name "$name" 2>&1)"
    local rc=$?
    if [[ $rc -ne 0 ]]; then
        cbx_error "Build failed: $build_out"
        cbx_pause
        return
    fi
    cbx_ok "Build complete."

    local build_dir="$CBX_DATA_DIR/sites/$name/_build"
    if [[ ! -d "$build_dir" ]]; then
        cbx_error "Build directory not found: $build_dir"
        cbx_pause
        return
    fi

    echo ""
    cbx_info "Starting preview server on port $port..."
    cbx_info "Open in browser: http://127.0.0.1:${port}/index.html"
    echo -e "  ${C_DIM}Press Ctrl+C to stop${C_NC}"
    echo ""

    cd "$build_dir" || { cbx_error "Cannot enter $build_dir"; cbx_pause; return; }

    if python3 -c "import http.server" &>/dev/null 2>&1; then
        python3 -m http.server "$port" --bind 127.0.0.1
    elif command -v node &>/dev/null; then
        node -e "
const http=require('http'),fs=require('fs'),path=require('path');
const mime={'.html':'text/html','.css':'text/css','.js':'application/javascript',
            '.png':'image/png','.jpg':'image/jpeg','.gif':'image/gif',
            '.svg':'image/svg+xml','.ico':'image/x-icon'};
http.createServer((req,res)=>{
  let fp=path.join('${build_dir}',req.url==='/'?'/index.html':req.url);
  if(fs.existsSync(fp)){
    const ct=mime[path.extname(fp)]||'text/plain';
    res.writeHead(200,{'Content-Type':ct});
    fs.createReadStream(fp).pipe(res);
  }else{res.writeHead(404);res.end('Not found');}
}).listen(${port},'127.0.0.1',()=>console.log('Preview: http://127.0.0.1:${port}/index.html'));
"
    else
        cbx_warn "No HTTP server available (need python3 or node)."
        cbx_info "Open directly: $build_dir/index.html"
        cbx_pause
    fi
}

# ---- Delete site -------------------------------------------------------------
_delete_site() {
    cbx_header "Website Builder — Delete Site"
    echo ""
    _wb list
    echo ""

    local name; name="$(cbx_prompt "Site name to delete")"
    [[ -z "$name" ]] && { cbx_warn "Cancelled."; cbx_pause; return; }

    echo ""
    cbx_warn "This will permanently delete '$name' and all its files."
    if cbx_confirm "Are you sure?"; then
        local out; out="$(_wb delete --name "$name" 2>&1)"
        local rc=$?
        [[ $rc -eq 0 ]] && cbx_ok "$out" || cbx_error "$out"
    else
        cbx_info "Cancelled."
    fi
    echo ""
    cbx_pause
}

# ---- Main menu ---------------------------------------------------------------
website_builder_menu() {
    _require_python || { cbx_pause; return; }

    while true; do
        clear
        cbx_banner "v${CBX_VERSION:-1.0.0}"
        cbx_header "Website Builder & Online Studio"
        echo ""
        echo -e "  ${C_CYAN}1${C_NC}  New Site          — Create a new website project"
        echo -e "  ${C_CYAN}2${C_NC}  My Sites          — List all projects"
        echo -e "  ${C_CYAN}3${C_NC}  Build Site        — Generate static HTML output"
        echo -e "  ${C_CYAN}4${C_NC}  Preview Site      — Serve a project in the browser"
        echo -e "  ${C_CYAN}5${C_NC}  Delete Site       — Remove a project"
        echo -e "  ${C_CYAN}B${C_NC}  Back"
        echo ""

        read -r -p "$(echo -e "  ${C_BOLD}Select option:${C_NC} ")" choice

        case "${choice,,}" in
            1) _create_site  ;;
            2) _list_sites   ;;
            3) _build_site   ;;
            4) _preview_site ;;
            5) _delete_site  ;;
            b|back) return   ;;
            *) cbx_warn "Unknown option: $choice"; sleep 1 ;;
        esac
    done
}

website_builder_menu "$@"
