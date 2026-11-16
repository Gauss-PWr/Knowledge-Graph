#!/usr/bin/env bash
# =============================================================================
# run_db_worker.sh - pull the latest code, start vLLM (Surya OCR) and run the
# database worker scripts/db_server_actions.py, which converts every book in
# the `books` table that is not converted yet and writes md + marker_json back.
#
# Assumes the one-time setup is done (repo cloned, envs installed, .env with
# PGHOST/PGPORT/PGUSER/PGPASSWORD/PGSSLMODE/PGDATABASE in the repo root, or the
# same variables in ~/.pdf_server.env).
# Every run:
#   1. git pull
#   2. reinstalls Python packages only if requirements.txt (repo root) changed
#   3. checks the database and that there is something to convert
#   4. starts vLLM (or reuses one that is already running)
#   5. runs scripts/db_server_actions.py
#   6. stops vLLM (unless --keep-vllm)
# Ctrl+C / kill: the book being converted is marked 'failed' and vLLM stopped.
#
# Usage (inside tmux):
#   bash ~/<repo>/scripts/run_db_worker.sh [--keep-vllm] [--no-pull]
#
# Settings: override any variable below in ~/.pdf_server.env
# =============================================================================
set -euo pipefail

# Everything in the settings file is exported, so the Python side sees it too
# (PG* database settings, SURYA_INFERENCE_PARALLEL, ...).
if [ -f "$HOME/.pdf_server.env" ]; then set -a; source "$HOME/.pdf_server.env"; set +a; fi

REPO_DIR="${REPO_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"   # repo = folder above scripts/
BRANCH="${BRANCH:-$(git -C "$REPO_DIR" rev-parse --abbrev-ref HEAD 2>/dev/null || echo main)}"
SCRIPT="${SCRIPT:-scripts/db_server_actions.py}"
ENV_DIR="${ENV_DIR:-$HOME/envs/marker}"
export HF_HOME="${HF_HOME:-$HOME/.cache/huggingface}"
LOG_DIR="${LOG_DIR:-$HOME/pdf-server-logs}"

# vLLM (started natively - Surya's own vLLM start needs Docker)
VLLM_ENV_DIR="${VLLM_ENV_DIR:-$HOME/envs/vllm}"
SURYA_MODEL="${SURYA_MODEL:-datalab-to/surya-ocr-2.5}"
VLLM_PORT="${VLLM_PORT:-8765}"
VLLM_GPUS="${VLLM_GPUS:-0}"
VLLM_GPU_TYPE="${VLLM_GPU_TYPE:-4090}"        # 4090=24GB, a100=40GB, h100=80GB, l40s, t4 ...
VLLM_DTYPE="${VLLM_DTYPE:-bfloat16}"          # float16 on T4 / V100
VLLM_GPU_MEM="${VLLM_GPU_MEM:-0.85}"          # fraction of the whole GPU; ignored when VLLM_GPU_GB is set
VLLM_GPU_GB="${VLLM_GPU_GB:-5}"               # GB for vLLM (model 1.3 GB + cache); empty = use VLLM_GPU_MEM
MARKER_GPU_GB="${MARKER_GPU_GB:-4}"           # GB Marker's own models need next to vLLM
MARKER_GPUS="${MARKER_GPUS:-${VLLM_GPUS%%,*}}" # GPU for Marker's models; default = vLLM's, which the memory check counts
VLLM_MAX_NUM_SEQS="${VLLM_MAX_NUM_SEQS:-32}"
VLLM_MAX_BATCHED_TOKENS="${VLLM_MAX_BATCHED_TOKENS:-8192}"
VLLM_MAX_MODEL_LEN="${VLLM_MAX_MODEL_LEN:-24576}"
VLLM_MTP="${VLLM_MTP:-0}"                        # set 0 if vLLM refuses to start
VLLM_EXTRA_ARGS="${VLLM_EXTRA_ARGS:---enforce-eager}"
export VLLM_USE_FLASHINFER_SAMPLER="${VLLM_USE_FLASHINFER_SAMPLER:-0}" # extra vllm serve flags, e.g. --enforce-eager
VLLM_STARTUP_TIMEOUT="${VLLM_STARTUP_TIMEOUT:-900}"

