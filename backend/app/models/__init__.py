# Import all models here so Alembic can discover them via Base.metadata
from app.models.base import BaseModel
from app.models.user import User, UserRole

__all__ = ["BaseModel", "User", "UserRole"]
