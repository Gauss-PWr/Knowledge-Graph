#!/usr/bin/env bash
# =============================================================================
# run_server.sh - pull the latest code and run the Marker tests on the server
#
# Repo layout (everything code-related lives in scripts/):
#   papers/  papers_md/  papers_json/  setup_guides_measurments_test_results/
#   scripts/  run_server.sh  run_setups.py  pdf_to_md_processing.py  requirements.txt
#
# Assumes the one-time setup is done (repo cloned, envs installed).
# Every run:
#   1. git pull
#   2. reinstalls Python packages only if scripts/requirements.txt changed
#   3. starts vLLM (or reuses one that is already running)
#   4. runs scripts/run_setups.py (or --script ...)
#   5. stops vLLM (unless --keep-vllm), pushes results with --push
#
# Usage (inside tmux):
#   bash ~/<repo>/scripts/run_server.sh [--push] [--keep-vllm] [--no-pull] [--script PATH]
#
# Settings: override any variable below in ~/.pdf_server.env
# =============================================================================
set -euo pipefail

[ -f "$HOME/.pdf_server.env" ] && source "$HOME/.pdf_server.env"

REPO_DIR="${REPO_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"   # repo = folder above scripts/
BRANCH="${BRANCH:-$(git -C "$REPO_DIR" rev-parse --abbrev-ref HEAD 2>/dev/null || echo main)}"   # default: the branch you cloned
SCRIPT="${SCRIPT:-scripts/run_setups.py}"
ENV_DIR="${ENV_DIR:-$HOME/envs/marker}"
BACKEND="${BACKEND:-vllm}"                    # vllm | llamacpp (run_setups.py follows this)
export HF_HOME="${HF_HOME:-$HOME/.cache/huggingface}"
LOG_DIR="${LOG_DIR:-$HOME/pdf-server-logs}"

# vLLM (started natively - Surya's own vLLM start needs Docker)
VLLM_ENV_DIR="${VLLM_ENV_DIR:-$HOME/envs/vllm}"
SURYA_MODEL="${SURYA_MODEL:-datalab-to/surya-ocr-2.5}"
VLLM_PORT="${VLLM_PORT:-8765}"
VLLM_GPUS="${VLLM_GPUS:-0}"
VLLM_GPU_TYPE="${VLLM_GPU_TYPE:-4090}"        # 4090=24GB, a100=40GB, h100=80GB, l40s, t4 ...
VLLM_DTYPE="${VLLM_DTYPE:-bfloat16}"          # float16 on T4 / V100
VLLM_GPU_MEM="${VLLM_GPU_MEM:-0.85}"          # lower if the GPU is shared
VLLM_MAX_NUM_SEQS="${VLLM_MAX_NUM_SEQS:-32}"
VLLM_MAX_BATCHED_TOKENS="${VLLM_MAX_BATCHED_TOKENS:-8192}"
VLLM_MAX_MODEL_LEN="${VLLM_MAX_MODEL_LEN:-24576}"
VLLM_MTP="${VLLM_MTP:-1}"                     # set 0 if vLLM refuses to start
VLLM_STARTUP_TIMEOUT="${VLLM_STARTUP_TIMEOUT:-900}"

LLAMA_CPP_BIN="${LLAMA_CPP_BIN:-$HOME/llama.cpp/build/bin/llama-server}"

# =============================================================================
info() { echo "[$(date '+%F %T')] $*"; }
die()  { echo "[$(date '+%F %T')] ERROR: $*" >&2; exit 1; }

VLLM_PID=""
cleanup() {
    if [ -n "$VLLM_PID" ] && kill -0 "$VLLM_PID" 2>/dev/null; then
        info "Stopping vLLM (pid $VLLM_PID)"
        kill "$VLLM_PID" 2>/dev/null || true
        wait "$VLLM_PID" 2>/dev/null || true
    fi
}

vllm_healthy() {
    "$ENV_DIR/bin/python" -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:$VLLM_PORT/health', timeout=3)" >/dev/null 2>&1
}

update_code() {
    [ -d "$REPO_DIR/.git" ] || die "No repo in $REPO_DIR - do the one-time setup first"
    if [ "$NO_PULL" = 1 ]; then
        info "Skipping git pull (--no-pull)"
    else
        git -C "$REPO_DIR" pull --ff-only origin "$BRANCH" \
            || die "git pull failed - check 'git -C $REPO_DIR status'"
    fi
    info "Code at $(git -C "$REPO_DIR" log -1 --format='%h %s')"
}

update_packages() {
    [ -x "$ENV_DIR/bin/python" ] || die "No Python env in $ENV_DIR - do the one-time setup first"
    local req="$REPO_DIR/scripts/requirements.txt" stamp="$ENV_DIR/.requirements_hash" want
    [ -f "$req" ] || { info "WARNING: $req not found - packages not checked"; return 0; }
    want="$(sha256sum < "$req" | cut -c1-16)"
    if [ "$want" != "$(cat "$stamp" 2>/dev/null || true)" ]; then
        info "requirements.txt changed - updating packages"
        "$ENV_DIR/bin/pip" install -r "$req"
        echo "$want" > "$stamp"
    fi
}

