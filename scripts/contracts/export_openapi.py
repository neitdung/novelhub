#!/usr/bin/env python3
"""Export OpenAPI spec from FastAPI app."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = ROOT / "backend"
CONTRACTS_DIR = ROOT / "contracts"


def main() -> int:
    backend_python = BACKEND_DIR / ".venv" / "bin" / "python"
    if not backend_python.exists():
        backend_python = Path(sys.executable)

    result = subprocess.run(
        [str(backend_python), "-c", "from app.main import app; import json; print(json.dumps(app.openapi()))"],
        cwd=str(BACKEND_DIR),
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"ERROR: Failed to export OpenAPI spec: {result.stderr}")
        return 1

    spec = json.loads(result.stdout)
    output_path = CONTRACTS_DIR / "openapi.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(spec, indent=2) + "\n", encoding="utf-8")
    print(f"OpenAPI spec written to {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
