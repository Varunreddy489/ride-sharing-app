from sqlalchemy import BigInteger, Enum, String
from sqlalchemy.orm import Mapped, mapped_column

from src.shared.db.base import Base
from src.shared.utils.enums import UserRoles


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    phone_number: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    role: Mapped[UserRoles] = mapped_column(
        Enum(UserRoles), name="role", nullable=False, default=UserRoles.RIDER
    )
    password: Mapped[str] = mapped_column(String(255), nullable=False)
