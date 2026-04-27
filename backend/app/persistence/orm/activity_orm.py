"""Mapeo ORM de SQLAlchemy para la tabla `activities`.

Los indicadores derivados del EVM (PV, EV, CPI, SPI, EAC, VAC) NO se
persisten intencionalmente. Los cinco campos de entrada a continuación son
la fuente única de verdad y los indicadores se calculan en cada lectura.
"""

from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Numeric, String, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ActivityORM(Base):
    __tablename__ = "activities"
    __table_args__ = (
        CheckConstraint("bac >= 0", name="chk_bac_non_negative"),
        CheckConstraint("actual_cost >= 0", name="chk_actual_cost_non_negative"),
        CheckConstraint(
            "planned_percent BETWEEN 0 AND 100",
            name="chk_planned_percent_range",
        ),
        CheckConstraint(
            "actual_percent BETWEEN 0 AND 100",
            name="chk_actual_percent_range",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    project_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    bac: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    planned_percent: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    actual_percent: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    actual_cost: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    project: Mapped["ProjectORM"] = relationship(  # noqa: F821
        "ProjectORM",
        back_populates="activities",
    )
