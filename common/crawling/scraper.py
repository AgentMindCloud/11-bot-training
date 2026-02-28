"""Web scraping utilities."""
from __future__ import annotations

import logging
from urllib.parse import urljoin, urlparse

logger = logging.getLogger(__name__)

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; RestaurantBot/1.0; +https://github.com/restaurant-bots)"
    )
}


class WebScraper:
    """Simple synchronous web scraper backed by httpx + BeautifulSoup."""

    def fetch(self, url: str) -> str:
        """Fetch URL and return raw HTML string."""
        try:
            import httpx

            with httpx.Client(follow_redirects=True, timeout=30, headers=_HEADERS) as client:
                response = client.get(url)
                response.raise_for_status()
                return response.text
        except Exception as exc:
            logger.error("fetch(%s) failed: %s", url, exc)
            return ""

    def extract_text(self, html: str) -> str:
        """Return clean plain text from HTML."""
        if not html:
            return ""
        try:
            from bs4 import BeautifulSoup

            soup = BeautifulSoup(html, "html.parser")
            # Remove script / style noise
            for tag in soup(["script", "style", "noscript", "head"]):
                tag.decompose()
            return " ".join(soup.get_text(separator=" ").split())
        except Exception as exc:
            logger.error("extract_text failed: %s", exc)
            return ""

    def extract_links(self, html: str, base_url: str = "") -> list[str]:
        """Return list of absolute href URLs found in HTML."""
        if not html:
            return []
        try:
            from bs4 import BeautifulSoup

            soup = BeautifulSoup(html, "html.parser")
            links: list[str] = []
            for anchor in soup.find_all("a", href=True):
                href: str = anchor["href"]
                if base_url:
                    href = urljoin(base_url, href)
                parsed = urlparse(href)
                if parsed.scheme in ("http", "https"):
                    links.append(href)
            return list(dict.fromkeys(links))  # deduplicate, preserve order
        except Exception as exc:
            logger.error("extract_links failed: %s", exc)
            return []

    def crawl(self, url: str) -> dict:
        """Fetch and parse a URL, returning a structured dict."""
        html = self.fetch(url)
        text = self.extract_text(html)
        links = self.extract_links(html, base_url=url)
        return {"url": url, "html": html, "text": text, "links": links}
