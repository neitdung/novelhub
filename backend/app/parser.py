from __future__ import annotations

import re
from pathlib import Path

CHAPTER_PATTERNS = {
    "en": [
        r"(?:^|\n)\s*Chapter\s+(\d+)(?:\s*[:\-.]\s*(.+?))?(?:\n|$)",
        r"(?:^|\n)\s*CHAPTER\s+(\d+)(?:\s*[:\-.]\s*(.+?))?(?:\n|$)",
        r"(?:^|\n)\s*Ch\.?\s*(\d+)(?:\s*[:\-.]\s*(.+?))?(?:\n|$)",
    ],
    "zh": [
        r"(?:^|\n)\s*第([一二三四五六七八九十百千\d]+)章(?:\s*(.+?))?(?:\n|$)",
        r"(?:^|\n)\s*第([一二三四五六七八九十百千\d]+)节(?:\s*(.+?))?(?:\n|$)",
    ],
    "vi": [
        r"(?:^|\n)\s*Chương\s+(\d+)(?:\s*[:\-\.]\s*(.+?))?(?:\n|$)",
        r"(?:^|\n)\s*Chuong\s+(\d+)(?:\s*[:\-\.]\s*(.+?))?(?:\n|$)",
    ],
}

VIETNAMESE_PATTERN = re.compile(
    r"[àáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợ"
    r"ùúủũụưứừửữựỳýỷỹỵđ]",
    re.IGNORECASE,
)


def detect_language(content: str) -> str:
    chinese_chars = len(re.findall(r"[\u4e00-\u9fff]", content))
    vietnamese_chars = len(VIETNAMESE_PATTERN.findall(content))

    if chinese_chars > len(content) * 0.1:
        return "zh"
    if vietnamese_chars > len(content) * 0.05:
        return "vi"
    return "en"


def split_chapters(
    content: str, language: str | None = None
) -> list[dict[str, str | int]]:
    if language is None:
        language = detect_language(content)

    patterns = CHAPTER_PATTERNS.get(language, CHAPTER_PATTERNS["en"])

    for pattern in patterns:
        matches = list(re.finditer(pattern, content, re.MULTILINE))
        if matches:
            return _extract_chapters(content, matches)

    return _fallback_chapters(content)


def _extract_chapters(
    content: str, matches: list[re.Match[str]]
) -> list[dict[str, str | int]]:
    chapters: list[dict[str, str | int]] = []

    for i, match in enumerate(matches):
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(content)

        chapter_content = content[start:end].strip()
        has_title = match.lastindex and match.lastindex >= 2
        chapter_title = match.group(2) if has_title else f"Chapter {i + 1}"

        chapters.append(
            {
                "chapter_number": i + 1,
                "title": chapter_title or f"Chapter {i + 1}",
                "content": chapter_content,
            }
        )

    return chapters


def _fallback_chapters(content: str) -> list[dict[str, str | int]]:
    paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]

    if not paragraphs:
        return [
            {
                "chapter_number": 1,
                "title": "Chapter 1",
                "content": content,
            }
        ]

    chunk_size = max(1, len(paragraphs) // 10) or 1
    chapters: list[dict[str, str | int]] = []

    for i in range(0, len(paragraphs), chunk_size):
        chunk = paragraphs[i : i + chunk_size]
        chapter_num = len(chapters) + 1
        chapters.append(
            {
                "chapter_number": chapter_num,
                "title": f"Chapter {chapter_num}",
                "content": "\n\n".join(chunk),
            }
        )

    return chapters


async def parse_novel(
    file_path: Path, language: str | None = None
) -> list[dict[str, str | int]]:
    content = file_path.read_text(encoding="utf-8-sig")
    return split_chapters(content, language)
