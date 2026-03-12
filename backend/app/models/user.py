import enum
import uuid

from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTableUUID
from sqlalchemy import Enum, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class UserRole(enum.StrEnum):
    INFLUENCER = "influencer"
    BRAND = "brand"
    AGENCY = "agency"
    ADMIN = "admin"


class User(SQLAlchemyBaseUserTableUUID, Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="userrole", create_type=True),
        default=UserRole.INFLUENCER,
        nullable=False,
    )
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
