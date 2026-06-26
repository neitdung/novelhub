from __future__ import annotations

import aiosqlite


async def run_migrations(db_path: str = "novelhub.db") -> None:
    async with aiosqlite.connect(db_path) as db:
        await db.execute("PRAGMA journal_mode=WAL")
        await db.execute("PRAGMA foreign_keys=ON")

        await db.execute("""
            CREATE TABLE IF NOT EXISTS schema_version (
                version INTEGER PRIMARY KEY,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor = await db.execute("SELECT MAX(version) FROM schema_version")
        row = await cursor.fetchone()
        current_version: int = row[0] if row is not None and row[0] is not None else 0

        migrations = get_migrations()
        for version, sql in sorted(migrations.items()):
            if version > current_version:
                await db.executescript(sql)
                await db.execute(
                    "INSERT INTO schema_version (version) VALUES (?)", (version,)
                )
                await db.commit()


def get_migrations() -> dict[int, str]:
    return {
        1: """
            CREATE TABLE IF NOT EXISTS novels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT NOT NULL DEFAULT '',
                language TEXT NOT NULL DEFAULT 'en',
                file_path TEXT NOT NULL,
                file_hash TEXT NOT NULL UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS chapters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                novel_id INTEGER NOT NULL,
                chapter_number INTEGER NOT NULL,
                title TEXT,
                content TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (novel_id) REFERENCES novels(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS bookmarks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                novel_id INTEGER NOT NULL,
                chapter_id INTEGER NOT NULL,
                position INTEGER NOT NULL DEFAULT 0,
                title TEXT NOT NULL DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (novel_id) REFERENCES novels(id) ON DELETE CASCADE,
                FOREIGN KEY (chapter_id) REFERENCES chapters(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS reading_progress (
                novel_id INTEGER PRIMARY KEY,
                chapter_id INTEGER NOT NULL,
                position INTEGER NOT NULL DEFAULT 0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (novel_id) REFERENCES novels(id) ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS idx_chapters_novel_id ON chapters(novel_id);
            CREATE INDEX IF NOT EXISTS idx_novels_file_hash ON novels(file_hash);
            CREATE INDEX IF NOT EXISTS idx_bookmarks_novel_id ON bookmarks(novel_id);
        """,
        2: """
            CREATE TABLE IF NOT EXISTS entities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                novel_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                entity_type TEXT NOT NULL DEFAULT 'character',
                attributes TEXT DEFAULT '{}',
                source_chapter INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (novel_id) REFERENCES novels(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS entity_aliases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entity_id INTEGER NOT NULL,
                alias TEXT NOT NULL,
                normalized TEXT NOT NULL,
                is_primary INTEGER NOT NULL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (entity_id) REFERENCES entities(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS entity_mentions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entity_id INTEGER NOT NULL,
                chapter_id INTEGER NOT NULL,
                position INTEGER NOT NULL DEFAULT 0,
                context TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (entity_id) REFERENCES entities(id) ON DELETE CASCADE,
                FOREIGN KEY (chapter_id) REFERENCES chapters(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS entity_relationships (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                novel_id INTEGER NOT NULL,
                source_entity_id INTEGER NOT NULL,
                target_entity_id INTEGER NOT NULL,
                relationship_type TEXT NOT NULL DEFAULT 'related_to',
                attributes TEXT DEFAULT '{}',
                source_chapter INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (novel_id) REFERENCES novels(id) ON DELETE CASCADE,
                FOREIGN KEY (source_entity_id)
                    REFERENCES entities(id) ON DELETE CASCADE,
                FOREIGN KEY (target_entity_id)
                    REFERENCES entities(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS wiki_pages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                novel_id INTEGER NOT NULL,
                entity_id INTEGER,
                title TEXT NOT NULL,
                content TEXT NOT NULL DEFAULT '',
                language TEXT NOT NULL DEFAULT 'en',
                version INTEGER NOT NULL DEFAULT 1,
                source_chapters TEXT DEFAULT '[]',
                prompt_version TEXT DEFAULT 'v1',
                is_published INTEGER NOT NULL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (novel_id) REFERENCES novels(id) ON DELETE CASCADE,
                FOREIGN KEY (entity_id)
                    REFERENCES entities(id) ON DELETE SET NULL
            );

            CREATE INDEX IF NOT EXISTS idx_entities_novel_id
                ON entities(novel_id);
            CREATE INDEX IF NOT EXISTS idx_entities_type
                ON entities(entity_type);
            CREATE INDEX IF NOT EXISTS idx_entity_aliases_entity_id
                ON entity_aliases(entity_id);
            CREATE INDEX IF NOT EXISTS idx_entity_aliases_normalized
                ON entity_aliases(normalized);
            CREATE INDEX IF NOT EXISTS idx_entity_mentions_entity_id
                ON entity_mentions(entity_id);
            CREATE INDEX IF NOT EXISTS idx_entity_mentions_chapter_id
                ON entity_mentions(chapter_id);
            CREATE INDEX IF NOT EXISTS idx_entity_relationships_novel
                ON entity_relationships(novel_id);
            CREATE INDEX IF NOT EXISTS idx_wiki_pages_novel_id
                ON wiki_pages(novel_id);
            CREATE INDEX IF NOT EXISTS idx_wiki_pages_entity_id
                ON wiki_pages(entity_id);
        """,
        3: """
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                novel_id INTEGER NOT NULL,
                title TEXT NOT NULL DEFAULT 'New Chat',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (novel_id) REFERENCES novels(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id INTEGER NOT NULL,
                role TEXT NOT NULL DEFAULT 'user',
                content TEXT NOT NULL DEFAULT '',
                citations TEXT DEFAULT '[]',
                tool_calls TEXT DEFAULT '[]',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (conversation_id)
                    REFERENCES conversations(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                novel_id INTEGER NOT NULL,
                chapter_id INTEGER,
                event_type TEXT NOT NULL DEFAULT 'general',
                title TEXT NOT NULL DEFAULT '',
                description TEXT DEFAULT '',
                importance INTEGER NOT NULL DEFAULT 1,
                participants TEXT DEFAULT '[]',
                attributes TEXT DEFAULT '{}',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (novel_id) REFERENCES novels(id) ON DELETE CASCADE,
                FOREIGN KEY (chapter_id) REFERENCES chapters(id) ON DELETE SET NULL
            );

            CREATE INDEX IF NOT EXISTS idx_conversations_novel_id
                ON conversations(novel_id);
            CREATE INDEX IF NOT EXISTS idx_messages_conversation_id
                ON messages(conversation_id);
            CREATE INDEX IF NOT EXISTS idx_events_novel_id
                ON events(novel_id);
            CREATE INDEX IF NOT EXISTS idx_events_chapter_id
                ON events(chapter_id);
            CREATE INDEX IF NOT EXISTS idx_events_type
                ON events(event_type);
        """,
        4: """
            CREATE TABLE IF NOT EXISTS sources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                url_template TEXT NOT NULL,
                css_selector TEXT NOT NULL DEFAULT '.txtnav',
                language TEXT NOT NULL DEFAULT 'zh',
                active INTEGER NOT NULL DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS ingest_jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                novel_id INTEGER NOT NULL,
                source_id INTEGER NOT NULL,
                chapter_start INTEGER NOT NULL,
                chapter_end INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                progress INTEGER NOT NULL DEFAULT 0,
                error TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (novel_id) REFERENCES novels(id) ON DELETE CASCADE,
                FOREIGN KEY (source_id) REFERENCES sources(id) ON DELETE CASCADE
            );

            ALTER TABLE novels ADD COLUMN source_type TEXT NOT NULL DEFAULT 'upload';
            ALTER TABLE novels ADD COLUMN source_id INTEGER REFERENCES sources(id);

            ALTER TABLE chapters ADD COLUMN raw_content TEXT;
            ALTER TABLE chapters ADD COLUMN source_url TEXT;
            ALTER TABLE chapters ADD COLUMN is_corrected INTEGER NOT NULL DEFAULT 0;
            ALTER TABLE chapters ADD COLUMN corrected_at TIMESTAMP;
            ALTER TABLE chapters ADD COLUMN ingest_job_id INTEGER
                REFERENCES ingest_jobs(id);

            CREATE INDEX IF NOT EXISTS idx_novels_source_type
                ON novels(source_type);
            CREATE INDEX IF NOT EXISTS idx_chapters_ingest_job
                ON chapters(ingest_job_id);
            CREATE INDEX IF NOT EXISTS idx_ingest_jobs_novel ON ingest_jobs(novel_id);
            CREATE INDEX IF NOT EXISTS idx_ingest_jobs_status ON ingest_jobs(status);
        """,
    }
