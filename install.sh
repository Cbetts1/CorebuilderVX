#!/usr/bin/env bash
# =============================================================================
# CoreBuilderVX — Installer
# Works in Termux (Android), Debian/Ubuntu, Arch, Alpine, macOS
# =============================================================================
set -euo pipefail

CBX_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export CBX_ROOT

GREEN="\033[0;32m"; YELLOW="\033[1;33m"; RED="\033[0;31m"; NC="\033[0m"
info()    { echo -e "${GREEN}[CBX-INSTALL]${NC} $*"; }
warning() { echo -e "${YELLOW}[CBX-WARN]${NC}   $*"; }
error()   { echo -e "${RED}[CBX-ERROR]${NC}  $*" >&2; }

# ---- Detect environment ------------------------------------------------------
detect_env() {
    if [[ -d /data/data/com.termux ]]; then
        ENV_TYPE="termux"
    elif [[ "$(uname)" == "Darwin" ]]; then
        ENV_TYPE="macos"
    elif command -v apt-get &>/dev/null; then
        ENV_TYPE="debian"
    elif command -v pacman  &>/dev/null; then
        ENV_TYPE="arch"
    elif command -v apk     &>/dev/null; then
        ENV_TYPE="alpine"
    else
        ENV_TYPE="generic"
    fi
    info "Detected environment: $ENV_TYPE"
}

# ---- Install packages --------------------------------------------------------
install_deps() {
    local PKGS_TERMUX="curl wget git python nodejs jq busybox openssh"
    local PKGS_APT="curl wget git python3 python3-pip nodejs npm jq"
    local PKGS_PACMAN="curl wget git python nodejs npm jq"
    local PKGS_ALPINE="curl wget git python3 py3-pip nodejs npm jq"
    local PKGS_BREW="curl wget git python node jq"

    case "$ENV_TYPE" in
        termux)
            info "Installing Termux packages..."
            pkg update -y
            pkg install -y $PKGS_TERMUX
            ;;
        debian)
            info "Installing apt packages..."
            sudo apt-get update -qq
            sudo apt-get install -y $PKGS_APT
            ;;
        arch)
            info "Installing pacman packages..."
            sudo pacman -Sy --noconfirm $PKGS_PACMAN
            ;;
        alpine)
            info "Installing apk packages..."
            sudo apk add --no-cache $PKGS_ALPINE
            ;;
        macos)
            info "Installing Homebrew packages..."
            brew install $PKGS_BREW || warning "Some packages may have failed"
            ;;
        *)
            warning "Unknown environment — skipping automatic package install."
            warning "Please manually install: curl wget git python3 nodejs jq"
            ;;
    esac
}

# ---- Python deps (optional) -------------------------------------------------
install_python_deps() {
    if command -v pip3 &>/dev/null; then
        info "Installing Python dependencies..."
        pip3 install --quiet flask flask-cors requests 2>/dev/null \
            || warning "Some Python deps failed (non-fatal)"
    elif command -v pip &>/dev/null; then
        pip install --quiet flask flask-cors requests 2>/dev/null \
            || warning "Some Python deps failed (non-fatal)"
    else
        warning "pip not found — Python backend will be limited"
    fi
}

# ---- Node deps (optional) ---------------------------------------------------
install_node_deps() {
    if command -v npm &>/dev/null; then
        info "Installing Node.js dependencies..."
        cd "$CBX_ROOT/modules/backend"
        npm install --silent 2>/dev/null || warning "npm install failed (non-fatal)"
        cd "$CBX_ROOT"
    else
        warning "npm not found — Node.js backend unavailable"
    fi
}

# ---- Permissions ------------------------------------------------------------
set_permissions() {
    info "Setting execute permissions..."
    find "$CBX_ROOT" -name "*.sh" -exec chmod +x {} \;
    chmod +x "$CBX_ROOT/core.sh"
}

# ---- Symlink (optional) -----------------------------------------------------
create_symlink() {
    local TARGET="/usr/local/bin/cbx"
    local PREFIX="${PREFIX:-}"   # Termux sets $PREFIX

    if [[ -n "$PREFIX" ]]; then
        TARGET="$PREFIX/bin/cbx"
    fi

    if [[ -w "$(dirname "$TARGET")" ]]; then
        ln -sf "$CBX_ROOT/core.sh" "$TARGET"
        info "Symlink created: cbx -> $CBX_ROOT/core.sh"
    else
        info "To add 'cbx' to PATH, run:"
        echo "  ln -s $CBX_ROOT/core.sh ~/bin/cbx   (or any dir in \$PATH)"
    fi
}

# ---- Run hardware detection -------------------------------------------------
run_detect() {
    info "Running hardware detection..."
    bash "$CBX_ROOT/modules/hardware/detect.sh" --save
}

# ---- Main -------------------------------------------------------------------
main() {
    echo ""
    echo -e "${GREEN}==================================================${NC}"
    echo -e "${GREEN}   CoreBuilderVX — Installer${NC}"
    echo -e "${GREEN}==================================================${NC}"
    echo ""

    detect_env
    install_deps
    install_python_deps
    install_node_deps
    set_permissions
    create_symlink
    run_detect

    echo ""
    info "Installation complete!"
    echo ""
    echo -e "  Run ${GREEN}./core.sh${NC} or ${GREEN}cbx${NC} to launch CoreBuilderVX"
    echo ""
}

main "$@"
