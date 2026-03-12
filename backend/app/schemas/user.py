import uuid

from fastapi_users import schemas
from pydantic import ConfigDict

from app.models.user import UserRole


class UserRead(schemas.BaseUser[uuid.UUID]):
    role: UserRole
    full_name: str | None = None
    model_config = ConfigDict(from_attributes=True)


class UserCreate(schemas.BaseUserCreate):
    role: UserRole = UserRole.INFLUENCER
    full_name: str | None = None


class UserUpdate(schemas.BaseUserUpdate):
    role: UserRole | None = None
    full_name: str | None = None
