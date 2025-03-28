from fastapi import APIRouter

from app.api.endpoints import auth
from app.api.endpoints import user
from app.api.endpoints import blog


router = APIRouter()


router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(user.router, prefix="/user", tags=["users"])
router.include_router(blog.router, prefix="/blogs", tags=["blogs"])
