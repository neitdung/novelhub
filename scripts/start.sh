#!/bin/bash
# Start script for NovelHub (FastAPI backend)
set -e

cd "$(dirname "$0")/.."

# Load .env first so it can override all defaults
if [ -f ".env" ]; then
    set -a
    source .env
    set +a
    echo "Loaded .env"
fi

# Parse CLI flags
START_LOCAL_LLM=${START_LOCAL_LLM:-0}
while [ $# -gt 0 ]; do
    case "$1" in
        --local) START_LOCAL_LLM=1; shift ;;
        *) shift ;;
    esac
done

# Apply defaults for any variables not set by .env
PORT=${PORT:-8000}
OPENCODE_HOST=${OPENCODE_HOST:-127.0.0.1}
OPENCODE_PORT=${OPENCODE_PORT:-4096}
CLEAR_PYTHON_CACHE=${CLEAR_PYTHON_CACHE:-0}
RESTART_APP=${RESTART_APP:-0}
INSTALL_DEPS=${INSTALL_DEPS:-0}
APP_URL=${APP_URL:-http://127.0.0.1:${PORT}}
LLAMA_PORT=${LLAMA_PORT:-10124}
LLAMA_HOST=${LLAMA_HOST:-127.0.0.1}

echo "=== NovelHub ==="
echo "Working directory: $(pwd)"
echo "App URL: $APP_URL"
echo "OpenCode port: $OPENCODE_PORT"
echo "Local LLM port: $LLAMA_PORT"

if [ "$RESTART_APP" != "1" ] && curl -s "$APP_URL/api/health" >/dev/null 2>&1; then
    echo "NovelHub is already running. Set RESTART_APP=1 to restart it."
    exit 0
fi

# Resolve the Python runtime
BACKEND_DIR="backend"
PYTHON=${PYTHON:-${BACKEND_DIR}/.venv/bin/python}

if [ ! -x "$PYTHON" ]; then
    if [ "$INSTALL_DEPS" = "1" ]; then
        echo "Creating virtual environment in ${BACKEND_DIR}/.venv..."
        python3 -m venv "${BACKEND_DIR}/.venv"
    else
        echo "Error: No usable virtual environment found at ${BACKEND_DIR}/.venv"
        echo "Create/install it once with:"
        echo "  INSTALL_DEPS=1 scripts/start.sh"
        exit 1
    fi
fi

PYTHON=${PYTHON:-${BACKEND_DIR}/.venv/bin/python}
if [ ! -x "$PYTHON" ]; then
    echo "Error: Python runtime not found: $PYTHON"
    echo "Install python3-venv, then run:"
    echo "  INSTALL_DEPS=1 scripts/start.sh"
    exit 1
fi

echo "Using Python: $($PYTHON -c 'import sys; print(sys.executable)')"

if ! "$PYTHON" -c "import fastapi" >/dev/null 2>&1; then
    if [ "$INSTALL_DEPS" = "1" ]; then
        echo "Installing missing Python dependencies..."
        "$PYTHON" -m ensurepip --upgrade >/dev/null 2>&1 || true
        cd "${BACKEND_DIR}" && "${PYTHON}" -m pip install --upgrade pip && "${PYTHON}" -m pip install -e . && cd ..
    else
        echo "Error: Python dependency 'fastapi' is not installed in $($PYTHON -c 'import sys; print(sys.executable)')"
        echo "Install dependencies once with:"
        echo "  INSTALL_DEPS=1 scripts/start.sh"
        exit 1
    fi
fi

if [ "$CLEAR_PYTHON_CACHE" = "1" ]; then
    echo "Clearing Python cache..."
    find backend -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
fi

# Start local LLM if enabled
LLM_PID=""
LLM_STARTED="no"
if [ "$START_LOCAL_LLM" = "1" ] && [ -x "scripts/local/local_llm.sh" ]; then
    if curl -s "http://${LLAMA_HOST}:${LLAMA_PORT}/v1/models" >/dev/null 2>&1; then
        echo "Local LLM already running on port ${LLAMA_PORT}"
        LLM_PID="existing"
        LLM_STARTED="yes"
    else
        echo "Starting local LLM on ${LLAMA_HOST}:${LLAMA_PORT}..."
        scripts/local/local_llm.sh &
        LLM_PID=$!

        echo "Waiting for local LLM (up to 120s)..."
        for i in $(seq 1 120); do
            if curl -s "http://${LLAMA_HOST}:${LLAMA_PORT}/v1/models" >/dev/null 2>&1; then
                echo "Local LLM is ready (PID $LLM_PID)"
                LLM_STARTED="yes"
                break
            fi
            if [ $((i % 10)) -eq 0 ]; then
                echo "  ... still waiting (${i}s)"
            fi
            sleep 1
        done
        if [ "$LLM_STARTED" != "yes" ]; then
            echo "Warning: Local LLM did not start within 120s."
            echo "LLM features will use fallback."
            LLM_PID=""
        fi
    fi
elif [ "$START_LOCAL_LLM" = "1" ]; then
    echo "Local LLM script not found at scripts/local/local_llm.sh."
    echo "LLM features will use fallback."
fi

export OPENCODE_PORT

echo "Rendering OpenCode project prompt config..."
"$PYTHON" scripts/harness/render_opencode_config.py

cleanup() {
    echo ""
    echo "Shutting down..."
    if [ -n "$OPENCODE_PID" ] && [ "$OPENCODE_PID" != "existing" ] && kill -0 "$OPENCODE_PID" 2>/dev/null; then
        echo "Stopping OpenCode server (PID $OPENCODE_PID)..."
        kill "$OPENCODE_PID" 2>/dev/null || true
    fi
    if [ -n "$LLM_PID" ] && [ "$LLM_PID" != "existing" ] && kill -0 "$LLM_PID" 2>/dev/null; then
        echo "Stopping local LLM (PID $LLM_PID)..."
        kill "$LLM_PID" 2>/dev/null || true
    fi
    if [ -n "$APP_PID" ] && kill -0 "$APP_PID" 2>/dev/null; then
        echo "Stopping NovelHub (PID $APP_PID)..."
        kill "$APP_PID" 2>/dev/null || true
    fi
    wait 2>/dev/null || true
    echo "Done."
}
trap cleanup EXIT INT TERM

# Start OpenCode server if available
OPENCODE_PID=""
if command -v opencode &>/dev/null; then
    echo "OpenCode binary found: $(which opencode)"

    if curl -s "http://${OPENCODE_HOST}:${OPENCODE_PORT}/global/health" >/dev/null 2>&1; then
        echo "OpenCode server already running on port ${OPENCODE_PORT}"
        OPENCODE_PID="existing"
    else
        echo "Starting OpenCode server on ${OPENCODE_HOST}:${OPENCODE_PORT}..."
        opencode serve --port "$OPENCODE_PORT" --hostname "$OPENCODE_HOST" &
        OPENCODE_PID=$!

        echo "Waiting for OpenCode server (up to 30s)..."
        for i in $(seq 1 30); do
            if curl -s "http://${OPENCODE_HOST}:${OPENCODE_PORT}/global/health" >/dev/null 2>&1; then
                echo "OpenCode server is ready (PID $OPENCODE_PID)"
                break
            fi
            if [ $i -eq 30 ]; then
                echo "Warning: OpenCode server did not start in 30s."
                OPENCODE_PID=""
            fi
            sleep 1
        done
    fi
else
    echo "OpenCode not found. The app will fall back to OpenRouter if configured."
    echo "To install: curl -fsSL https://opencode.ai/install | bash"
fi

echo ""
echo "Starting NovelHub backend on port ${PORT}..."
echo "Local LLM: $([ "$LLM_STARTED" = "yes" ] && echo "AVAILABLE on port $LLAMA_PORT" || echo "NOT AVAILABLE")"
echo "OpenCode: $([ -n "$OPENCODE_PID" ] && echo "AVAILABLE on port $OPENCODE_PORT" || echo "NOT AVAILABLE")"
echo ""

# Stop any existing process on app port only for explicit restarts.
if [ "$RESTART_APP" = "1" ]; then
    fuser -k "${PORT}/tcp" 2>/dev/null || true
    sleep 1
fi

# Run the backend with uvicorn
cd "${BACKEND_DIR}" && "$PYTHON" -m uvicorn app.main:app --host 0.0.0.0 --port "$PORT" --reload &
APP_PID=$!
cd ..

echo "NovelHub started (PID $APP_PID)"
echo "Press Ctrl+C to stop."
echo ""

wait $APP_PID