# =============================================================================
info() { echo "[$(date '+%F %T')] $*"; }
die()  { echo "[$(date '+%F %T')] ERROR: $*" >&2; exit 1; }

VLLM_PID=""
PY_PID=""
cleanup() {
    if [ -n "$VLLM_PID" ] && kill -0 "$VLLM_PID" 2>/dev/null; then
        info "Stopping vLLM (pid $VLLM_PID)"
        kill "$VLLM_PID" 2>/dev/null || true
        wait "$VLLM_PID" 2>/dev/null || true
    fi
    pkill -f "surya\..*server" 2>/dev/null || true      # Surya's keep-alive helpers hold GPU memory
}

# Ctrl+C / kill: let the worker mark its current book as failed, then exit.
on_signal() {
    if [ -n "$PY_PID" ] && kill -0 "$PY_PID" 2>/dev/null; then
        info "Stop requested - letting the worker mark the current book as failed"
        kill -TERM "$PY_PID" 2>/dev/null || true
    else
        info "Stop requested"
        exit 130
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
    local req="$REPO_DIR/requirements.txt" stamp="$ENV_DIR/.requirements_hash" want
    if [ ! -f "$req" ] && [ -f "$REPO_DIR/scripts/requirements.txt" ]; then
        info "WARNING: no requirements.txt in the repo root - using scripts/requirements.txt"
        req="$REPO_DIR/scripts/requirements.txt"
    fi
    [ -f "$req" ] || { info "WARNING: requirements.txt not found - packages not checked"; return 0; }
    want="$(sha256sum < "$req" | cut -c1-16)"
    if [ "$want" != "$(cat "$stamp" 2>/dev/null || true)" ]; then
        info "requirements.txt changed - updating packages"
        "$ENV_DIR/bin/pip" install -r "$req"
        echo "$want" > "$stamp"
    fi
}

# Connects with the same settings as the worker (database/config.py) and counts
# the books it would convert, so vLLM is not loaded for nothing.
check_database() {
    if [ ! -f "$REPO_DIR/.env" ] && [ -z "${PGHOST:-}" ]; then
        die "No database settings: create $REPO_DIR/.env (PGHOST, PGPORT, PGUSER, PGPASSWORD, PGSSLMODE, PGDATABASE) or put them in ~/.pdf_server.env"
    fi
    local todo
    todo=$(cd "$REPO_DIR" && "$ENV_DIR/bin/python" - <<'EOF'
import sys
sys.path.insert(0, ".")
from sqlalchemy import text
from database.connection import get_db_connection
with get_db_connection().connect() as conn:
    print(conn.execute(text("""
        SELECT count(*) FROM books b
        WHERE NOT EXISTS (SELECT 1 FROM book_report r
            WHERE r.book_id = b.book_id AND r.config_name = 'config_final'
              AND r.status IN ('running', 'converted'))
        AND (SELECT count(*) FROM book_report r
            WHERE r.book_id = b.book_id AND r.config_name = 'config_final'
              AND r.status = 'failed') < 3
    """)).scalar())
EOF
    ) || die "Cannot reach the database or its tables (see the error above)"
    info "Database OK: $todo book(s) to convert"
    [ "$todo" -gt 0 ] || { info "Nothing to convert - not starting vLLM"; exit 0; }
}

