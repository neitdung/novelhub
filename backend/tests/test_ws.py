from __future__ import annotations

import pytest

from app.ws import ConnectionManager, broadcast_progress


@pytest.mark.asyncio
async def test_connection_manager_connect() -> None:
    test_manager = ConnectionManager()
    assert len(test_manager.active_connections) == 0


@pytest.mark.asyncio
async def test_broadcast_progress_no_connections() -> None:
    await broadcast_progress(999, {"type": "progress", "percent": 50})
