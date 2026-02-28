"""Competitor Analysis bot implementation."""
from __future__ import annotations

import json
import logging
from datetime import datetime, timezone

from bots.base import BotBase
from bots.competitor_analysis.models import (
    CompetitorAnalysisOutput,
    CompetitorComparison,
    CompetitorProfile,
)
from bots.competitor_analysis.prompts import (
    COMPARE_COMPETITORS_PROMPT,
    EXTRACT_COMPETITOR_DATA_PROMPT,
    GENERATE_REPORT_PROMPT,
)
from common.config import get_settings
from common.crawling.scraper import WebScraper
from common.llm.client import LLMClient

logger = logging.getLogger(__name__)


class CompetitorAnalysisBot(BotBase):
    name = "competitor_analysis"
    description = "Crawls competitor sites and generates a comparative analysis report"

    def __init__(self, llm: LLMClient | None = None, scraper: WebScraper | None = None) -> None:
        self._llm = llm or LLMClient()
        self._scraper = scraper or WebScraper()

    # ------------------------------------------------------------------

    def crawl_competitor(self, url: str) -> str:
        """Fetch and return cleaned text from a competitor URL."""
        result = self._scraper.crawl(url)
        return result.get("text", "")

    def extract_competitor_profile(
        self, url: str, html: str, restaurant_name: str
    ) -> CompetitorProfile:
        """Use LLM to extract structured competitor data from scraped text."""
        # Truncate to avoid token limits
        text = html[:8000] if len(html) > 8000 else html
        prompt = EXTRACT_COMPETITOR_DATA_PROMPT.format(
            url=url,
            our_restaurant_name=restaurant_name,
            website_text=text,
        )
        messages = [{"role": "user", "content": prompt}]
        try:
            result = self._llm.structured_completion(messages, CompetitorProfile)
            return result
        except Exception as exc:
            logger.debug("structured_completion failed (%s), falling back", exc)
            raw = self._llm.chat_completion(messages)
            return self._parse_competitor_profile(raw, url)

    def compare_competitor(
        self, our_restaurant_info: dict, competitor: CompetitorProfile
    ) -> CompetitorComparison:
        """Compare our restaurant against a competitor profile."""
        prompt = COMPARE_COMPETITORS_PROMPT.format(
            our_restaurant_json=json.dumps(our_restaurant_info, indent=2),
            competitor_json=competitor.model_dump_json(indent=2),
        )
        messages = [{"role": "user", "content": prompt}]
        try:
            result = self._llm.structured_completion(messages, CompetitorComparison)
            return result
        except Exception as exc:
            logger.debug("structured_completion failed (%s), falling back", exc)
            raw = self._llm.chat_completion(messages)
            return self._parse_comparison(raw, our_restaurant_info.get("name", ""), competitor)

    def generate_report(self, comparisons: list[CompetitorComparison]) -> str:
        """Generate a Markdown report from all comparisons."""
        settings = get_settings()
        prompt = GENERATE_REPORT_PROMPT.format(
            restaurant_name=settings.restaurant_name,
            analysis_date=datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            comparisons_json=json.dumps(
                [c.model_dump() for c in comparisons], indent=2, default=str
            ),
        )
        messages = [{"role": "user", "content": prompt}]
        try:
            return self._llm.chat_completion(messages, temperature=0.4, max_tokens=3000)
        except Exception as exc:
            logger.error("generate_report failed: %s", exc)
            return "# Competitor Analysis Report\n\n*Report generation failed.*"

    def run(self, **kwargs) -> dict:
        settings = get_settings()
        our_restaurant_info = {
            "name": kwargs.get("restaurant_name", settings.restaurant_name),
            "city": kwargs.get("city", settings.restaurant_city),
            "cuisine": kwargs.get("cuisine", settings.restaurant_cuisine),
        }
        competitor_urls: list[str] = kwargs.get("competitor_urls", [])

        comparisons: list[CompetitorComparison] = []
        for url in competitor_urls:
            logger.info("CompetitorAnalysisBot: crawling %s", url)
            text = self.crawl_competitor(url)
            if not text:
                logger.warning("No text extracted from %s", url)
                continue
            profile = self.extract_competitor_profile(url, text, our_restaurant_info["name"])
            comparison = self.compare_competitor(our_restaurant_info, profile)
            comparisons.append(comparison)

        report_markdown = self.generate_report(comparisons) if comparisons else ""

        output = CompetitorAnalysisOutput(
            competitors=comparisons,
            report_markdown=report_markdown,
            generated_at=datetime.now(timezone.utc),
        )
        result = output.model_dump(mode="json")
        self.save_output(result, "latest.json")
        return result

    # ------------------------------------------------------------------
    # Fallback parsers
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_competitor_profile(raw: str, url: str) -> CompetitorProfile:
        try:
            raw = raw.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
            data = json.loads(raw)
            return CompetitorProfile.model_validate(data)
        except Exception as exc:
            logger.error("_parse_competitor_profile failed: %s", exc)
            return CompetitorProfile(name="Unknown", url=url)

    @staticmethod
    def _parse_comparison(
        raw: str, our_name: str, competitor: CompetitorProfile
    ) -> CompetitorComparison:
        try:
            raw = raw.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
            data = json.loads(raw)
            return CompetitorComparison.model_validate(data)
        except Exception as exc:
            logger.error("_parse_comparison failed: %s", exc)
            return CompetitorComparison(
                our_restaurant=our_name,
                competitor=competitor,
                summary="Comparison could not be parsed.",
            )
