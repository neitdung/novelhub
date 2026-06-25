from __future__ import annotations

from app.security import (
    sanitize_html,
    sanitize_markdown,
    sanitize_url,
    validate_entity_name,
    validate_input,
    validate_novel_title,
)


def test_sanitize_html() -> None:
    result = sanitize_html("<script>alert('xss')</script>")
    assert result == "&lt;script&gt;alert(&#x27;xss&#x27;)&lt;/script&gt;"
    assert sanitize_html("Hello World") == "Hello World"


def test_sanitize_url_valid() -> None:
    assert sanitize_url("https://example.com") == "https://example.com"
    assert sanitize_url("http://example.com/path") == "http://example.com/path"
    assert sanitize_url("mailto:user@example.com") == "mailto:user@example.com"


def test_sanitize_url_invalid() -> None:
    assert sanitize_url("javascript:alert(1)") is None
    assert sanitize_url("file:///etc/passwd") is None
    assert sanitize_url("http://192.168.1.1") is None


def test_sanitize_markdown() -> None:
    text = "Hello <script>alert(1)</script> World"
    result = sanitize_markdown(text)
    assert "<script>" not in result
    assert "Hello" in result


def test_validate_input() -> None:
    assert validate_input("Hello") == "Hello"
    assert validate_input("x" * 10001) is None
    assert validate_input("Hello\x00World") is None


def test_validate_entity_name() -> None:
    assert validate_entity_name("Alice") == "Alice"
    assert validate_entity_name("") is None
    assert validate_entity_name("x" * 501) is None
    assert validate_entity_name("Alice<script>") is None


def test_validate_novel_title() -> None:
    assert validate_novel_title("My Novel") == "My Novel"
    assert validate_novel_title("") is None
    assert validate_novel_title("x" * 1001) is None
