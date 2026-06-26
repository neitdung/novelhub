from __future__ import annotations

import logging
import time
from collections.abc import Callable, Mapping
from typing import Any

logger = logging.getLogger("scraper")


class ScrapeError(Exception):
    """Raised when a chapter cannot be scraped."""


class BaseScraper:
    """Base scraper with retry and progress callback support."""

    def __init__(self, max_retries: int = 3, delay: float = 5.0):
        self.max_retries = max_retries
        self.delay = delay

    def fetch_chapter(self, chapter_number: int, url: str) -> str:
        raise NotImplementedError

    def scrape_one(
        self,
        chapter_number: int,
        url: str,
        on_progress: Callable[[int, int, str], None] | None = None,
    ) -> str:
        last_error: str | None = None
        for attempt in range(1, self.max_retries + 1):
            try:
                text = self.fetch_chapter(chapter_number, url)
                if on_progress:
                    on_progress(chapter_number, 0, f"done ({len(text)} chars)")
                return text
            except Exception as e:
                last_error = str(e)
                logger.warning(
                    f"Chapter {chapter_number} attempt"
                    f" {attempt}/{self.max_retries} failed: {last_error}"
                )
                if attempt < self.max_retries:
                    backoff = self.delay * (2 ** (attempt - 1))
                    logger.info(f"Backing off {backoff}s before retry")
                    time.sleep(backoff)
        raise ScrapeError(
            f"Chapter {chapter_number} failed after"
            f" {self.max_retries} attempts: {last_error}"
        )

    def scrape_range(
        self,
        start: int,
        end: int,
        url_template: str,
        url_params: dict[str, str] | None = None,
        on_progress: Callable[[int, int, str], None] | None = None,
    ) -> dict[int, str]:
        params = url_params or {}
        results: dict[int, str] = {}
        consecutive_failures = 0
        total = end - start + 1

        for chapter_num in range(start, end + 1):
            try:
                url = url_template.format(
                    chapter_id=str(chapter_num),
                    chapter_number=str(chapter_num),
                    **params,
                )
                text = self.scrape_one(chapter_num, url, on_progress)
                results[chapter_num] = text
                consecutive_failures = 0
                if on_progress:
                    on_progress(chapter_num, total, f"done ({len(text)} chars)")
            except ScrapeError as e:
                consecutive_failures += 1
                status = f"failed: {e}"
                if on_progress:
                    on_progress(chapter_num, total, status)
                if consecutive_failures >= 3:
                    logger.error(
                        f"Aborting after {consecutive_failures}"
                        " consecutive failures"
                    )
                    break

            time.sleep(self.delay)

        return results


class ShubaScraper(BaseScraper):
    """69shuba.com scraper using Scrapling with Cloudflare bypass."""

    SKIP_PREFIXES = (
        "loadAdv", "window.", "var ", "function", "if (", "for (",
        "$(doc", "return", "pubfuturetag", "googletag", "setTimeout",
        "clearTimeout",
    )

    def __init__(
        self, max_retries: int = 3, delay: float = 5.0, css_selector: str = ".txtnav"
    ):
        super().__init__(max_retries, delay)
        self.css_selector = css_selector

    def fetch_chapter(self, chapter_number: int, url: str) -> str:
        try:
            from scrapling.fetchers import StealthyFetcher
        except ImportError:
            raise ScrapeError("scrapling not installed; run: pip install scrapling")

        logger.info(f"Fetching chapter {chapter_number} from {url}")
        page = StealthyFetcher.fetch(
            url,
            headless=True,
            solve_cloudflare=True,
            network_idle=True,
            google_search=False,
        )

        title = page.css("title::text").get()
        if title:
            logger.info(f"Chapter {chapter_number} title: {title.strip()}")

        text = self._extract_clean_text(page)
        if not text or len(text) < 100:
            raise ScrapeError(
                f"Chapter {chapter_number} text too short"
                f" ({len(text)} chars) — possible scrape failure"
            )

        logger.info(f"Chapter {chapter_number}: {len(text)} chars extracted")
        return text

    def _extract_clean_text(self, page: Any) -> str:
        raw_texts = page.css(self.css_selector).css("::text").getall()

        lines: list[str] = []
        for t in raw_texts:
            t = str(t).strip()
            if not t or len(t) < 2:
                continue
            if any(t.startswith(p) for p in self.SKIP_PREFIXES):
                continue
            if t.startswith(tuple("0123456789")) and "-" in t and len(t) < 15:
                continue
            lines.append(t)

        return "\n\n".join(lines)


def get_scraper(source: Mapping[str, object]) -> BaseScraper:
    """Factory: return the appropriate scraper for a source config."""
    name = str(source.get("name", "")).lower()
    css_selector = str(source.get("css_selector", ".txtnav"))

    if "69shuba" in name or "shuba" in name:
        return ShubaScraper(css_selector=css_selector)
    return ShubaScraper(css_selector=css_selector)
