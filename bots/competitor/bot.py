"""Competitor Website Analysis Bot (Bot 5)."""
from __future__ import annotations

import json
import logging

from bots.base import BaseBot
from bots.competitor.models import (
    ComparisonAxis,
    CompetitorInput,
    CompetitorProfile,
    CompetitorReport,
    MenuItem,
)
from common.crawling.crawler import WebCrawler
from common.llm.client import LLMClient
from common.models.base import BotName
from infra.config import settings

logger = logging.getLogger(__name__)

EXTRACT_SYSTEM_PROMPT = """
You are an expert at analyzing restaurant websites.
Given the text content of a restaurant website, extract structured information.
Respond ONLY with valid JSON:
{
  "name": "Restaurant Name",
  "cuisines": ["italian", "pizza"],
  "price_range": "$$",
  "menu_items": [
    {"name": "Margherita Pizza", "price": "$14", "description": "...", "category": "Pizza"}
  ],
  "delivery_platforms": ["DoorDash", "Uber Eats"],
  "promotions": ["Happy Hour 3-6pm"],
  "usps": ["wood-fired oven", "family recipes since 1980"]
}
"""

COMPARE_SYSTEM_PROMPT = """
You are a restaurant business analyst comparing two restaurants.
Given profiles of our restaurant and a competitor, provide a structured comparison.
Respond ONLY with valid JSON:
{
  "comparisons": [
    {
      "axis": "price_range",
      "our_value": "$$",
      "competitor_value": "$$$",
      "advantage": "ours",
      "notes": "We are more affordable"
    }
  ],
  "opportunities": ["We could offer wood-fired options"],
  "threats": ["Competitor has more delivery platforms"]
}
"""


class CompetitorBot(BaseBot):
    """Crawls competitor sites, extracts data, compares against our restaurant."""

    name = BotName.COMPETITOR

    def __init__(
        self,
        competitor_input: CompetitorInput | None = None,
        llm: LLMClient | None = None,
        crawler: WebCrawler | None = None,
    ) -> None:
        super().__init__()
        self.competitor_input = competitor_input or CompetitorInput()
        self.llm = llm or LLMClient()
        self.crawler = crawler or WebCrawler()
        settings.output_dir.mkdir(parents=True, exist_ok=True)

    def run(self) -> dict:
        logger.info(
            "CompetitorBot: analyzing %d competitors",
            len(self.competitor_input.competitor_urls),
        )
        reports: list[CompetitorReport] = []
        for url in self.competitor_input.competitor_urls:
            report = self._analyze_competitor(url)
            if report:
                reports.append(report)

        output = {"reports": [r.model_dump() for r in reports], "total_analyzed": len(reports)}
        self._save_output(output)
        return output

    def _analyze_competitor(self, url: str) -> CompetitorReport | None:
        page = self.crawler.fetch(url)
        if page.status_code == 0:
            logger.warning("Could not fetch competitor: %s", url)
            return None

        profile = self._extract_profile(url, page.title, page.text)
        comparison = self._compare_with_ours(profile)
        comparisons = [ComparisonAxis(**c) for c in comparison.get("comparisons", [])]
        return CompetitorReport(
            competitor=profile,
            comparisons=comparisons,
            opportunities=comparison.get("opportunities", []),
            threats=comparison.get("threats", []),
        )

    def _extract_profile(self, url: str, title: str, text: str) -> CompetitorProfile:
        user_prompt = f"URL: {url}\nTitle: {title}\nContent (first 3000 chars):\n{text[:3000]}"
        raw = self.llm.chat(EXTRACT_SYSTEM_PROMPT, user_prompt, temperature=0.3)
        data = json.loads(raw)
        menu_items = [MenuItem(**item) for item in data.pop("menu_items", [])]
        return CompetitorProfile(url=url, menu_items=menu_items, **data)

    def _compare_with_ours(self, competitor: CompetitorProfile) -> dict:
        our_profile = self.competitor_input.our_profile or {
            "name": settings.restaurant_name,
            "cuisine": settings.restaurant_cuisine,
            "city": settings.restaurant_city,
        }
        user_prompt = (
            f"Our restaurant: {json.dumps(our_profile)}\n"
            f"Competitor: {competitor.model_dump_json()}"
        )
        raw = self.llm.chat(COMPARE_SYSTEM_PROMPT, user_prompt, temperature=0.4)
        return json.loads(raw)

    def _save_output(self, output: dict) -> None:
        path = settings.output_dir / "competitor_output.json"
        path.write_text(json.dumps(output, indent=2, default=str))
        logger.info("CompetitorBot: saved output to %s", path)
