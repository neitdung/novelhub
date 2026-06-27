#!/bin/bash
# install.sh — Install all NovelHub project dependencies
#
# Usage:
#   ./scripts/install.sh          # Install all dependencies
#   ./scripts/install.sh --help   # Show this help
#
# Environment variables:
#   BACKEND_DIR   Backend directory (default: backend)
#   FRONTEND_DIR  Frontend directory (default: frontend)
#   VERBOSE       Show detailed output (default: 0)

set -euo pipefail

cd "$(dirname "$0")/.."

# Load .env if present
if [ -f ".env" ]; then
    set -a
    source .env
    set +a
fi

BACKEND_DIR="${BACKEND_DIR:-backend}"
FRONTEND_DIR="${FRONTEND_DIR:-frontend}"
VERBOSE="${VERBOSE:-0}"

show_help() {
    cat <<EOF
install.sh — Install all NovelHub project dependencies

Usage:
  ./scripts/install.sh              Install all dependencies
  ./scripts/install.sh --help       Show this help

Installs:
  - Backend Python virtual environment and dependencies (via uv sync)
  - Frontend npm packages (via npm ci)

Environment variables:
  BACKEND_DIR   Backend directory (default: backend)
  FRONTEND_DIR  Frontend directory (default: frontend)
  VERBOSE       Set to 1 for verbose output (default: 0)
EOF
    exit 0
}

if [ "${1:-}" = "--help" ] || [ "${1:-}" = "-h" ]; then
    show_help
fi

echo "=== NovelHub Dependency Installer ==="
echo ""

# ------------------------------------------------------------------
# Backend: Python virtual environment and dependencies
# ------------------------------------------------------------------
echo "[1/2] Installing backend dependencies..."
if [ "$VERBOSE" = "1" ]; then
    (cd "$BACKEND_DIR" && uv sync)
else
    echo "  Running: cd $BACKEND_DIR && uv sync"
    (cd "$BACKEND_DIR" && uv sync 2>&1 | tail -5)
fi

# Verify backend install
if [ ! -d "$BACKEND_DIR/.venv" ]; then
    echo "ERROR: Backend .venv not created; uv sync may have failed." >&2
    exit 1
fi
echo "  Backend dependencies installed."

# ------------------------------------------------------------------
# Frontend: npm packages
# ------------------------------------------------------------------
echo ""
echo "[2/2] Installing frontend dependencies..."
if [ "$VERBOSE" = "1" ]; then
    (cd "$FRONTEND_DIR" && npm ci)
else
    echo "  Running: cd $FRONTEND_DIR && npm ci"
    (cd "$FRONTEND_DIR" && npm ci 2>&1 | tail -5)
fi

# Verify frontend install
if [ ! -d "$FRONTEND_DIR/node_modules" ]; then
    echo "ERROR: Frontend node_modules not created; npm ci may have failed." >&2
    exit 1
fi
echo "  Frontend dependencies installed."

# ------------------------------------------------------------------
# Summary
# ------------------------------------------------------------------
echo ""
echo "=== All dependencies installed successfully ==="
echo "  Backend:  $BACKEND_DIR/.venv"
echo "  Frontend: $FRONTEND_DIR/node_modules"
echo ""
echo "You can now start the project with:"
echo "  make start"
echo ""
