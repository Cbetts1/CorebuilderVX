#!/usr/bin/env bash
# =============================================================================
# CoreBuilderVX — Local AI Runner
# Detects available AI backends and runs small models locally
# Supports: llama.cpp, ollama, transformers (Python), gpt4all, stub mode
# =============================================================================

CBX_ROOT="${CBX_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
source "$CBX_ROOT/api/internal_api.sh"
[[ -f "$CBX_ROOT/config/hardware.conf" ]] && source "$CBX_ROOT/config/hardware.conf"

# ---- Detect available AI backends -------------------------------------------
detect_ai_backend() {
    if command -v ollama &>/dev/null; then
        echo "ollama"
    elif command -v llama-cli &>/dev/null || command -v llama.cpp &>/dev/null; then
        echo "llama_cpp"
    elif python3 -c "import llama_cpp" 2>/dev/null; then
        echo "llama_cpp_python"
    elif python3 -c "import transformers" 2>/dev/null; then
        echo "transformers"
    elif python3 -c "import gpt4all" 2>/dev/null; then
        echo "gpt4all"
    else
        echo "stub"
    fi
}

# ---- Stub mode (no real model — demo responses) -----------------------------
run_stub_mode() {
    cbx_warn "No AI backend detected — running in STUB mode"
    cbx_info "Install one of: ollama, llama.cpp, gpt4all, transformers"
    echo ""
    cbx_info "Stub responses are placeholders only"
    echo ""

    local responses=(
        "I am CoreBuilderVX AI (stub mode). Install a real model for full capability."
        "That's an interesting build configuration. I'd recommend starting with minimal."
        "Your hardware profile suggests the llama-2-7b-q4 model would run well."
        "To install ollama: pkg install ollama (Termux) or visit ollama.com"
        "Build complete. All systems nominal. (stub)"
    )

    local chat_log="$CBX_DATA_DIR/ai_chat_$(date +%Y%m%d).log"

    while true; do
        echo ""
        read -r -p "$(echo -e "  ${C_CYAN}You:${C_NC} ")" user_input
        [[ "${user_input,,}" =~ ^(exit|quit|bye)$ ]] && break
        [[ -z "$user_input" ]] && continue

        local reply="${responses[$((RANDOM % ${#responses[@]}))]}"
        echo -e "  ${C_GREEN}AI:${C_NC}  $reply"

        # Log conversation
        echo "[$(date '+%H:%M:%S')][USER] $user_input" >> "$chat_log"
        echo "[$(date '+%H:%M:%S')][AI]   $reply"     >> "$chat_log"
    done
}

# ---- Ollama backend ---------------------------------------------------------
run_ollama() {
    local model="${CBX_AI_MODEL:-llama3.2}"

    cbx_info "Ollama backend detected"

    # Check if model is pulled
    if ! ollama list 2>/dev/null | grep -q "$model"; then
        cbx_warn "Model '$model' not found locally"
        if cbx_confirm "Pull '$model' now? (may be large)"; then
            ollama pull "$model"
        else
            cbx_info "Available models:"
            ollama list
            model="$(cbx_prompt "Enter model name")"
        fi
    fi

    cbx_info "Starting chat with: $model"
    echo -e "  ${C_DIM}Type 'exit' to quit${C_NC}"
    echo ""
    ollama run "$model"
}

# ---- Transformers / GPT-2 (Python) -----------------------------------------
run_transformers() {
    cbx_info "Transformers backend detected"
    local model="${CBX_AI_MODEL:-gpt2}"
    cbx_info "Using model: $model"
    echo ""

    python3 - "$model" <<'PYEOF'
import sys, textwrap
try:
    from transformers import pipeline
    model = sys.argv[1] if len(sys.argv) > 1 else "gpt2"
    print(f"  Loading {model}...")
    gen = pipeline("text-generation", model=model, max_new_tokens=128)
    print(f"  Model ready. Type 'exit' to quit.\n")
    while True:
        prompt = input("  You: ").strip()
        if prompt.lower() in ("exit", "quit", "bye"):
            break
        if not prompt:
            continue
        result = gen(prompt, do_sample=True, temperature=0.7)[0]["generated_text"]
        print(f"  AI:  {textwrap.fill(result, width=70, subsequent_indent='       ')}")
        print()
except KeyboardInterrupt:
    pass
except Exception as e:
    print(f"  Error: {e}")
PYEOF
}

# ---- GPT4All backend --------------------------------------------------------
run_gpt4all() {
    cbx_info "GPT4All backend detected"
    python3 - <<'PYEOF'
try:
    from gpt4all import GPT4All
    model = GPT4All("orca-mini-3b-gguf2-q4_0.gguf")
    print("  Model ready. Type 'exit' to quit.\n")
    with model.chat_session():
        while True:
            prompt = input("  You: ").strip()
            if prompt.lower() in ("exit", "quit"):
                break
            if not prompt:
                continue
            response = model.generate(prompt, max_tokens=128)
            print(f"  AI: {response}\n")
except Exception as e:
    print(f"  Error: {e}")
PYEOF
}

# ---- Main -------------------------------------------------------------------
run_local_ai() {
    cbx_header "Local AI Runner"
    echo ""

    # Hardware-aware warning
    local ram="${CBX_HW_RAM_MB:-0}"
    if [[ "$ram" -lt 2048 && "$ram" -gt 0 ]]; then
        cbx_warn "Low RAM (${ram}MB) — use quantised (Q4) models for best performance"
    fi

    local backend
    backend="$(detect_ai_backend)"
    cbx_info "AI backend: $backend"
    echo ""

    case "$backend" in
        ollama)           run_ollama ;;
        transformers)     run_transformers ;;
        gpt4all)          run_gpt4all ;;
        stub|*)           run_stub_mode ;;
    esac

    echo ""
    cbx_info "AI session ended"
    cbx_pause
}

run_local_ai "$@"
