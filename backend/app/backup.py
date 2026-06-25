from __future__ import annotations

import hashlib
import json
import os
import shutil
import zipfile
from datetime import UTC, datetime
from io import BytesIO

from .database import get_db_path
from .migrations import get_migrations


async def create_backup() -> bytes:
    db_path = get_db_path()

    manifest = {
        "version": 1,
        "schema_version": max(get_migrations().keys()),
        "created_at": datetime.now(UTC).isoformat(),
        "database_checksum": "",
        "files": [],
    }

    with open(db_path, "rb") as f:
        db_bytes = f.read()
        manifest["database_checksum"] = hashlib.sha256(db_bytes).hexdigest()

    files = ["novelhub.db"]
    manifest["files"] = files

    buffer = BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("manifest.json", json.dumps(manifest, indent=2))
        zf.writestr("novelhub.db", db_bytes)

    return buffer.getvalue()


async def validate_backup(backup_data: bytes) -> dict[str, object]:
    try:
        with zipfile.ZipFile(BytesIO(backup_data), "r") as zf:
            if "manifest.json" not in zf.namelist():
                return {"valid": False, "error": "Missing manifest.json"}

            manifest = json.loads(zf.read("manifest.json"))

            required_fields = ["version", "schema_version", "created_at"]
            for field in required_fields:
                if field not in manifest:
                    return {"valid": False, "error": f"Missing field: {field}"}

            current_schema = max(get_migrations().keys())
            if manifest["schema_version"] > current_schema:
                return {
                    "valid": False,
                    "error": f"Schema version {manifest['schema_version']} "
                    f"not supported (max: {current_schema})",
                }

            return {
                "valid": True,
                "manifest": manifest,
            }
    except zipfile.BadZipFile:
        return {"valid": False, "error": "Invalid ZIP file"}
    except json.JSONDecodeError:
        return {"valid": False, "error": "Invalid manifest JSON"}


async def restore_backup(backup_data: bytes) -> dict[str, str]:
    validation = await validate_backup(backup_data)
    if not validation["valid"]:
        error_msg = str(validation.get("error", "Unknown error"))
        return {"status": "error", "error": error_msg}

    db_path = get_db_path()
    backup_path = db_path + ".backup"

    shutil.copy2(db_path, backup_path)

    try:
        with zipfile.ZipFile(BytesIO(backup_data), "r") as zf:
            zf.extract("novelhub.db", os.path.dirname(db_path) or ".")
            extracted = os.path.join(os.path.dirname(db_path) or ".", "novelhub.db")
            os.replace(extracted, db_path)

        return {"status": "restored", "backup": backup_path}
    except Exception as e:
        if os.path.exists(backup_path):
            shutil.move(backup_path, db_path)
        return {"status": "error", "error": str(e)}
