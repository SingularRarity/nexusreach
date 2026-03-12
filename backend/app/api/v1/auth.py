from fastapi import APIRouter

from app.core.auth import auth_backend, fastapi_users
from app.schemas.user import UserCreate, UserRead

router = APIRouter(prefix="/auth", tags=["auth"])

# POST /login, POST /logout
router.include_router(fastapi_users.get_auth_router(auth_backend))

# POST /register
router.include_router(fastapi_users.get_register_router(UserRead, UserCreate))
