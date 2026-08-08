import logging
from datetime import UTC, datetime
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from starlette import status

from config.settings import Config, config
from db import get_session
from models.auth import User
from repositories.expired_access_tokens import ExpiredTokenRepository
from repositories.users import UserRepository
from schemas.auth import (
    JwtUser,
    TokenInput,
    TokenPair,
    UserAuthenticate,
    UserRead,
    UserReadList,
)
from services.exceptions import TokenAlreadyBlacklisted, TokenExpired

logger = logging.getLogger()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)


class AuthService:
    def __init__(
        self,
        user_repository: UserRepository,
        expired_access_tokens_repository: ExpiredTokenRepository,
    ):
        self.config: Config = config
        self.user_repository: UserRepository = user_repository
        self.expired_access_tokens_repository = expired_access_tokens_repository

    def login(self, user_auth_data: UserAuthenticate) -> TokenPair:
        """Login auth - take credentials, checks if they are valid, and returns JWT token pair."""
        existing_user = self.user_repository.check_user_by_username_exists(
            user_auth_data.username
        )
        if not existing_user:
            raise HTTPException(401, "Invalid username or password")

        user = self.validate_password(user_auth_data.username, user_auth_data.password)
        if not user:
            raise HTTPException(401, "Invalid username or password")

        jwt_token_dict = self.prepare_jwt_tokens(user.id)
        return jwt_token_dict

    def logout(self, access_token: TokenInput, refresh_token: str):
        """Logout user by invalidating current tokens, if they are not already expired."""
        access_payload = None
        try:
            access_payload = jwt.decode(
                access_token.token,
                self.config.SECRET_KEY,
                algorithms=[self.config.ALGORITHM],
            )
            self.blacklist_token(access_token.token, access_payload["exp"])
        except jwt.ExpiredSignatureError:
            pass  # Access token is already expired, so we don't need to blacklist it

        try:
            refresh_payload = jwt.decode(
                refresh_token,
                self.config.SECRET_KEY,
                algorithms=[self.config.ALGORITHM],
            )
            self.blacklist_token(refresh_token, refresh_payload["exp"])
        except jwt.ExpiredSignatureError:
            pass  # Refresh token is already expired, so we don't need to blacklist it

    def list_users(self) -> UserReadList:
        users = self.user_repository.list_users()
        user_reads = [UserRead.model_validate(user) for user in users]
        return UserReadList(users=user_reads)

    def validate_password(self, username: str, password: str) -> User | None:
        """
        Validate password for user by input ID.
        Return user model if password is valid or None otherwise.
        """
        user = self.user_repository.get_by_username(username)
        if not user:
            return None

        hashed_password = User._make_salted_hash(password, user._salt)
        if hashed_password == user.password:
            return user

        return None

    def prepare_jwt_tokens(self, user_id: int) -> TokenPair:
        access_token, refresh_token = self.create_jwt_token_pair(user_id)
        return TokenPair(
            access_token=access_token, refresh_token=refresh_token, token_type="bearer"
        )

    def create_jwt_token_pair(
        self,
        user_id: int,
        config=config,
    ) -> tuple[str, str]:
        """Create new fresh access and refresh tokens, and return both"""
        access_to_encode = {}
        refresh_to_encode = {}
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise HTTPException(401, "Invalid username or password")

        access_expire = datetime.now(UTC) + config.ACCESS_TOKEN_EXPIRES
        refresh_expire = datetime.now(UTC) + config.REFRESH_TOKEN_EXPIRES
        access_to_encode.update({"sub": str(user_id), "exp": access_expire})
        refresh_to_encode.update({"sub": str(user_id), "exp": refresh_expire})

        encoded_access = jwt.encode(
            access_to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM
        )
        encoded_refresh = jwt.encode(
            refresh_to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM
        )
        return encoded_access, encoded_refresh

    def refresh_access_token(
        self,
        access_payload: dict | None,
        refresh_payload: dict,
        access_token: TokenInput,
        refresh_token: str,
    ) -> TokenPair:
        """Prepare new access token and blacklist previous one. Assume that refresh token is not expired"""
        if access_payload:  # blacklist access token if not expired
            self.blacklist_token(access_token.token, access_payload["exp"])
        new_token_pair = self.prepare_jwt_tokens(refresh_payload["sub"])
        # If refresh is expired too, we this will raise error - router should then raise http error, so frontend can redirect user to log in page
        self.blacklist_token(refresh_token, refresh_payload["exp"])

        return TokenPair(
            access_token=new_token_pair.access_token,
            refresh_token=new_token_pair.refresh_token,
            token_type="bearer",
        )

    def prepare_new_access_token(
        self,
        access_payload: dict,
        refresh_token: str,
        config=config,
    ) -> str:
        """Create new access token, after first validating current refresh token, and blacklisting old access token if it is still valid"""
        self.verify_token(refresh_token)

        user = self.user_repository.get_by_id(access_payload["sub"])
        if not user:
            raise HTTPException(401, "User does not exist")

        new_access_expire = datetime.now(UTC) + config.ACCESS_TOKEN_EXPIRES
        encoded_access = jwt.encode(
            {"sub": str(access_payload["sub"]), "exp": new_access_expire},
            config.SECRET_KEY,
            algorithm=config.ALGORITHM,
        )
        return encoded_access

    def prepare_refresh_token(
        self,
        user_id: int,
        data: dict | None = None,
        config=config,
    ) -> tuple[str, str]:
        if not data:
            data = {}
        access_to_encode = data.copy()
        refresh_to_encode = data.copy()
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise HTTPException(401, "Invalid username or password")

        access_expire = datetime.now(UTC) + config.ACCESS_TOKEN_EXPIRES
        refresh_expire = datetime.now(UTC) + config.REFRESH_TOKEN_EXPIRES
        access_to_encode.update({"sub": str(user_id), "exp": access_expire})
        refresh_to_encode.update({"sub": str(user_id), "exp": refresh_expire})

        encoded_access = jwt.encode(
            access_to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM
        )
        encoded_refresh = jwt.encode(
            refresh_to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM
        )
        return encoded_access, encoded_refresh

    def verify_token(self, token: str) -> dict:
        """
        Check if JWT token is valid and not expired.
        Return decoded payload if valid,
        otherwise raise HTTPException with appropriate message if expired or invalid.
        """
        try:
            payload = jwt.decode(
                token, self.config.SECRET_KEY, algorithms=[self.config.ALGORITHM]
            )
            user_id: str | None = payload.get("sub")
            if not user_id:
                raise HTTPException(401, "Invalid token")
            if self.expired_access_tokens_repository.is_blacklisted(token):
                raise TokenAlreadyBlacklisted
            return payload
        except jwt.ExpiredSignatureError:
            raise TokenExpired(401, "Token has expired")
        except jwt.InvalidTokenError as e:
            raise HTTPException(401, f"Invalid token: {e}")

    def authorize_current_user(self, token: Annotated[str, Depends(oauth2_scheme)]):
        """Check JWT access token if is valid, is not blacklisted, and return current user, otherwise raise 401 error"""
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        if self.expired_access_tokens_repository.is_blacklisted(token):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        try:
            payload = jwt.decode(
                token, self.config.SECRET_KEY, algorithms=[self.config.ALGORITHM]
            )
            user_id = payload.get("sub")
            if not user_id:
                raise credentials_exception
            token_data = JwtUser(user_id=user_id)
        except jwt.InvalidTokenError:
            raise credentials_exception

        user = self.user_repository.get_by_id(token_data.user_id)
        if user is None:
            raise credentials_exception
        return user

    def blacklist_token(self, token: str, expire_time):
        """Blacklist token by adding it to the expired tokens table"""
        # TODO: note: cleanup could run as regular cronjob for more optimal performance, not on every request
        self.expired_access_tokens_repository.expired_token_cleanup()
        self.expired_access_tokens_repository.blacklist_token(token, expire_time)


def get_auth_service(session: Annotated[Session, Depends(get_session)]) -> AuthService:
    """Return auth service with db session object dependency injected"""
    return AuthService(UserRepository(session), ExpiredTokenRepository(session))


async def authorize_current_user(
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    token: Annotated[str, Depends(oauth2_scheme)],
) -> User:
    """Authorizes request based on validity of attached access token. If valid, returns decoded info about current user."""
    return auth_service.authorize_current_user(token)
