"""Tests for common utilities."""
from __future__ import annotations

import pytest

from common.crawling.scraper import WebScraper
from common.storage.database import (
    ProspectRepository,
    ProspectStatus,
    get_engine,
    init_db,
)


class TestWebScraper:
    def test_extract_text_strips_html_tags(self):
        scraper = WebScraper()
        html = "<html><body><h1>Hello World</h1><p>Test content here.</p></body></html>"
        text = scraper.extract_text(html)
        assert "<" not in text
        assert "Hello World" in text
        assert "Test content here" in text

    def test_extract_text_removes_scripts(self):
        scraper = WebScraper()
        html = "<html><body><script>alert('xss')</script><p>Real content</p></body></html>"
        text = scraper.extract_text(html)
        assert "alert" not in text
        assert "Real content" in text

    def test_extract_text_empty_input(self):
        scraper = WebScraper()
        assert scraper.extract_text("") == ""

    def test_extract_links_returns_valid_urls(self):
        scraper = WebScraper()
        html = """
        <html><body>
          <a href="https://example.com/page1">Page 1</a>
          <a href="https://other.com/about">About</a>
          <a href="/relative">Relative</a>
          <a href="mailto:test@test.com">Email</a>
        </body></html>
        """
        links = scraper.extract_links(html, base_url="https://example.com")
        assert "https://example.com/page1" in links
        assert "https://other.com/about" in links
        assert "https://example.com/relative" in links
        # mailto should be excluded
        assert not any("mailto" in link for link in links)

    def test_extract_links_deduplicates(self):
        scraper = WebScraper()
        html = """
        <html><body>
          <a href="https://example.com">Link 1</a>
          <a href="https://example.com">Link 2</a>
        </body></html>
        """
        links = scraper.extract_links(html)
        assert links.count("https://example.com") == 1

    def test_extract_links_empty_html(self):
        scraper = WebScraper()
        assert scraper.extract_links("") == []


class TestProspectRepository:
    @pytest.fixture
    def db_engine(self):
        engine = get_engine("sqlite:///:memory:")
        init_db(engine)
        return engine

    def test_add_and_get_all(self, db_engine):
        repo = ProspectRepository(db_engine)
        repo.add(url="https://blog.example.com", email="editor@example.com", name="Editor")
        all_prospects = repo.get_all()
        assert len(all_prospects) == 1
        assert all_prospects[0].url == "https://blog.example.com"
        assert all_prospects[0].email == "editor@example.com"

    def test_get_by_status(self, db_engine):
        repo = ProspectRepository(db_engine)
        repo.add(url="https://a.example.com")
        repo.add(url="https://b.example.com")
        prospects = repo.get_by_status(ProspectStatus.prospect)
        assert len(prospects) == 2

    def test_update_status(self, db_engine):
        repo = ProspectRepository(db_engine)
        prospect = repo.add(url="https://site.example.com")
        assert prospect.status == ProspectStatus.prospect

        updated = repo.update_status(prospect.id, ProspectStatus.contacted)
        assert updated is not None
        assert updated.status == ProspectStatus.contacted

    def test_update_status_nonexistent_returns_none(self, db_engine):
        repo = ProspectRepository(db_engine)
        result = repo.update_status(9999, ProspectStatus.contacted)
        assert result is None

    def test_multiple_prospects_with_different_statuses(self, db_engine):
        repo = ProspectRepository(db_engine)
        p1 = repo.add(url="https://one.example.com")
        p2 = repo.add(url="https://two.example.com")
        repo.update_status(p1.id, ProspectStatus.contacted)

        prospects_contacted = repo.get_by_status(ProspectStatus.contacted)
        prospects_raw = repo.get_by_status(ProspectStatus.prospect)

        assert len(prospects_contacted) == 1
        assert len(prospects_raw) == 1
        assert prospects_contacted[0].url == "https://one.example.com"
