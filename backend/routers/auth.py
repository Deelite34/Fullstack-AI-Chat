import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from starlette import status

from models.auth import User
from schemas.auth import (
    Token,
    TokenInput,
    TokenPair,
    UserAuthenticate,
    UserCreate,
    UserRead,
    UserReadList,
)
from services.auth_service import (
    AuthService,
    authorize_current_user,
    get_auth_service,
)
from services.exceptions import (
    CredentialsAlreadyUsed,
    TokenAlreadyBlacklisted,
    TokenExpired,
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
) -> Token:
    # TODO: note: could use CSRF protection (both backend+frontend) for login endpoint,
    # and also for refresh token endpoint, to prevent CSRF attacks
    # skipped it to avoid scope creep
    token_pair = auth_service.login(user_auth)
    if not token_pair:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    response.set_cookie(
        key="refresh_token",
        value=token_pair.refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",  # TODO: note: strict could theoretically be used here if this would ever be moved to production
    )
    return Token.access_token_from_pair(token_pair)


@auth_router.post("/auth/logout", status_code=200, response_model=TokenPair)
async def logout_user(
    auth: Annotated[User, Depends(authorize_current_user)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    access_token: TokenInput,
    response: Response,
    request: Request,
):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        logger.info("Missing refresh token in logout request")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Failed to log out",
            headers={"WWW-Authenticate": "Bearer"},
        )

    auth_service.logout(access_token, refresh_token)
    response.delete_cookie(key="refresh_token", secure=True, samesite="lax")


@auth_router.post("/auth/tokens/refresh", status_code=200, response_model=Token)
async def refresh_access_token(
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    access_token: TokenInput,
    request: Request,
    response: Response,
) -> Token:
    """
    Refresh access token, and also refresh token -
    validate refresh token, and if valid, generate new access+refresh tokens, and blacklist old ones.
    If refresh token is expired, return 401.
    """
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        refresh_payload = auth_service.verify_token(refresh_token)
    except TokenExpired:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except TokenAlreadyBlacklisted:
        logger.warning(
            "Possible security issue: There was attempt to refresh blacklisted refresh token, possible token reuse attempt %s",
            refresh_token,
        )
        # TODO: note: here this could theoretically use some more advanced handling of possible security issue - more detailed logs, saving IP address, etc..
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_payload = None
    try:
        access_payload = auth_service.verify_token(access_token.token)
    except TokenExpired:
        # Access token is expired, but we can still refresh it
        logger.debug(
            "Access token expired, refreshing for user %s", refresh_payload["sub"]
        )
    except TokenAlreadyBlacklisted:
        logger.warning(
            "Possible security issue: There was attempt to refresh blacklisted access token, possible token reuse attempt %s",
            access_token,
        )
        # TODO: here this could theoretically use some more advanced handling of possible security issue - more detailed logs, saving IP address, etc..
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    new_token_pair = auth_service.refresh_access_token(
        access_payload, refresh_payload, access_token, refresh_token
    )

    response.set_cookie(
        key="refresh_token",
        value=new_token_pair.refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
    )
    return Token.access_token_from_pair(new_token_pair)


@auth_router.get("/auth/users", status_code=200, response_model=UserReadList)
async def debug_list_users(
    user_service: Annotated[UserService, Depends(get_user_service)],
):
    return user_service.list_users()


@auth_router.get("/auth/test-auth")
async def debug_test_auth(
    auth: Annotated[User, Depends(authorize_current_user)],
):
    return {"status": "auth is working", "user": auth.username}
