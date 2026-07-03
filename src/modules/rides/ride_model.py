from datetime import datetime

from geoalchemy2 import Geography
from sqlalchemy import DECIMAL, BigInteger, DateTime, Enum, Float, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from src.shared.db.base import Base
from src.shared.utils.enums import RideStatus


class RideModel(Base):
    __tablename__ = "ride_requests"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    lock_version: Mapped[int] = mapped_column(BigInteger, nullable=False)
    rider_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    driver_id: Mapped[int] = mapped_column(BigInteger, nullable=True)
    vehicle_id: Mapped[int] = mapped_column(BigInteger, nullable=True)
    # Store pickup location as a single Geography POINT (longitude, latitude)
    # This allows storing coordinates like 78.4747° E, 17.3616° N
    pickup_point = mapped_column(
        Geography(geometry_type="POINT", srid=4326),
        nullable=False,
    )

    # Store dropoff location as a single Geography POINT (longitude, latitude)
    drop_off_point = mapped_column(
        Geography(geometry_type="POINT", srid=4326),
        nullable=False,
    )
    status: Mapped[RideStatus] = mapped_column(
        Enum(RideStatus), name="status", nullable=False, default=RideStatus.PENDING
    )

    fare: Mapped[DECIMAL | None] = mapped_column(
        Numeric(10, 2),
        nullable=True,
    )

    distance_km: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    duration_minutes: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    cancellation_reason: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )

    requested_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    accepted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    canceled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
