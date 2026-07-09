import logging
from typing import Annotated

from fastapi import APIRouter, Depends

from schemas.auth import UserCreate, UserRead, UserReadList
from services.UserService import UserService, get_user_service

auth_router = APIRouter()
logger = logging.getLogger(__name__)


@auth_router.post("/auth/register", status_code=201, response_model=UserRead)
async def create_user(
    user_service: Annotated[UserService, Depends(get_user_service)],
    user: UserCreate,
):
    # TODO
    # Add a uniqueness check for email/username before insert.
    # consider correct, and safest response when user we want to create already exists
    """Create a new user and return the serialized representation."""
    return user_service.create_user(user)


@auth_router.get("/auth/users", status_code=200, response_model=UserReadList)
async def debug_list_users(
    user_service: Annotated[UserService, Depends(get_user_service)],
):
    return user_service.list_users()