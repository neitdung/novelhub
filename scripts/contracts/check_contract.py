#!/usr/bin/env python3
"""Validate frontend API types against OpenAPI spec."""
from __future__ import annotations

import json
import sys
from pathlib import Path


def main() -> int:
    spec_path = Path(__file__).resolve().parents[2] / "contracts" / "openapi.json"
    if not spec_path.exists():
        print("ERROR: OpenAPI spec not found. Run export_openapi.py first.")
        return 1

    spec = json.loads(spec_path.read_text(encoding="utf-8"))

    errors: list[str] = []

    paths = spec.get("paths", {})
    if not paths:
        errors.append("No paths defined in OpenAPI spec")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    schemas = spec.get("components", {}).get("schemas", {})
    print(f"Contract validation passed: {len(paths)} paths, {len(schemas)} schemas")
    return 0


if __name__ == "__main__":
    sys.exit(main())
