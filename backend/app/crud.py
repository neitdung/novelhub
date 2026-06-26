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


# --- Source Operations ---

async def create_source(
    db: aiosqlite.Connection,
    name: str,
    url_template: str,
    css_selector: str,
    language: str,
    active: bool,
) -> int:
    cursor = await db.execute(
        "INSERT INTO sources (name, url_template, css_selector, language, active)"
        " VALUES (?, ?, ?, ?, ?)",
        (name, url_template, css_selector, language, int(active)),
    )
    await db.commit()
    return cursor.lastrowid or 0


async def list_sources(db: aiosqlite.Connection) -> list[dict[str, object]]:
    cursor = await db.execute("SELECT * FROM sources ORDER BY name")
    rows = await cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    return [dict(zip(columns, row)) for row in rows]


async def get_source(
    db: aiosqlite.Connection, source_id: int
) -> dict[str, object] | None:
    cursor = await db.execute("SELECT * FROM sources WHERE id = ?", (source_id,))
    row = await cursor.fetchone()
    if row is None:
        return None
    columns = [desc[0] for desc in cursor.description]
    return dict(zip(columns, row))


async def update_source(
    db: aiosqlite.Connection, source_id: int, updates: dict[str, object]
) -> bool:
    if not updates:
        return False
    sets = ", ".join(f"{k} = ?" for k in updates)
    values = list(updates.values()) + [source_id]
    cursor = await db.execute(
        f"UPDATE sources SET {sets}, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
        values,
    )
    await db.commit()
    return cursor.rowcount > 0


async def delete_source(db: aiosqlite.Connection, source_id: int) -> bool:
    cursor = await db.execute("DELETE FROM sources WHERE id = ?", (source_id,))
    await db.commit()
    return cursor.rowcount > 0


async def count_novels_for_source(db: aiosqlite.Connection, source_id: int) -> int:
    cursor = await db.execute(
        "SELECT COUNT(*) FROM novels WHERE source_id = ?", (source_id,)
    )
    row = await cursor.fetchone()
    return row[0] if row else 0


# --- Ingest Job Operations ---

async def create_ingest_job(
    db: aiosqlite.Connection,
    novel_id: int,
    source_id: int,
    chapter_start: int,
    chapter_end: int,
) -> int:
    cursor = await db.execute(
        "INSERT INTO ingest_jobs"
        " (novel_id, source_id, chapter_start, chapter_end, status)"
        " VALUES (?, ?, ?, ?, 'pending')",
        (novel_id, source_id, chapter_start, chapter_end),
    )
    await db.commit()
    return cursor.lastrowid or 0


async def update_ingest_job(
    db: aiosqlite.Connection,
    job_id: int,
    status: str | None = None,
    progress: int | None = None,
    error: str | None = None,
) -> None:
    updates: dict[str, object] = {}
    if status is not None:
        updates["status"] = status
    if progress is not None:
        updates["progress"] = progress
    if error is not None:
        updates["error"] = error
    if updates:
        sets = ", ".join(f"{k} = ?" for k in updates)
        values = list(updates.values()) + [job_id]
        sql = (
            "UPDATE ingest_jobs SET"
            f" {sets}, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
        )
        await db.execute(sql, values)
        await db.commit()


async def get_ingest_job(
    db: aiosqlite.Connection, job_id: int
) -> dict[str, object] | None:
    cursor = await db.execute("SELECT * FROM ingest_jobs WHERE id = ?", (job_id,))
    row = await cursor.fetchone()
    if row is None:
        return None
    columns = [desc[0] for desc in cursor.description]
    return dict(zip(columns, row))


async def list_ingest_jobs(
    db: aiosqlite.Connection, novel_id: int
) -> list[dict[str, object]]:
    cursor = await db.execute(
        "SELECT * FROM ingest_jobs WHERE novel_id = ? ORDER BY created_at DESC",
        (novel_id,),
    )
    rows = await cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    return [dict(zip(columns, row)) for row in rows]


# --- Chapter Operations ---

async def create_chapter(
    db: aiosqlite.Connection,
    novel_id: int,
    chapter_number: int,
    title: str,
    content: str,
    raw_content: str | None = None,
    source_url: str | None = None,
    ingest_job_id: int | None = None,
) -> int:
    cursor = await db.execute(
        "INSERT INTO chapters"
        " (novel_id, chapter_number, title, content,"
        "  raw_content, source_url, ingest_job_id)"
        " VALUES (?, ?, ?, ?, ?, ?, ?)",
        (
            novel_id,
            chapter_number,
            title,
            content,
            raw_content,
            source_url,
            ingest_job_id,
        ),
    )
    await db.commit()
    return cursor.lastrowid or 0


