"""Orchestrator bot implementation."""
from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from bots.base import BotBase
from bots.orchestrator.models import (
    ActionableTask,
    BotSummary,
    ExecutiveSummary,
    TaskPriority,
)
from bots.orchestrator.prompts import (
    EXECUTIVE_SUMMARY_PROMPT,
    PRIORITIZE_TASKS_PROMPT,
    SUMMARIZE_BOT_OUTPUT_PROMPT,
)
from common.config import get_settings
from common.llm.client import LLMClient

logger = logging.getLogger(__name__)

_KNOWN_BOTS = [
    "local_seo",
    "content_creation",
    "forum_marketing",
    "link_building",
    "competitor_analysis",
    "trend_tracking",
    "chatbot",
]


class OrchestratorBot(BotBase):
    name = "orchestrator"
    description = "Aggregates all bot outputs into an executive summary with prioritised tasks"

    def __init__(self, llm: LLMClient | None = None) -> None:
        self._llm = llm or LLMClient()

    # ------------------------------------------------------------------

    def load_bot_outputs(self) -> dict[str, dict]:
        """Load the latest JSON output from each known bot."""
        settings = get_settings()
        output_root = Path(settings.output_dir)
        results: dict[str, dict] = {}

        for bot_name in _KNOWN_BOTS:
            latest = output_root / bot_name / "latest.json"
            if latest.exists():
                try:
                    results[bot_name] = json.loads(latest.read_text(encoding="utf-8"))
                    logger.info("Loaded output for bot: %s", bot_name)
                except Exception as exc:
                    logger.warning("Failed to load %s: %s", latest, exc)
            else:
                logger.debug("No output found for bot: %s", bot_name)

        return results

    def summarize_bot_output(self, bot_name: str, output_data: dict) -> BotSummary:
        """Use LLM to extract key findings and tasks from a bot's output."""
        # Truncate large payloads
        output_json = json.dumps(output_data, indent=2, default=str)
        if len(output_json) > 6000:
            output_json = output_json[:6000] + "\n... (truncated)"

        prompt = SUMMARIZE_BOT_OUTPUT_PROMPT.format(
            bot_name=bot_name,
            output_json=output_json,
        )
        messages = [{"role": "user", "content": prompt}]
        try:
            result = self._llm.structured_completion(messages, BotSummary)
            result.bot_name = bot_name
            # Set last_run from output if present
            if "generated_at" in output_data:
                try:
                    result.last_run = datetime.fromisoformat(str(output_data["generated_at"]))
                except Exception:
                    pass
            return result
        except Exception as exc:
            logger.debug("structured_completion failed (%s), falling back", exc)
            raw = self._llm.chat_completion(messages)
            return self._parse_bot_summary(raw, bot_name)

    def prioritize_tasks(self, all_tasks: list[ActionableTask]) -> list[ActionableTask]:
        """Re-prioritize and deduplicate tasks across all bots."""
        if not all_tasks:
            return []
        tasks_json = json.dumps([t.model_dump() for t in all_tasks], indent=2)
        prompt = PRIORITIZE_TASKS_PROMPT.format(tasks_json=tasks_json)
        messages = [{"role": "user", "content": prompt}]
        try:
            raw = self._llm.chat_completion(messages, temperature=0.3)
            raw = raw.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
            data = json.loads(raw)
            items = data.get("top_tasks", data) if isinstance(data, dict) else data
            return [ActionableTask.model_validate(item) for item in items]
        except Exception as exc:
            logger.error("prioritize_tasks failed: %s", exc)
            # Fall back: sort by priority
            priority_order = {TaskPriority.high: 0, TaskPriority.medium: 1, TaskPriority.low: 2}
            return sorted(all_tasks, key=lambda t: priority_order.get(t.priority, 1))[:10]

    def generate_executive_summary(self, bot_summaries: list[BotSummary]) -> ExecutiveSummary:
        """Generate the full executive summary from all bot summaries."""
        settings = get_settings()
        all_tasks = [task for summary in bot_summaries for task in summary.tasks]
        top_tasks = self.prioritize_tasks(all_tasks)

        period = datetime.now(timezone.utc).strftime("%B %Y")
        summaries_json = json.dumps(
            [s.model_dump(mode="json") for s in bot_summaries], indent=2, default=str
        )
        # Truncate if needed
        if len(summaries_json) > 8000:
            summaries_json = summaries_json[:8000] + "\n... (truncated)"

        active_bots = len([s for s in bot_summaries if s.last_run])
        health_score = round(min(10.0, (active_bots / max(len(_KNOWN_BOTS), 1)) * 10), 1)

        prompt = EXECUTIVE_SUMMARY_PROMPT.format(
            restaurant_name=settings.restaurant_name,
            period=period,
            summaries_json=summaries_json,
            health_score=health_score,
        )
        messages = [{"role": "user", "content": prompt}]
        try:
            report_markdown = self._llm.chat_completion(messages, temperature=0.4, max_tokens=2000)
        except Exception as exc:
            logger.error("generate_executive_summary LLM call failed: %s", exc)
            report_markdown = f"# Marketing Summary - {period}\n\n*Report generation failed.*"

        return ExecutiveSummary(
            period=period,
            overall_health_score=health_score,
            bot_summaries=bot_summaries,
            top_tasks=top_tasks,
            report_markdown=report_markdown,
            generated_at=datetime.now(timezone.utc),
        )

    def run(self, **kwargs) -> dict:
        logger.info("OrchestratorBot: loading bot outputs")
        bot_outputs = self.load_bot_outputs()

        if not bot_outputs:
            logger.warning("OrchestratorBot: no bot outputs found; generating empty summary")

        bot_summaries: list[BotSummary] = []
        for bot_name, output_data in bot_outputs.items():
            logger.info("OrchestratorBot: summarising %s", bot_name)
            summary = self.summarize_bot_output(bot_name, output_data)
            bot_summaries.append(summary)

        logger.info("OrchestratorBot: generating executive summary")
        executive_summary = self.generate_executive_summary(bot_summaries)

        result = executive_summary.model_dump(mode="json")
        self.save_output(result, "latest.json")
        return result

    # ------------------------------------------------------------------
    # Fallback parsers
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_bot_summary(raw: str, bot_name: str) -> BotSummary:
        try:
            raw = raw.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
            data = json.loads(raw)
            summary = BotSummary.model_validate(data)
            summary.bot_name = bot_name
            return summary
        except Exception as exc:
            logger.error("_parse_bot_summary failed: %s", exc)
            return BotSummary(bot_name=bot_name, key_findings=[], tasks=[])
