from geoalchemy2 import Geography
from sqlalchemy import BigInteger
from sqlalchemy.orm import Mapped, mapped_column

from src.shared.db.base import Base


class DriverLocationModel(Base):
    __tablename__ = "driver_locations"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    driver_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    location = mapped_column(
        Geography(geometry_type="POINT", srid=4326),
        nullable=False,
    )
