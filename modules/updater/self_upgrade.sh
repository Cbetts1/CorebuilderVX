#!/usr/bin/env bash
# =============================================================================
# CoreBuilderVX — Self-Upgrade Module
# Pulls latest release from GitHub and applies updates in-place
# =============================================================================

CBX_ROOT="${CBX_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
source "$CBX_ROOT/api/internal_api.sh"
source "$CBX_ROOT/config/default.conf" 2>/dev/null || true

run_self_upgrade() {
    cbx_header "Self-Upgrade"
    echo ""

    local source="${CBX_UPDATE_SOURCE:-https://github.com/Cbetts1/CorebuilderVX}"
    local branch="${CBX_UPDATE_BRANCH:-main}"

    cbx_info "Update source: $source"
    cbx_info "Branch: $branch"
    echo ""

    # ---- Check git availability ---------------------------------------------
    if ! command -v git &>/dev/null; then
        cbx_error "git not found. Install git and retry."
        cbx_pause
        return 1
    fi

    # ---- Check internet connectivity ----------------------------------------
    cbx_step "Checking connectivity..."
    if ! curl -s --max-time 5 --head "https://github.com" &>/dev/null \
       && ! wget -q --timeout=5 --spider "https://github.com" &>/dev/null; then
        cbx_warn "No internet connection — cannot check for updates"
        cbx_pause
        return 1
    fi
    cbx_ok "Connected"

    # ---- Check if we're in a git repo ---------------------------------------
    if ! git -C "$CBX_ROOT" rev-parse --is-inside-work-tree &>/dev/null; then
        cbx_warn "Not a git repository — cannot self-upgrade via git"
        cbx_info "Manual update: download the latest release from:"
        echo "  $source/releases"
        cbx_pause
        return 0
    fi

    # ---- Get current version/commit -----------------------------------------
    local current_commit; current_commit="$(git -C "$CBX_ROOT" rev-parse --short HEAD 2>/dev/null || echo unknown)"
    cbx_info "Current commit: $current_commit"

    # ---- Fetch remote -------------------------------------------------------
    cbx_step "Fetching remote updates..."
    if ! git -C "$CBX_ROOT" fetch origin "$branch" --quiet; then
        cbx_error "Failed to fetch updates"
        cbx_pause
        return 1
    fi

    # ---- Compare commits -----------------------------------------------------
    local remote_commit; remote_commit="$(git -C "$CBX_ROOT" rev-parse --short "origin/$branch" 2>/dev/null || echo unknown)"
    cbx_info "Remote commit: $remote_commit"

    if [[ "$current_commit" == "$remote_commit" ]]; then
        cbx_ok "Already up to date (v${CBX_VERSION:-?})"
        cbx_pause
        return 0
    fi

    # ---- Show changelog -----------------------------------------------------
    echo ""
    cbx_step "Changes:"
    git -C "$CBX_ROOT" log --oneline "HEAD..origin/$branch" 2>/dev/null | head -20 || true
    echo ""

    # ---- Confirm update -----------------------------------------------------
    if ! cbx_confirm "Apply update? (your current changes will be backed up)"; then
        cbx_info "Update cancelled"
        cbx_pause
        return 0
    fi

    # ---- Backup current state -----------------------------------------------
    local backup_dir="$CBX_DATA_DIR/backups/pre-upgrade-$(date +%Y%m%d-%H%M%S)"
    mkdir -p "$backup_dir"
    cbx_step "Backing up to $backup_dir..."
    cp -r "$CBX_ROOT/config" "$backup_dir/" 2>/dev/null || true
    cp -r "$CBX_ROOT/data"   "$backup_dir/" 2>/dev/null || true
    cbx_ok "Backup complete"

    # ---- Apply update --------------------------------------------------------
    cbx_step "Applying update..."
    if git -C "$CBX_ROOT" merge "origin/$branch" --ff-only --quiet; then
        cbx_ok "Update applied"
    elif git -C "$CBX_ROOT" rebase "origin/$branch" --quiet; then
        cbx_ok "Update rebased"
    else
        cbx_error "Merge conflict — manual resolution required"
        cbx_info "Backup available at: $backup_dir"
        cbx_pause
        return 1
    fi

    # ---- Restore permissions ------------------------------------------------
    find "$CBX_ROOT" -name "*.sh" -exec chmod +x {} \;
    cbx_ok "Permissions restored"

    local new_commit; new_commit="$(git -C "$CBX_ROOT" rev-parse --short HEAD 2>/dev/null)"
    cbx_ok "Updated: $current_commit → $new_commit"
    echo ""
    cbx_info "Restart CoreBuilderVX to use the new version"
    cbx_pause
}

run_self_upgrade "$@"
