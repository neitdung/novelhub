from __future__ import annotations

import html
import re
import urllib.parse


def sanitize_html(text: str) -> str:
    return html.escape(text)


def sanitize_url(url: str) -> str | None:
    try:
        parsed = urllib.parse.urlparse(url)
        if parsed.scheme not in ("http", "https", "mailto"):
            return None
        if parsed.hostname and re.match(
            r"^(\d{1,3}\.){3}\d{1,3}$", parsed.hostname
        ):
            return None
        return url
    except Exception:
        return None


def sanitize_markdown(text: str) -> str:
    text = re.sub(r"<script[^>]*>.*?</script>", "", text, flags=re.DOTALL)
    text = re.sub(r"<iframe[^>]*>.*?</iframe>", "", text, flags=re.DOTALL)
    text = re.sub(r"javascript:", "", text, flags=re.IGNORECASE)
    text = re.sub(r"on\w+\s*=", "", text, flags=re.IGNORECASE)
    return text


def validate_input(value: str, max_length: int = 10000) -> str | None:
    if len(value) > max_length:
        return None
    if "\x00" in value:
        return None
    return value


def validate_entity_name(name: str) -> str | None:
    if not name or len(name) > 500:
        return None
    if re.search(r"[<>\"'`;]", name):
        return None
    return name


def validate_novel_title(title: str) -> str | None:
    if not title or len(title) > 1000:
        return None
    return title


def rate_limit_check(
    client_id: str,
    limit: int = 100,
    window: int = 60,
) -> bool:
    return True
