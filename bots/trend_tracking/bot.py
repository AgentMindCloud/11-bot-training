"""Industry/Trend Tracking Bot (Bot 6)."""
from __future__ import annotations

import json
import logging
from datetime import datetime, timezone

from bots.base import BaseBot
from bots.trend_tracking.models import TrendInput, TrendItem, TrendReport, TrendSource
from common.crawling.crawler import WebCrawler
from common.llm.client import LLMClient
from common.models.base import BotName
from infra.config import settings

logger = logging.getLogger(__name__)

DEFAULT_TREND_URLS = [
    "https://www.eater.com",
    "https://restaurantbusinessonline.com",
    "https://www.foodbusinessnews.net",
]

TREND_SYSTEM_PROMPT = """
You are a restaurant industry analyst. Given text from industry news sources, identify 3-5 emerging trends relevant to a local restaurant.
For each trend, provide actionable ideas the restaurant can implement.
Respond ONLY with valid JSON:
[
  {
    "topic": "Plant-based menu expansion",
    "summary": "...",
    "actionable_ideas": ["Add 2 vegan options", "Market to health-conscious crowd"],
    "relevance_score": 4
  }
]
"""

SUMMARY_SYSTEM_PROMPT = """
You are writing a weekly executive summary for a restaurant owner.
Given a list of trends, write a concise executive summary (3-4 sentences) and list top 5 opportunities.
Respond ONLY with valid JSON:
{
  "executive_summary": "...",
  "top_opportunities": ["Opportunity 1", "Opportunity 2"]
}
"""


class TrendTrackingBot(BaseBot):
    """Monitors news sources, summarizes weekly trends and opportunities."""

    name = BotName.TREND_TRACKING

    def __init__(
        self,
        trend_input: TrendInput | None = None,
        llm: LLMClient | None = None,
        crawler: WebCrawler | None = None,
    ) -> None:
        super().__init__()
        self.trend_input = trend_input or TrendInput(
            seed_urls=DEFAULT_TREND_URLS,
            topics=["restaurant trends", "food delivery", "local dining"],
            location=settings.restaurant_city,
        )
        self.llm = llm or LLMClient()
        self.crawler = crawler or WebCrawler()
        settings.output_dir.mkdir(parents=True, exist_ok=True)

    def run(self) -> dict:
        logger.info("TrendTrackingBot: crawling %d sources", len(self.trend_input.seed_urls))
        sources: list[TrendSource] = []
        combined_text = ""

        for url in self.trend_input.seed_urls:
            page = self.crawler.fetch(url)
            if page.status_code > 0:
                sources.append(TrendSource(url=url, title=page.title, snippet=page.text[:500]))
                combined_text += f"\n\n[Source: {url}]\n{page.text[:2000]}"

        trends = self._extract_trends(combined_text)
        summary_data = self._generate_summary(trends)

        report = TrendReport(
            week_of=datetime.now(timezone.utc),
            trends=trends,
            top_opportunities=summary_data.get("top_opportunities", []),
            executive_summary=summary_data.get("executive_summary", ""),
        )
        self._save_output(report)
        return report.model_dump(mode="json")

    def _extract_trends(self, text: str) -> list[TrendItem]:
        user_prompt = (
            f"Restaurant type: {settings.restaurant_cuisine} in {settings.restaurant_city}\n"
            f"News content:\n{text[:6000]}"
        )
        raw = self.llm.chat(TREND_SYSTEM_PROMPT, user_prompt, temperature=0.6)
        items_data = json.loads(raw)
        return [TrendItem(**item) for item in items_data]

    def _generate_summary(self, trends: list[TrendItem]) -> dict:
        trends_text = json.dumps([t.model_dump() for t in trends], indent=2)
        raw = self.llm.chat(SUMMARY_SYSTEM_PROMPT, trends_text, temperature=0.5)
        return json.loads(raw)

    def _save_output(self, report: TrendReport) -> None:
        path = settings.output_dir / "trend_report.json"
        path.write_text(report.model_dump_json(indent=2))
        logger.info("TrendTrackingBot: saved trend report to %s", path)
