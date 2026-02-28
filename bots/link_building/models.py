"""Data models for the Link-Building Outreach Bot."""
from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field
from sqlalchemy import Column, DateTime, Integer, String, Text

from common.db.database import Base


class ProspectStatus(str, Enum):
    PROSPECT = "prospect"
    CONTACTED = "contacted"
    REPLIED = "replied"
    LINK_SECURED = "link_secured"
    DECLINED = "declined"


class OutreachProspect(Base):
    """SQLAlchemy ORM model for tracking outreach prospects."""

    __tablename__ = "outreach_prospects"

    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String(500), nullable=False)
    site_name = Column(String(200), default="")
    contact_email = Column(String(200), default="")
    contact_form_url = Column(String(500), default="")
    status = Column(String(50), default=ProspectStatus.PROSPECT.value)
    outreach_email_subject = Column(String(300), default="")
    outreach_email_body = Column(Text, default="")
    notes = Column(Text, default="")
    discovered_at = Column(DateTime, default=datetime.utcnow)
    contacted_at = Column(DateTime, nullable=True)
    replied_at = Column(DateTime, nullable=True)
    link_secured_at = Column(DateTime, nullable=True)


class LinkBuildingInput(BaseModel):
    keywords: list[str] = Field(default_factory=list)
    location: str = ""
    seed_urls: list[str] = Field(default_factory=list)


class ProspectSummary(BaseModel):
    url: str
    site_name: str = ""
    contact_email: str = ""
    status: ProspectStatus = ProspectStatus.PROSPECT
    outreach_subject: str = ""
