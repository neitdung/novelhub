from __future__ import annotations

import pytest

from app.backup import create_backup, validate_backup


@pytest.mark.asyncio
async def test_create_backup() -> None:
    backup_data = await create_backup()
    assert len(backup_data) > 0


@pytest.mark.asyncio
async def test_validate_backup() -> None:
    backup_data = await create_backup()
    result = await validate_backup(backup_data)
    assert result["valid"] is True
    assert "manifest" in result


@pytest.mark.asyncio
async def test_validate_invalid_backup() -> None:
    result = await validate_backup(b"not a zip file")
    assert result["valid"] is False
    assert "error" in result
