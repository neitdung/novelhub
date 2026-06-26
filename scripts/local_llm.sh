#!/usr/bin/env bash
set -euo pipefail

LLAMA_CPP_DIR=${LLAMA_CPP_DIR:-/home/bloot/tools/llama.cpp}
LLAMA_SERVER=${LLAMA_SERVER:-${LLAMA_CPP_DIR}/build/bin/llama-server}
MODEL=${MODEL:-${LLAMA_CPP_DIR}/models/qwen3.6-mtp/Qwen3.6-35B-A3B-UD-IQ4_NL.gguf}
HOST=${LLAMA_HOST:-127.0.0.1}
PORT=${LLAMA_PORT:-10124}
CTX_SIZE=${LLAMA_CTX_SIZE:-32768}
GPU_LAYERS=${LLAMA_GPU_LAYERS:-auto-safe}
THREADS=${LLAMA_THREADS:-12}
BATCH_SIZE=${LLAMA_BATCH_SIZE:-512}
UBATCH_SIZE=${LLAMA_UBATCH_SIZE:-128}
MLLOCK=${LLAMA_MLOCK:-0}
NO_MMAP=${LLAMA_NO_MMAP:-0}
MTP=${LLAMA_MTP:-0}
STOP_EXISTING=${LLAMA_STOP_EXISTING:-1}
REFRESH_GLOSSARY=${REFRESH_TRANSLATION_GLOSSARY:-1}
PROJECT_ROOT=${PROJECT_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}
GLOSSARY_INPUT=${TRANSLATION_GLOSSARY_INPUT:-${PROJECT_ROOT}/backend/data/wiki.xlsx}
GLOSSARY_OUTPUT=${TRANSLATION_GLOSSARY_PATH:-${PROJECT_ROOT}/backend/data/translation_glossary.json}

