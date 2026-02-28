"""Trend Tracking bot implementation."""
from __future__ import annotations

import json
import logging
from datetime import datetime, timezone

from bots.base import BotBase
from bots.trend_tracking.models import TrendItem, WeeklyTrendReport
from bots.trend_tracking.prompts import ACTIONABLE_IDEAS_PROMPT, TREND_ANALYSIS_PROMPT
from common.config import get_settings
from common.llm.client import LLMClient

logger = logging.getLogger(__name__)

_RSS_FEEDS = [
    "https://www.restaurantbusinessonline.com/feed",
    "https://www.foodandwine.com/syndication/rss/all.rss",
    "https://feeds.feedburner.com/eater/nyc",
]


class TrendTrackingBot(BotBase):
    name = "trend_tracking"
    description = "Tracks restaurant industry trends and generates weekly opportunity reports"

    def __init__(self, llm: LLMClient | None = None) -> None:
        self._llm = llm or LLMClient()

    # ------------------------------------------------------------------

    def fetch_news_headlines(self, topics: list[str] | None = None) -> list[str]:
        """Fetch headlines from RSS feeds and/or news search."""
        headlines: list[str] = []
        try:
            import httpx

            for feed_url in _RSS_FEEDS:
                try:
                    with httpx.Client(timeout=10, follow_redirects=True) as client:
                        resp = client.get(feed_url)
                        resp.raise_for_status()
                        headlines.extend(self._parse_rss_titles(resp.text))
                except Exception as exc:
                    logger.debug("Failed to fetch %s: %s", feed_url, exc)
        except ImportError:
            logger.warning("httpx not available; skipping news fetch")

        if not headlines and topics:
            # Fallback: use topic names as placeholder headlines
            headlines = [f"Latest trends in {t}" for t in topics]

        return headlines[:50]  # cap at 50 headlines

    @staticmethod
    def _parse_rss_titles(rss_xml: str) -> list[str]:
        """Extract <title> text from basic RSS XML."""
        try:
            from bs4 import BeautifulSoup

            soup = BeautifulSoup(rss_xml, "xml")
            items = soup.find_all("item")
            return [item.find("title").get_text(strip=True) for item in items if item.find("title")]
        except Exception:
            return []

    def analyze_trends(self, headlines: list[str], restaurant_info: dict) -> list[TrendItem]:
        """Use LLM to identify relevant trends from headlines."""
        settings = get_settings()
        headlines_text = "\n".join(f"- {h}" for h in headlines) if headlines else "No headlines available."
        prompt = TREND_ANALYSIS_PROMPT.format(
            restaurant_name=restaurant_info.get("restaurant_name", settings.restaurant_name),
            city=restaurant_info.get("city", settings.restaurant_city),
            cuisine=restaurant_info.get("cuisine", settings.restaurant_cuisine),
            headlines_text=headlines_text,
        )
        messages = [{"role": "user", "content": prompt}]
        try:
            from pydantic import BaseModel as PydanticBase

            class _TrendsResponse(PydanticBase):
                trends: list[TrendItem]

            result = self._llm.structured_completion(messages, _TrendsResponse)
            trends = result.trends
        except Exception as exc:
            logger.debug("structured_completion failed (%s), falling back", exc)
            raw = self._llm.chat_completion(messages)
            trends = self._parse_trends(raw)

        # Enrich with actionable ideas
        for trend in trends:
            if not trend.actionable_ideas:
                trend.actionable_ideas = self._generate_actionable_ideas(trend, restaurant_info)

        return trends

    def _generate_actionable_ideas(self, trend: TrendItem, restaurant_info: dict) -> list[str]:
        """Generate actionable ideas for a specific trend."""
        settings = get_settings()
        prompt = ACTIONABLE_IDEAS_PROMPT.format(
            restaurant_name=restaurant_info.get("restaurant_name", settings.restaurant_name),
            city=restaurant_info.get("city", settings.restaurant_city),
            cuisine=restaurant_info.get("cuisine", settings.restaurant_cuisine),
            trend_topic=trend.topic,
            trend_summary=trend.summary,
        )
        messages = [{"role": "user", "content": prompt}]
        try:
            raw = self._llm.chat_completion(messages, temperature=0.5)
            raw = raw.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
            data = json.loads(raw)
            return data.get("actionable_ideas", [])
        except Exception as exc:
            logger.error("_generate_actionable_ideas failed: %s", exc)
            return []

    def generate_weekly_report(self, trends: list[TrendItem]) -> WeeklyTrendReport:
        """Build a WeeklyTrendReport from analysed trends."""
        top_opportunities: list[str] = []
        for trend in sorted(trends, key=lambda t: t.relevance_score, reverse=True)[:3]:
            top_opportunities.extend(trend.actionable_ideas[:2])

        week_of = datetime.now(timezone.utc).strftime("Week of %Y-%m-%d")
        return WeeklyTrendReport(
            week_of=week_of,
            trends=trends,
            top_opportunities=top_opportunities,
            generated_at=datetime.now(timezone.utc),
        )

    def run(self, **kwargs) -> dict:
        settings = get_settings()
        restaurant_info = {
            "restaurant_name": kwargs.get("restaurant_name", settings.restaurant_name),
            "city": kwargs.get("city", settings.restaurant_city),
            "cuisine": kwargs.get("cuisine", settings.restaurant_cuisine),
        }
        topics = kwargs.get(
            "topics",
            [restaurant_info["cuisine"], "restaurant industry", "food trends", restaurant_info["city"]],
        )

        logger.info("TrendTrackingBot: fetching headlines")
        headlines = self.fetch_news_headlines(topics)

        logger.info("TrendTrackingBot: analysing %d headlines", len(headlines))
        trends = self.analyze_trends(headlines, restaurant_info)

        report = self.generate_weekly_report(trends)
        result = report.model_dump(mode="json")
        self.save_output(result, "latest.json")
        return result

    # ------------------------------------------------------------------
    # Fallback parsers
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_trends(raw: str) -> list[TrendItem]:
        try:
            raw = raw.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
            data = json.loads(raw)
            items = data.get("trends", data) if isinstance(data, dict) else data
            return [TrendItem.model_validate(item) for item in items]
        except Exception as exc:
            logger.error("_parse_trends failed: %s", exc)
            return []
