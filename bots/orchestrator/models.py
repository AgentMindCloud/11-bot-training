"""Data models for the Manager/Analytics Orchestrator Bot."""
from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from pathlib import Path

from pydantic import BaseModel, Field


class TaskPriority(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ActionableTask(BaseModel):
    title: str
    description: str
    source_bot: str
    priority: TaskPriority = TaskPriority.MEDIUM
    due_date: datetime | None = None
    tags: list[str] = Field(default_factory=list)


class BotSummary(BaseModel):
    bot_name: str
    last_run: datetime | None = None
    key_insights: list[str] = Field(default_factory=list)
    output_files: list[str] = Field(default_factory=list)


class WeeklyReport(BaseModel):
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    executive_summary: str = ""
    bot_summaries: list[BotSummary] = Field(default_factory=list)
    actionable_tasks: list[ActionableTask] = Field(default_factory=list)
    report_markdown: str = ""


class OrchestratorInput(BaseModel):
    output_dir: Path = Path("./outputs")
    generate_pdf: bool = False