start_vllm() {
    export SURYA_INFERENCE_BACKEND=vllm VLLM_GPU_TYPE VLLM_GPUS
    export SURYA_INFERENCE_URL="http://127.0.0.1:$VLLM_PORT/v1"
    if vllm_healthy; then
        info "vLLM already running on port $VLLM_PORT - reusing it"
        return
    fi
    [ -x "$VLLM_ENV_DIR/bin/vllm" ] || die "vLLM not found in $VLLM_ENV_DIR - do the one-time setup first"

    local args=(
        serve "$SURYA_MODEL"
        --host 127.0.0.1 --port "$VLLM_PORT"
        --served-model-name "$SURYA_MODEL"       # Surya checks this name
        --dtype "$VLLM_DTYPE"
        --max-model-len "$VLLM_MAX_MODEL_LEN"
        --max-num-seqs "$VLLM_MAX_NUM_SEQS"
        --max-num-batched-tokens "$VLLM_MAX_BATCHED_TOKENS"
        --gpu-memory-utilization "$VLLM_GPU_MEM"
        --enable-prefix-caching
        --mm-processor-kwargs '{"min_pixels": 3136, "max_pixels": 6291456}'
    )
    [ "$VLLM_MTP" = 1 ] && args+=(--speculative-config '{"method": "mtp", "num_speculative_tokens": 2}')

    local vlog pid waited=0
    vlog="$LOG_DIR/vllm_$(date +%F_%H%M).log"
    info "Starting vLLM on GPU $VLLM_GPUS, port $VLLM_PORT (log: $vlog)"
    CUDA_VISIBLE_DEVICES="$VLLM_GPUS" nohup "$VLLM_ENV_DIR/bin/vllm" "${args[@]}" > "$vlog" 2>&1 &
    pid=$!
    [ "$KEEP_VLLM" = 1 ] || VLLM_PID=$pid      # cleanup() stops it at the end

    until vllm_healthy; do
        kill -0 "$pid" 2>/dev/null || { tail -n 30 "$vlog"; die "vLLM exited during startup (log: $vlog)"; }
        [ "$waited" -ge "$VLLM_STARTUP_TIMEOUT" ] && die "vLLM not ready after ${VLLM_STARTUP_TIMEOUT}s (log: $vlog)"
        sleep 10; waited=$((waited + 10))
        [ $((waited % 60)) -eq 0 ] && info "  still loading model... ${waited}s"
    done
    info "vLLM ready after ${waited}s"
}

push_results() {
    cd "$REPO_DIR"
    local dirs=() d
    for d in papers_md papers_json setup_guides_measurments_test_results; do
        [ -d "$d" ] && dirs+=("$d")
    done
    [ ${#dirs[@]} -eq 0 ] && { info "No result folders to push"; return; }
    git add -- "${dirs[@]}" || info "WARNING: some result folders are in .gitignore"
    if git diff --cached --quiet; then
        info "No new results to commit"; return
    fi
    if ! git commit -m "results: run $(date '+%F %H:%M') on $(hostname -s)" --quiet; then
        info "WARNING: git commit failed - results stay uncommitted"; return
    fi
    git pull --rebase --quiet origin "$BRANCH" && git push --quiet origin "$BRANCH" \
        && info "Results pushed to GitHub" \
        || info "WARNING: push failed - results are committed locally"
}

# =============================================================================
main() {
    NO_PULL=0; PUSH=0; KEEP_VLLM=0
    while [ $# -gt 0 ]; do
        case "$1" in
            --no-pull)   NO_PULL=1 ;;
            --push)      PUSH=1 ;;
            --keep-vllm) KEEP_VLLM=1 ;;
            --script)    SCRIPT="$2"; shift ;;
            -h|--help)   sed -n '2,18p' "$0"; exit 0 ;;
            *)           die "Unknown option: $1 (see --help)" ;;
        esac
        shift
    done
    trap cleanup EXIT INT TERM
    mkdir -p "$LOG_DIR"

    update_code
    update_packages
    case "$BACKEND" in
        vllm)     start_vllm ;;
        llamacpp) [ -x "$LLAMA_CPP_BIN" ] || die "llama-server not found at $LLAMA_CPP_BIN"
                  export SURYA_INFERENCE_BACKEND=llamacpp LLAMA_CPP_BINARY="$LLAMA_CPP_BIN" ;;
        *)        die "BACKEND must be vllm or llamacpp, got $BACKEND" ;;
    esac

    cd "$REPO_DIR"
    [ -f "$SCRIPT" ] || die "$SCRIPT not found in $REPO_DIR"
    [ -d papers ] || die "No papers/ folder in $REPO_DIR"
    [ -n "$(ls papers/*.pdf 2>/dev/null)" ] || info "WARNING: no PDFs in $REPO_DIR/papers"
    mkdir -p papers_md papers_json setup_guides_measurments_test_results

    info "Running $SCRIPT (backend: $BACKEND)"
    local status=0
    "$ENV_DIR/bin/python" -u "$SCRIPT" || status=$?
    [ "$status" -eq 0 ] || info "WARNING: $SCRIPT exited with status $status"

    [ "$PUSH" = 1 ] && push_results
    [ "$KEEP_VLLM" = 1 ] && vllm_healthy && info "vLLM left running (stop: pkill -f 'vllm serve')"
    info "Done"
    return "$status"
}

# Wrapped in main() so bash reads the whole file first - safe when git pull updates it.
main "$@"