from datetime import datetime, timezone
import logging
from typing import Annotated

from fastapi import Depends, HTTPException, Response
from fastapi.security import OAuth2PasswordBearer
import jwt
from sqlalchemy.orm import Session
from starlette import status

from services.exceptions import TokenExpired
from models.auth import User
from config.settings import Config, config, get_config
from db import get_session
from repositories.users import UserRepository
from schemas.auth import JwtUser, TokenPair, UserAuthenticate, UserRead, UserReadList


logger = logging.getLogger()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)


class AuthService:
    def __init__(self, user_repository: UserRepository):
        self.config: Config = config
        self.user_repository: UserRepository = user_repository

    def login(self, user_auth_data: UserAuthenticate) -> TokenPair:
        """Takes input credentials, checks if they are valid, and returns JWT token pair."""
        existing_user = self.user_repository.check_user_by_username_exists(
            user_auth_data.username
        )
        if not existing_user:
            raise HTTPException(401, "Invalid username or password")

        user = self.validate_password(user_auth_data.username, user_auth_data.password)
        if not user:
            raise HTTPException(401, "Invalid username or password")

        jwt_token_dict = self.prepare_jwt_tokens(user.id)
        # response.set_cookie(**jwt_token_dict)
        return jwt_token_dict

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
        data: dict = {},
        config=get_config(),
    ) -> tuple[str, str]:
        access_to_encode = data.copy()
        refresh_to_encode = data.copy()
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise HTTPException(401, "Invalid username or password")

        access_expire = datetime.now(timezone.utc) + config.ACCESS_TOKEN_EXPIRES
        refresh_expire = datetime.now(timezone.utc) + config.REFRESH_TOKEN_EXPIRES
        access_to_encode.update({"sub": str(user_id), "exp": access_expire})
        refresh_to_encode.update({"sub": str(user_id), "exp": refresh_expire})

        encoded_access = jwt.encode(
            access_to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM
        )
        encoded_refresh = jwt.encode(
            refresh_to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM
        )
        return encoded_access, encoded_refresh

    # def create_refresh_token(self, username: str):
    #     to_encode = dict()
    #     user = self.user_repository.get_by_username(username)
    #     if user:
    #         user_id = user.id
    #     else:
    #         raise HTTPException(401, "Invalid username or password")

    #     to_encode.update(
    #         {
    #             "sub": user_id,
    #         }
    #     )

    #     expire = datetime.now(timezone.utc) + config.ACCESS_TOKEN_EXPIRES
    #     to_encode.update({"exp": expire})

    #     encoded_jwt = jwt.encode(
    #         to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM
    #     )
    #     return encoded_jwt

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
            user_id: str = payload.get("sub")
            if not user_id:
                raise HTTPException(401, "Invalid token")
            return payload
        except jwt.ExpiredSignatureError:
            raise TokenExpired(401, "Token has expired")
        except jwt.InvalidTokenError as e:
            raise HTTPException(401, f"Invalid token: {str(e)}")

    def authorize_current_user(self, token: Annotated[str, Depends(oauth2_scheme)]):
        """Check JWT access token if is valid, and return current user, otherwise raise 401 error"""
        credentials_exception = HTTPException(
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


def get_auth_service(session: Annotated[Session, Depends(get_session)]) -> AuthService:
    """Return auth service with db session object dependency injected"""
    return AuthService(UserRepository(session))


async def authorize_current_user(
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    token: Annotated[str, Depends(oauth2_scheme)],
) -> User:
    """Authorizes request based on validity of attached access token. If valid, returns decoded info about current user."""
    return auth_service.authorize_current_user(token)
