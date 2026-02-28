"""Pydantic models for the Link Building bot."""
from __future__ import annotations

import enum
from datetime import datetime

from pydantic import BaseModel, Field


class OutreachStatus(str, enum.Enum):
    prospect = "prospect"
    contacted = "contacted"
    replied = "replied"
    link_secured = "link_secured"
    rejected = "rejected"


class LinkProspect(BaseModel):
    id: int | None = None
    url: str
    email: str | None = None
    contact_name: str | None = None
    domain_authority_estimate: int | None = None
    relevance_score: float = 0.0
    notes: str = ""
    status: OutreachStatus = OutreachStatus.prospect


class OutreachEmail(BaseModel):
    prospect_url: str
    subject: str
    body: str


class LinkBuildingOutput(BaseModel):
    prospects: list[LinkProspect] = Field(default_factory=list)
    outreach_emails: list[OutreachEmail] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=datetime.utcnow)
