from __future__ import annotations

import hashlib
from pathlib import Path

import aiosqlite


async def create_novel(
    db: aiosqlite.Connection,
    title: str,
    author: str,
    language: str,
    file_path: Path,
    file_hash: str,
) -> int:
    cursor = await db.execute(
        "INSERT INTO novels (title, author, language, file_path, file_hash)"
        " VALUES (?, ?, ?, ?, ?)",
        (title, author, language, str(file_path), file_hash),
    )
    await db.commit()
    return cursor.lastrowid or 0


async def get_novel(
    db: aiosqlite.Connection, novel_id: int
) -> dict[str, object] | None:
    cursor = await db.execute("SELECT * FROM novels WHERE id = ?", (novel_id,))
    row = await cursor.fetchone()
    if row is None:
        return None
    return {
        "id": row[0],
        "title": row[1],
        "author": row[2],
        "language": row[3],
        "file_path": row[4],
        "file_hash": row[5],
    }


async def list_novels(db: aiosqlite.Connection) -> list[dict[str, object]]:
    cursor = await db.execute("SELECT * FROM novels ORDER BY title")
    rows = await cursor.fetchall()
    return [
        {
            "id": row[0],
            "title": row[1],
            "author": row[2],
            "language": row[3],
            "file_path": row[4],
            "file_hash": row[5],
        }
        for row in rows
    ]


async def delete_novel(db: aiosqlite.Connection, novel_id: int) -> bool:
    cursor = await db.execute("DELETE FROM novels WHERE id = ?", (novel_id,))
    await db.commit()
    return cursor.rowcount > 0


def compute_file_hash(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


async def check_duplicate(db: aiosqlite.Connection, file_hash: str) -> bool:
    cursor = await db.execute(
        "SELECT COUNT(*) FROM novels WHERE file_hash = ?", (file_hash,)
    )
    row = await cursor.fetchone()
    return row is not None and row[0] > 0


async def create_bookmark(
    db: aiosqlite.Connection,
    novel_id: int,
    chapter_id: int,
    position: int,
    title: str,
) -> int:
    cursor = await db.execute(
        "INSERT INTO bookmarks (novel_id, chapter_id, position, title)"
        " VALUES (?, ?, ?, ?)",
        (novel_id, chapter_id, position, title),
    )
    await db.commit()
    return cursor.lastrowid or 0


async def get_bookmarks(
    db: aiosqlite.Connection, novel_id: int
) -> list[dict[str, object]]:
    cursor = await db.execute(
        "SELECT id, novel_id, chapter_id, position, title"
        " FROM bookmarks WHERE novel_id = ? ORDER BY created_at",
        (novel_id,),
    )
    rows = await cursor.fetchall()
    return [
        {
            "id": row[0],
            "novel_id": row[1],
            "chapter_id": row[2],
            "position": row[3],
            "title": row[4],
        }
        for row in rows
    ]


async def delete_bookmark(
    db: aiosqlite.Connection, novel_id: int, bookmark_id: int
) -> bool:
    cursor = await db.execute(
        "DELETE FROM bookmarks WHERE id = ? AND novel_id = ?",
        (bookmark_id, novel_id),
    )
    await db.commit()
    return cursor.rowcount > 0


async def get_progress(
    db: aiosqlite.Connection, novel_id: int
) -> dict[str, object] | None:
    cursor = await db.execute(
        "SELECT novel_id, chapter_id, position FROM reading_progress"
        " WHERE novel_id = ?",
        (novel_id,),
    )
    row = await cursor.fetchone()
    if row is None:
        return None
    return {"novel_id": row[0], "chapter_id": row[1], "position": row[2]}


async def update_progress(
    db: aiosqlite.Connection, novel_id: int, chapter_id: int, position: int
) -> None:
    await db.execute(
        "INSERT INTO reading_progress (novel_id, chapter_id, position)"
        " VALUES (?, ?, ?)"
        " ON CONFLICT(novel_id) DO UPDATE SET chapter_id=?, position=?",
        (novel_id, chapter_id, position, chapter_id, position),
    )
    await db.commit()
