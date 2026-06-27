#!/bin/bash
# Stop script for NovelHub
set -e

cd "$(dirname "$0")/.."

# Load .env first so it can override all defaults
if [ -f ".env" ]; then
    set -a
    source .env
    set +a
    echo "Loaded .env"
fi

PORT=${PORT:-8000}
FRONTEND_PORT=${FRONTEND_PORT:-3000}
OPENCODE_PORT=${OPENCODE_PORT:-4096}

echo "=== Stopping NovelHub ==="

# Stop the main backend application
if fuser "${PORT}/tcp" >/dev/null 2>&1 || (command -v lsof >/dev/null 2>&1 && lsof -i:"${PORT}" >/dev/null 2>&1); then
    echo "Stopping NovelHub backend running on port ${PORT}..."
    fuser -k "${PORT}/tcp" 2>/dev/null || true
    if command -v lsof >/dev/null 2>&1; then
        PID=$(lsof -t -i:"${PORT}" 2>/dev/null)
        if [ -n "$PID" ]; then
            kill $PID 2>/dev/null || kill -9 $PID 2>/dev/null || true
        fi
    fi
    echo "NovelHub backend stopped."
else
    echo "NovelHub backend is not running on port ${PORT}."
fi

# Stop OpenCode server if running
if fuser "${OPENCODE_PORT}/tcp" >/dev/null 2>&1 || (command -v lsof >/dev/null 2>&1 && lsof -i:"${OPENCODE_PORT}" >/dev/null 2>&1); then
    echo "Stopping OpenCode server running on port ${OPENCODE_PORT}..."
    fuser -k "${OPENCODE_PORT}/tcp" 2>/dev/null || true
    if command -v lsof >/dev/null 2>&1; then
        PID=$(lsof -t -i:"${OPENCODE_PORT}" 2>/dev/null)
        if [ -n "$PID" ]; then
            kill $PID 2>/dev/null || kill -9 $PID 2>/dev/null || true
        fi
    fi
    echo "OpenCode server stopped."
else
    echo "OpenCode server is not running on port ${OPENCODE_PORT}."
fi

# Stop Next.js frontend dev server if running
if fuser "${FRONTEND_PORT}/tcp" >/dev/null 2>&1 || (command -v lsof >/dev/null 2>&1 && lsof -i:"${FRONTEND_PORT}" >/dev/null 2>&1); then
    echo "Stopping frontend dev server running on port ${FRONTEND_PORT}..."
    fuser -k "${FRONTEND_PORT}/tcp" 2>/dev/null || true
    if command -v lsof >/dev/null 2>&1; then
        PID=$(lsof -t -i:"${FRONTEND_PORT}" 2>/dev/null)
        if [ -n "$PID" ]; then
            kill $PID 2>/dev/null || kill -9 $PID 2>/dev/null || true
        fi
    fi
    echo "Frontend dev server stopped."
else
    echo "Frontend dev server is not running on port ${FRONTEND_PORT}."
fi

echo "Done."