start_vllm() {
    # Tell Surya to use our vLLM instead of starting its own (Docker) one.
    # Surya refuses a server whose model name differs from SURYA_MODEL_CHECKPOINT.
    export SURYA_INFERENCE_BACKEND=vllm VLLM_GPU_TYPE VLLM_GPUS
    export SURYA_INFERENCE_URL="http://127.0.0.1:$VLLM_PORT/v1"
    export SURYA_MODEL_CHECKPOINT="$SURYA_MODEL"
    if vllm_healthy; then
        info "vLLM already running on port $VLLM_PORT - reusing it"
        return
    fi
    [ -x "$VLLM_ENV_DIR/bin/vllm" ] || die "vLLM not found in $VLLM_ENV_DIR - do the one-time setup first"

    # Shared GPU: size vLLM in GB and check that vLLM + Marker fit into what is free right now
    local total free need
    read -r total free < <(nvidia-smi --id="${VLLM_GPUS%%,*}" --query-gpu=memory.total,memory.free \
                           --format=csv,noheader,nounits 2>/dev/null | tr -d ',') || true
    if [ -n "${total:-}" ]; then
        [ -n "$VLLM_GPU_GB" ] && VLLM_GPU_MEM=$(awk -v g="$VLLM_GPU_GB" -v t="$total" 'BEGIN{printf "%.3f", g*1024/t}')
        need=$(awk -v u="$VLLM_GPU_MEM" -v t="$total" -v m="$MARKER_GPU_GB" 'BEGIN{printf "%d", u*t + m*1024}')
        info "GPU $VLLM_GPUS: $((free/1024)) of $((total/1024)) GB free; vLLM gets $VLLM_GPU_MEM of it, run needs ~$((need/1024)) GB"
        [ "$free" -ge "$need" ] || die "Not enough free GPU memory ($((free/1024)) GB free, ~$((need/1024)) GB needed) - someone else is using the GPU. Try later or lower VLLM_GPU_GB / MARKER_GPU_GB"
    fi

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
    # shellcheck disable=SC2206  # split on purpose: "--a --b x" -> separate flags
    [ -n "$VLLM_EXTRA_ARGS" ] && args+=($VLLM_EXTRA_ARGS)

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

run_worker() {
    local wlog status=0
    wlog="$LOG_DIR/worker_$(date +%F_%H%M).log"
    info "Running $SCRIPT on GPU $MARKER_GPUS (log: $wlog)"
    # Runs in the background so Ctrl+C / kill reach on_signal(); tee ignores them
    # so the worker's last log lines (marking the book failed) are not lost.
    CUDA_VISIBLE_DEVICES="$MARKER_GPUS" "$ENV_DIR/bin/python" -u "$SCRIPT" \
        > >(trap '' INT TERM; exec tee -a "$wlog") 2>&1 &
    PY_PID=$!
    while :; do
        wait "$PY_PID" && { status=0; break; } || status=$?
        kill -0 "$PY_PID" 2>/dev/null || break      # exited (not just interrupted by a signal)
    done
    PY_PID=""
    return "$status"
}

# =============================================================================
main() {
    NO_PULL=0; KEEP_VLLM=0
    while [ $# -gt 0 ]; do
        case "$1" in
            --no-pull)   NO_PULL=1 ;;
            --keep-vllm) KEEP_VLLM=1 ;;
            -h|--help)   sed -n '2,23p' "$0"; exit 0 ;;
            *)           die "Unknown option: $1 (see --help)" ;;
        esac
        shift
    done
    trap cleanup EXIT
    trap on_signal INT TERM
    mkdir -p "$LOG_DIR"

    update_code
    update_packages
    cd "$REPO_DIR"
    [ -f "$SCRIPT" ] || die "$SCRIPT not found in $REPO_DIR"
    check_database
    start_vllm

    local status=0
    run_worker || status=$?
    [ "$status" -eq 0 ] || info "WARNING: $SCRIPT exited with status $status"

    [ "$KEEP_VLLM" = 1 ] && vllm_healthy && info "vLLM left running (stop: pkill -f 'vllm serve')"
    info "Done"
    return "$status"
}

# Wrapped in main() so bash reads the whole file first - safe when git pull updates it.
main "$@"