get_free_vram_mib() {
    if ! command -v rocm-smi >/dev/null 2>&1; then
        return 1
    fi

    python3 - <<'PY'
import re
import subprocess

try:
    out = subprocess.check_output(
        ["rocm-smi", "--showmeminfo", "vram"],
        text=True,
        stderr=subprocess.DEVNULL,
    )
except Exception:
    raise SystemExit(1)

total = used = None
for line in out.splitlines():
    if "VRAM Total Memory" in line:
        total = int(re.findall(r"(\d+)", line)[-1])
    elif "VRAM Total Used Memory" in line:
        used = int(re.findall(r"(\d+)", line)[-1])

if total is None or used is None:
    raise SystemExit(1)
print(max(0, (total - used) // (1024 * 1024)))
PY
}

choose_gpu_layers() {
    if [ "$GPU_LAYERS" != "auto-safe" ]; then
        echo "$GPU_LAYERS"
        return
    fi

    local free_mib
    free_mib=$(get_free_vram_mib 2>/dev/null || echo 0)
    echo "Detected free VRAM: ${free_mib} MiB" >&2

    # RX 6600 XT has 8 GiB VRAM. Keep large headroom for ROCm, KV, and desktop.
    # RX 6600 8GB safer but much more aggressive
    if [ "$free_mib" -ge 8000 ]; then
        echo 15
    elif [ "$free_mib" -ge 6800 ]; then
        echo 14
    elif [ "$free_mib" -ge 6200 ]; then
        echo 12
    elif [ "$free_mib" -ge 5500 ]; then
        echo 10
    elif [ "$free_mib" -ge 4500 ]; then
        echo 8
    elif [ "$free_mib" -ge 3500 ]; then
        echo 6
    else
        echo 4
    fi
}

stop_existing_llama() {
    mapfile -t pids < <(pgrep -f "llama-server" || true)
    if [ "${#pids[@]}" -eq 0 ]; then
        return
    fi

    echo "Stopping existing llama-server processes: ${pids[*]}"
    kill "${pids[@]}" 2>/dev/null || true

    for _ in $(seq 1 10); do
        mapfile -t remaining < <(pgrep -f "llama-server" || true)
        if [ "${#remaining[@]}" -eq 0 ]; then
            return
        fi
        sleep 0.5
    done

    mapfile -t remaining < <(pgrep -f "llama-server" || true)
    if [ "${#remaining[@]}" -gt 0 ]; then
        echo "Force-killing remaining llama-server processes: ${remaining[*]}"
        kill -9 "${remaining[@]}" 2>/dev/null || true
        sleep 1
    fi

    mapfile -t remaining < <(pgrep -f "llama-server" || true)
    if [ "${#remaining[@]}" -gt 0 ]; then
        echo "Warning: some llama-server processes could not be killed:" >&2
        ps -o pid,stat,etime,cmd -p "$(IFS=,; echo "${remaining[*]}")" >&2 || true
        echo "Processes in D state are stuck in the kernel and usually require reboot." >&2
    fi
}

refresh_translation_glossary() {
    if [ "$REFRESH_GLOSSARY" != "1" ]; then
        return
    fi

    if [ ! -f "$GLOSSARY_INPUT" ]; then
        echo "Translation glossary source not found, skipping: $GLOSSARY_INPUT" >&2
        return
    fi

    local python_bin="${PROJECT_ROOT}/backend/.venv/bin/python"
    if [ ! -x "$python_bin" ]; then
        python_bin=$(command -v python3 || true)
    fi
    if [ -z "$python_bin" ]; then
        echo "Python not found; skipping translation glossary refresh." >&2
        return
    fi

    echo "Refreshing translation glossary: $GLOSSARY_OUTPUT"
    if ! "$python_bin" "${PROJECT_ROOT}/scripts/export_wiki_glossary.py" \
        --input "$GLOSSARY_INPUT" \
        --output "$GLOSSARY_OUTPUT"; then
        echo "Warning: failed to refresh translation glossary; continuing with existing file." >&2
    fi

    echo "Building CN-VN name pairs: ${PROJECT_ROOT}/backend/data/cn_vn_pairs.json"
    if ! "$python_bin" "${PROJECT_ROOT}/scripts/build_cn_vn_pairs.py" \
        --glossary "$GLOSSARY_OUTPUT" \
        --output "${PROJECT_ROOT}/backend/data/cn_vn_pairs.json"; then
        echo "Warning: failed to build CN-VN pairs; continuing without them." >&2
    fi
}

if [ ! -x "$LLAMA_SERVER" ]; then
    echo "llama-server not found or not executable: $LLAMA_SERVER" >&2
    exit 1
fi

if [ ! -f "$MODEL" ]; then
    echo "Model not found: $MODEL" >&2
    echo "Download it from unsloth/Qwen3.6-35B-A3B-MTP-GGUF first." >&2
    exit 1
fi

if [ "$STOP_EXISTING" = "1" ]; then
    stop_existing_llama
fi

refresh_translation_glossary

if ss -ltn "( sport = :$PORT )" | grep -q LISTEN; then
    echo "Port $PORT is still busy after cleanup:" >&2
    ss -ltnp "( sport = :$PORT )" >&2 || true
    exit 1
fi

RESOLVED_GPU_LAYERS=$(choose_gpu_layers)
echo "Using GPU layers: $RESOLVED_GPU_LAYERS"
echo "Using context size: $CTX_SIZE"
echo "Using MTP: $MTP"

args=(
    "$LLAMA_SERVER"
    -m "$MODEL" \
    -c "$CTX_SIZE" \
    -ngl "$RESOLVED_GPU_LAYERS" \
    -t "$THREADS" \
    --host "$HOST" \
    --port "$PORT" \
    --batch-size "$BATCH_SIZE" \
    --ubatch-size "$UBATCH_SIZE" \
    -fa on \
    --reasoning off \
    -np 1
)

if [ "$MTP" = "1" ]; then
    args+=(
        --spec-type draft-mtp
        --spec-draft-n-max 2
        --spec-draft-ngl "$RESOLVED_GPU_LAYERS"
    )
fi

if [ "$MLLOCK" = "1" ]; then
    args+=(--mlock)
fi

if [ "$NO_MMAP" = "1" ]; then
    args+=(--no-mmap)
fi


exec "${args[@]}"
