#!/bin/bash
# Clear all data for a fresh start

cd "$(dirname "$0")/.."

echo "Clearing all data for fresh start..."

# Stop app if running
PORT=${PORT:-8000}
fuser -k "${PORT}/tcp" 2>/dev/null || true

# Remove database (stored in backend by default)
DB_PATH="${NOVELHUB_DB_PATH:-backend/novelhub.db}"
if [ -f "$DB_PATH" ]; then
    rm -f "$DB_PATH"
    echo "  - Removed $DB_PATH"
fi

# Remove Python cache in backend
find backend -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find backend -name "*.pyc" -delete 2>/dev/null
echo "  - Cleared Python cache in backend/"

echo ""
echo "Done! You can now start fresh with:"
echo "  ./scripts/start.sh"
