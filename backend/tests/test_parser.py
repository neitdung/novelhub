from __future__ import annotations

from app.parser import detect_language, split_chapters


def test_detect_language_english() -> None:
    content = "This is an English novel with multiple chapters."
    assert detect_language(content) == "en"


def test_detect_language_chinese() -> None:
    content = "这是一本中文小说，包含多个章节。"
    assert detect_language(content) == "zh"


def test_split_chapters_english() -> None:
    content = """Chapter 1: The Beginning

This is the first chapter.

Chapter 2: The Middle

This is the second chapter.

Chapter 3: The End

This is the third chapter."""

    chapters = split_chapters(content, "en")
    assert len(chapters) == 3
    assert chapters[0]["chapter_number"] == 1
    assert chapters[1]["chapter_number"] == 2
    assert chapters[2]["chapter_number"] == 3


def test_split_chapters_chinese() -> None:
    content = """第一章 开始

这是第一章的内容。

第二章 中间

这是第二章的内容。"""

    chapters = split_chapters(content, "zh")
    assert len(chapters) == 2
    assert chapters[0]["chapter_number"] == 1
    assert chapters[1]["chapter_number"] == 2


def test_split_chapters_vietnamese() -> None:
    content = """Chương 1: Khởi đầu

Đây là chương đầu tiên.

Chương 2: Giữa

Đây là chương thứ hai."""

    chapters = split_chapters(content, "vi")
    assert len(chapters) == 2


def test_split_chapters_fallback() -> None:
    content = "Paragraph one.\n\nParagraph two.\n\nParagraph three.\n\nParagraph four."
    chapters = split_chapters(content, "en")
    assert len(chapters) >= 1


def test_split_chapters_empty() -> None:
    content = ""
    chapters = split_chapters(content, "en")
    assert len(chapters) == 1
    assert chapters[0]["chapter_number"] == 1
