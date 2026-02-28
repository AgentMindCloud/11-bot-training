"""Lightweight web crawler using httpx + BeautifulSoup."""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; RestaurantBots/1.0; +https://myrestaurant.com)"
    )
}


@dataclass
class CrawledPage:
    url: str
    status_code: int
    title: str = ""
    text: str = ""
    links: list[str] = field(default_factory=list)
    emails: list[str] = field(default_factory=list)
    meta: dict[str, str] = field(default_factory=dict)
    raw_html: str = ""


class WebCrawler:
    """Synchronous HTTP crawler."""

    def __init__(
        self,
        timeout: float = 15.0,
        headers: dict[str, str] | None = None,
        follow_redirects: bool = True,
    ) -> None:
        self.timeout = timeout
        self.headers = headers or DEFAULT_HEADERS
        self.follow_redirects = follow_redirects

    def fetch(self, url: str) -> CrawledPage:
        """Fetch a single URL and return a CrawledPage."""
        try:
            with httpx.Client(
                timeout=self.timeout,
                headers=self.headers,
                follow_redirects=self.follow_redirects,
            ) as client:
                response = client.get(url)
            return self._parse(url, response)
        except httpx.RequestError as exc:
            logger.warning("Failed to fetch %s: %s", url, exc)
            return CrawledPage(url=url, status_code=0)

    def _parse(self, url: str, response: httpx.Response) -> CrawledPage:
        soup = BeautifulSoup(response.text, "html.parser")
        title = soup.title.string.strip() if soup.title and soup.title.string else ""
        text = soup.get_text(separator=" ", strip=True)

        # Extract all links
        links = [
            urljoin(url, a["href"])
            for a in soup.find_all("a", href=True)
            if not a["href"].startswith("#")
        ]

        # Extract emails from mailto links
        emails = [
            a["href"].replace("mailto:", "").strip()
            for a in soup.find_all("a", href=True)
            if a["href"].startswith("mailto:")
        ]

        # Extract meta tags
        meta: dict[str, str] = {}
        for tag in soup.find_all("meta"):
            name = tag.get("name") or tag.get("property") or ""
            content = tag.get("content") or ""
            if name and content:
                meta[name] = content

        return CrawledPage(
            url=url,
            status_code=response.status_code,
            title=title,
            text=text[:50_000],  # cap text size
            links=links,
            emails=emails,
            meta=meta,
            raw_html=response.text[:100_000],
        )
