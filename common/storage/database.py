"""SQLAlchemy 2.0-style database layer."""
from __future__ import annotations

import enum
from datetime import datetime, timezone

from sqlalchemy import (
    DateTime,
    Engine,
    Enum,
    Integer,
    String,
    Text,
    create_engine,
    select,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class ProspectStatus(str, enum.Enum):
    prospect = "prospect"
    contacted = "contacted"
    replied = "replied"
    link_secured = "link_secured"
    rejected = "rejected"


# ---------------------------------------------------------------------------
# ORM models
# ---------------------------------------------------------------------------


class Base(DeclarativeBase):
    pass


class OutreachProspect(Base):
    __tablename__ = "outreach_prospects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    url: Mapped[str] = mapped_column(String(2048), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[ProspectStatus] = mapped_column(
        Enum(ProspectStatus), default=ProspectStatus.prospect, nullable=False
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


# ---------------------------------------------------------------------------
# Repository
# ---------------------------------------------------------------------------


class ProspectRepository:
    def __init__(self, engine: Engine) -> None:
        self._engine = engine

    def add(self, url: str, email: str | None = None, name: str | None = None, notes: str | None = None) -> OutreachProspect:
        with Session(self._engine) as session:
            prospect = OutreachProspect(url=url, email=email, name=name, notes=notes)
            session.add(prospect)
            session.commit()
            session.refresh(prospect)
            return prospect

    def get_all(self) -> list[OutreachProspect]:
        with Session(self._engine) as session:
            return list(session.scalars(select(OutreachProspect)).all())

    def get_by_status(self, status: ProspectStatus) -> list[OutreachProspect]:
        with Session(self._engine) as session:
            return list(
                session.scalars(
                    select(OutreachProspect).where(OutreachProspect.status == status)
                ).all()
            )

    def update_status(self, prospect_id: int, status: ProspectStatus) -> OutreachProspect | None:
        with Session(self._engine) as session:
            prospect = session.get(OutreachProspect, prospect_id)
            if prospect is None:
                return None
            prospect.status = status
            prospect.updated_at = datetime.now(timezone.utc)
            session.commit()
            session.refresh(prospect)
            return prospect


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def get_engine(database_url: str) -> Engine:
    return create_engine(database_url)


def init_db(engine: Engine) -> None:
    Base.metadata.create_all(engine)
