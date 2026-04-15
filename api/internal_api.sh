#!/usr/bin/env bash
# =============================================================================
# CoreBuilderVX — Internal API / Helper Library
# Source this file to get logging, colours, prompts, and utility functions
# =============================================================================

# ---- Colour palette (respects CBX_NO_COLOR) ----------------------------------
if [[ "${CBX_NO_COLOR:-0}" -eq 0 ]] && [[ -t 1 ]]; then
    C_RED="\033[0;31m";    C_GREEN="\033[0;32m"
    C_YELLOW="\033[1;33m"; C_BLUE="\033[0;34m"
    C_CYAN="\033[0;36m";   C_BOLD="\033[1m"
    C_DIM="\033[2m";       C_NC="\033[0m"
else
    C_RED=""; C_GREEN=""; C_YELLOW=""; C_BLUE=""
    C_CYAN=""; C_BOLD=""; C_DIM=""; C_NC=""
fi

# ---- Logging -----------------------------------------------------------------
cbx_log() {
    local level="$1"; shift
    local ts; ts="$(date '+%H:%M:%S')"
    local msg="[$ts][$level] $*"

    # Write to log file if configured
    local log_file="${CBX_LOG_FILE:-}"
    [[ -n "$log_file" ]] && echo "$msg" >> "$log_file" 2>/dev/null || true

    case "$level" in
        INFO)  echo -e "${C_GREEN}[CBX]${C_NC}  $*" ;;
        WARN)  echo -e "${C_YELLOW}[WARN]${C_NC} $*" ;;
        ERROR) echo -e "${C_RED}[ERR]${C_NC}  $*" >&2 ;;
        DEBUG) [[ "${CBX_LOG_LEVEL:-info}" == "debug" ]] \
               && echo -e "${C_DIM}[DBG]  $*${C_NC}" ;;
        STEP)  echo -e "${C_CYAN}  →${C_NC} $*" ;;
        OK)    echo -e "${C_GREEN}  ✓${C_NC} $*" ;;
        FAIL)  echo -e "${C_RED}  ✗${C_NC} $*" ;;
    esac
}

cbx_info()  { cbx_log INFO  "$@"; }
cbx_warn()  { cbx_log WARN  "$@"; }
cbx_error() { cbx_log ERROR "$@"; }
cbx_debug() { cbx_log DEBUG "$@"; }
cbx_step()  { cbx_log STEP  "$@"; }
cbx_ok()    { cbx_log OK    "$@"; }
cbx_fail()  { cbx_log FAIL  "$@"; }

# ---- Banner ------------------------------------------------------------------
cbx_banner() {
    local title="${1:-CoreBuilderVX}"
    echo -e "${C_BOLD}${C_CYAN}"
    echo "  ██████╗██████╗ ██╗  ██╗"
    echo " ██╔════╝██╔══██╗╚██╗██╔╝"
    echo " ██║     ██████╔╝ ╚███╔╝ "
    echo " ██║     ██╔══██╗ ██╔██╗ "
    echo " ╚██████╗██████╔╝██╔╝ ██╗"
    echo "  ╚═════╝╚═════╝ ╚═╝  ╚═╝"
    echo -e "${C_NC}${C_BOLD}  $title${C_NC}"
    echo ""
}

# ---- Section header ---------------------------------------------------------
cbx_header() {
    local title="$1"
    local width="${CBX_TERM_WIDTH:-60}"
    local line; line="$(printf '═%.0s' $(seq 1 $((width-2))))"
    echo -e "\n${C_BOLD}╔${line}╗"
    printf "║  %-$((width-4))s  ║\n" "$title"
    echo -e "╚${line}╝${C_NC}"
}

# ---- Prompt yes/no -----------------------------------------------------------
cbx_confirm() {
    local prompt="${1:-Continue?} [y/N] "
    local answer
    read -r -p "$(echo -e "${C_YELLOW}${prompt}${C_NC}")" answer
    [[ "${answer,,}" =~ ^(y|yes)$ ]]
}

# ---- Prompt for value --------------------------------------------------------
cbx_prompt() {
    local prompt="$1"
    local default="${2:-}"
    local value
    if [[ -n "$default" ]]; then
        read -r -p "$(echo -e "${C_CYAN}${prompt} [${default}]:${C_NC} ")" value
        echo "${value:-$default}"
    else
        read -r -p "$(echo -e "${C_CYAN}${prompt}:${C_NC} ")" value
        echo "$value"
    fi
}

# ---- Spinner -----------------------------------------------------------------
cbx_spinner_start() {
    local msg="${1:-Working...}"
    (
        local i=0
        local sp='⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏'
        while true; do
            printf "\r${C_CYAN}${sp:$i:1}${C_NC} %s" "$msg"
            i=$(( (i+1) % ${#sp} ))
            sleep 0.1
        done
    ) &
    CBX_SPINNER_PID=$!
}

cbx_spinner_stop() {
    [[ -n "${CBX_SPINNER_PID:-}" ]] && kill "$CBX_SPINNER_PID" 2>/dev/null; printf "\r"
    CBX_SPINNER_PID=""
}

# ---- Progress bar ------------------------------------------------------------
cbx_progress() {
    local current="$1" total="$2" label="${3:-}"
    local width=40
    local filled=$(( current * width / total ))
    local empty=$(( width - filled ))
    local bar; bar="$(printf '█%.0s' $(seq 1 $filled))$(printf '░%.0s' $(seq 1 $empty))"
    printf "\r${C_CYAN}[${bar}]${C_NC} %d/%d %s" "$current" "$total" "$label"
    [[ "$current" -eq "$total" ]] && echo ""
}

# ---- Require a command -------------------------------------------------------
cbx_require() {
    local cmd="$1"
    if ! command -v "$cmd" &>/dev/null; then
        cbx_error "Required command not found: $cmd"
        cbx_info  "Run ./install.sh to install dependencies"
        return 1
    fi
}

# ---- Write timestamped build log entry --------------------------------------
cbx_build_log() {
    local tag="$1"; shift
    local msg="$*"
    local log="${CBX_BUILD_DIR:-$CBX_ROOT/builds}/build.log"
    mkdir -p "$(dirname "$log")"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')][$tag] $msg" >> "$log"
}

# ---- Check available disk space (MB) ----------------------------------------
cbx_check_disk() {
    local required_mb="${1:-100}"
    local available_mb
    available_mb="$(df -m "${CBX_ROOT:-.}" | awk 'NR==2{print $4}')"
    if [[ "$available_mb" -lt "$required_mb" ]]; then
        cbx_warn "Low disk space: ${available_mb}MB available, ${required_mb}MB needed"
        return 1
    fi
    return 0
}

# ---- Source a module safely --------------------------------------------------
cbx_load_module() {
    local mod_path="$CBX_ROOT/modules/$1"
    if [[ -f "$mod_path" ]]; then
        source "$mod_path"
        cbx_debug "Loaded module: $1"
    else
        cbx_warn "Module not found: $1"
        return 1
    fi
}

# ---- Pause / Press-any-key --------------------------------------------------
cbx_pause() {
    local msg="${1:-Press Enter to continue...}"
    read -r -p "$(echo -e "${C_DIM}${msg}${C_NC}")" _
}
