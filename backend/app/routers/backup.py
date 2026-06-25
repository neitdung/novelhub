from __future__ import annotations

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

from ..backup import create_backup, restore_backup, validate_backup

router = APIRouter(prefix="/api/backup", tags=["backup"])


@router.post("/create")
async def create_backup_endpoint() -> Response:
    backup_data = await create_backup()
    return Response(
        content=backup_data,
        media_type="application/zip",
        headers={
            "Content-Disposition": "attachment; filename=novelhub-backup.zip"
        },
    )


@router.post("/validate")
async def validate_backup_endpoint(backup_data: bytes) -> dict[str, object]:
    result = await validate_backup(backup_data)
    return result


@router.post("/restore")
async def restore_backup_endpoint(backup_data: bytes) -> dict[str, str]:
    result = await restore_backup(backup_data)
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["error"])
    return result
