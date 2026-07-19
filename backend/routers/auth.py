import logging
from typing import Annotated, Union

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from starlette import status

from services.exceptions import CredentialsAlreadyUsed
from models.auth import User
from services.auth_service import (
    AuthService,
    get_auth_service,
    authorize_current_user,
)
from schemas.auth import (
    AccessToken,
    TokenPair,
    UserAuthenticate,
    UserCreate,
    UserRead,
    UserReadList,
)
from services.user_service import UserService, get_user_service

auth_router = APIRouter()
logger = logging.getLogger(__name__)


@auth_router.post("/auth/register", status_code=201, response_model=UserRead)
async def register_user(
    user_service: Annotated[UserService, Depends(get_user_service)],
    user: UserCreate,
):
    """Create a new user and return the serialized representation."""
    try:
        new_user = user_service.create_user(user)
    except CredentialsAlreadyUsed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This username or email is not available.",
        )
    return new_user


@auth_router.post("/auth/login", status_code=200, response_model=TokenPair)
async def login_user(
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    user_auth: UserAuthenticate,
    response: Response,
) -> TokenPair:
    token_pair = auth_service.login(user_auth, response)
    if not token_pair:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    response.set_cookie(
        key="refresh_token", value=token_pair.refresh_token, httponly=True
    )
    return token_pair


@auth_router.post("/auth/refresh", status_code=200, response_model=AccessToken)
async def refresh_jwt_tokens(
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    request: Request,
    response: Response,
) -> AccessToken:
    """
    Validate refresh token. If valid, set cookie for new refresh,
    and return new access token.
    """
    # TODO implement handling in frontend:
    # https://secture.com/en/how-to-correctly-store-jwt-tokens-in-the-front-end/
    # - use service layer in frontend
    # - frontend checks access token before every request
    # if expired, call this endpoint
    # backend - add blacklisting the old refresh/access tokens either with postgresql for simplicity or redis/in memory db with persistence for performance/quality of this project
    # if refresh token is expired/not valid - return error to log in again.
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # validate and check if token is not expired
    payload = auth_service.verify_token(refresh_token)
    new_token_pair = auth_service.prepare_jwt_tokens(payload["sub"])

    response.set_cookie(
        key="refresh_token", value=new_token_pair.refresh_token, httponly=True
    )
    return AccessToken.from_token_pair(new_token_pair)


@auth_router.get("/auth/users", status_code=200, response_model=UserReadList)
async def debug_list_users(
    user_service: Annotated[UserService, Depends(get_user_service)],
):
    return user_service.list_users()


@auth_router.get("/auth/test-auth")
async def debug_test_auth(
    current_user: Annotated[User, Depends(authorize_current_user)],
):
    return {"status": "auth is working", "user": current_user.username}
