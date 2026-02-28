"""APScheduler-based scheduler for automated bot execution."""
from __future__ import annotations

import logging
from typing import Callable, Any

logger = logging.getLogger(__name__)


class BotScheduler:
    """Wraps APScheduler's BackgroundScheduler to run bots on a schedule."""

    def __init__(self) -> None:
        try:
            from apscheduler.schedulers.background import BackgroundScheduler

            self._scheduler = BackgroundScheduler()
        except ImportError as exc:
            raise RuntimeError("apscheduler is required for BotScheduler") from exc

    def schedule_bot(
        self,
        bot_name: str,
        cron_expression: str,
        bot_callable: Callable,
        **kwargs: Any,
    ) -> None:
        """Schedule a bot callable using a cron expression string.

        cron_expression format: "minute hour day month day_of_week"
        e.g. "0 8 * * 1" = every Monday at 08:00
        """
        parts = cron_expression.strip().split()
        if len(parts) != 5:
            raise ValueError(
                f"Invalid cron expression '{cron_expression}'. "
                "Expected 5 space-separated fields: minute hour day month day_of_week"
            )
        minute, hour, day, month, day_of_week = parts

        self._scheduler.add_job(
            func=bot_callable,
            trigger="cron",
            minute=minute,
            hour=hour,
            day=day,
            month=month,
            day_of_week=day_of_week,
            kwargs=kwargs,
            id=bot_name,
            name=f"Bot: {bot_name}",
            replace_existing=True,
        )
        logger.info("Scheduled bot '%s' with cron '%s'", bot_name, cron_expression)

    def start(self) -> None:
        """Start the background scheduler."""
        self._scheduler.start()
        logger.info("BotScheduler started")

    def stop(self) -> None:
        """Stop the background scheduler."""
        self._scheduler.shutdown(wait=False)
        logger.info("BotScheduler stopped")

    def list_jobs(self) -> list[dict]:
        """Return a list of scheduled jobs."""
        return [
            {"id": job.id, "name": job.name, "next_run": str(job.next_run_time)}
            for job in self._scheduler.get_jobs()
        ]


def default_schedule(scheduler: BotScheduler | None = None) -> BotScheduler:
    """Create a BotScheduler with sensible default schedules for all bots."""
    if scheduler is None:
        scheduler = BotScheduler()

    from bots.local_seo.bot import LocalSeoBot
    from bots.content_creation.bot import ContentCreationBot
    from bots.forum_marketing.bot import ForumMarketingBot
    from bots.link_building.bot import LinkBuildingBot
    from bots.competitor_analysis.bot import CompetitorAnalysisBot
    from bots.trend_tracking.bot import TrendTrackingBot
    from bots.chatbot.bot import ChatbotBot
    from bots.orchestrator.bot import OrchestratorBot

    def _run(bot_class):
        def _inner(**kwargs):
            try:
                bot = bot_class()
                bot.run(**kwargs)
            except Exception as exc:
                logger.error("Scheduled run of %s failed: %s", bot_class.__name__, exc)
        return _inner

    # Weekly on Monday at 06:00
    scheduler.schedule_bot("local_seo", "0 6 * * 1", _run(LocalSeoBot))
    # Weekly on Monday at 07:00
    scheduler.schedule_bot("content_creation", "0 7 * * 1", _run(ContentCreationBot))
    # Weekly on Tuesday at 06:00
    scheduler.schedule_bot("forum_marketing", "0 6 * * 2", _run(ForumMarketingBot))
    # Weekly on Wednesday at 06:00
    scheduler.schedule_bot("link_building", "0 6 * * 3", _run(LinkBuildingBot))
    # Weekly on Thursday at 06:00
    scheduler.schedule_bot("competitor_analysis", "0 6 * * 4", _run(CompetitorAnalysisBot))
    # Daily at 07:00
    scheduler.schedule_bot("trend_tracking", "0 7 * * *", _run(TrendTrackingBot))
    # Daily at 08:00 (orchestrator aggregates all outputs)
    scheduler.schedule_bot("orchestrator", "0 8 * * *", _run(OrchestratorBot))

    return scheduler
