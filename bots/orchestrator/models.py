"""Pydantic models for the Orchestrator bot."""
from __future__ import annotations

import enum
from datetime import datetime

from pydantic import BaseModel, Field


class TaskPriority(str, enum.Enum):
    high = "high"
    medium = "medium"
    low = "low"


class ActionableTask(BaseModel):
    title: str
    description: str
    priority: TaskPriority = TaskPriority.medium
    source_bot: str = ""
    estimated_effort: str = ""


class BotSummary(BaseModel):
    bot_name: str
    last_run: datetime | None = None
    key_findings: list[str] = Field(default_factory=list)
    tasks: list[ActionableTask] = Field(default_factory=list)


class ExecutiveSummary(BaseModel):
    period: str
    overall_health_score: float = 0.0
    bot_summaries: list[BotSummary] = Field(default_factory=list)
    top_tasks: list[ActionableTask] = Field(default_factory=list)
    report_markdown: str = ""
    generated_at: datetime = Field(default_factory=datetime.utcnow)