async def list_chapters(
    db: aiosqlite.Connection, novel_id: int
) -> list[dict[str, object]]:
    cursor = await db.execute(
        "SELECT id, novel_id, chapter_number, title,"
        " CASE WHEN raw_content IS NOT NULL AND raw_content != ''"
        "  THEN 1 ELSE 0 END as has_raw,"
        " CASE WHEN content IS NOT NULL AND content != ''"
        "  THEN 1 ELSE 0 END as has_content,"
        " is_corrected, corrected_at, created_at"
        " FROM chapters WHERE novel_id = ? ORDER BY chapter_number",
        (novel_id,),
    )
    rows = await cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    return [dict(zip(columns, row)) for row in rows]


async def get_chapter(
    db: aiosqlite.Connection, chapter_id: int
) -> dict[str, object] | None:
    cursor = await db.execute("SELECT * FROM chapters WHERE id = ?", (chapter_id,))
    row = await cursor.fetchone()
    if row is None:
        return None
    columns = [desc[0] for desc in cursor.description]
    return dict(zip(columns, row))


async def update_chapter(
    db: aiosqlite.Connection,
    chapter_id: int,
    title: str | None = None,
    content: str | None = None,
    raw_content: str | None = None,
) -> bool:
    updates = {}
    if title is not None:
        updates["title"] = title
    if content is not None:
        updates["content"] = content
    if raw_content is not None:
        updates["raw_content"] = raw_content
    if title is not None or content is not None or raw_content is not None:
        updates["is_corrected"] = 1  # type: ignore[assignment]
    if not updates:
        return False
    sets = ", ".join(f"{k} = ?" for k in updates)
    values = list(updates.values())
    cursor = await db.execute(
        f"UPDATE chapters SET {sets}, corrected_at = CURRENT_TIMESTAMP WHERE id = ?",
        values + [chapter_id],
    )
    await db.commit()
    return cursor.rowcount > 0


async def delete_chapter(db: aiosqlite.Connection, chapter_id: int) -> bool:
    cursor = await db.execute("DELETE FROM chapters WHERE id = ?", (chapter_id,))
    await db.commit()
    return cursor.rowcount > 0


async def delete_chapters_range(
    db: aiosqlite.Connection, novel_id: int, start: int, end: int
) -> int:
    cursor = await db.execute(
        "DELETE FROM chapters WHERE novel_id = ? AND chapter_number BETWEEN ? AND ?",
        (novel_id, start, end),
    )
    await db.commit()
    return cursor.rowcount


async def delete_chapters_batch(
    db: aiosqlite.Connection, chapter_ids: list[int]
) -> int:
    if not chapter_ids:
        return 0
    placeholders = ",".join("?" for _ in chapter_ids)
    cursor = await db.execute(
        f"DELETE FROM chapters WHERE id IN ({placeholders})",
        chapter_ids,
    )
    await db.commit()
    return cursor.rowcount


async def swap_chapters(
    db: aiosqlite.Connection, chapter_id_a: int, chapter_id_b: int
) -> bool:
    async with db.execute(
        "SELECT chapter_number FROM chapters WHERE id = ?", (chapter_id_a,)
    ) as cursor:
        row_a = await cursor.fetchone()
    async with db.execute(
        "SELECT chapter_number FROM chapters WHERE id = ?", (chapter_id_b,)
    ) as cursor:
        row_b = await cursor.fetchone()
    if row_a is None or row_b is None:
        return False
    num_a, num_b = row_a[0], row_b[0]
    await db.execute(
        "UPDATE chapters SET chapter_number = ? WHERE id = ?", (-1, chapter_id_a)
    )
    await db.execute(
        "UPDATE chapters SET chapter_number = ? WHERE id = ?", (num_a, chapter_id_b)
    )
    await db.execute(
        "UPDATE chapters SET chapter_number = ? WHERE id = ?", (num_b, chapter_id_a)
    )
    await db.commit()
    return True


async def get_chapter_by_number(
    db: aiosqlite.Connection, novel_id: int, chapter_number: int
) -> dict[str, object] | None:
    cursor = await db.execute(
        "SELECT * FROM chapters WHERE novel_id = ? AND chapter_number = ?",
        (novel_id, chapter_number),
    )
    row = await cursor.fetchone()
    if row is None:
        return None
    columns = [desc[0] for desc in cursor.description]
    return dict(zip(columns, row))


async def update_novel_source(
    db: aiosqlite.Connection, novel_id: int, source_id: int, source_type: str = "scrape"
) -> None:
    await db.execute(
        "UPDATE novels SET source_id = ?, source_type = ? WHERE id = ?",
        (source_id, source_type, novel_id),
    )
    await db.commit()
