from pydantic import BaseModel, ConfigDict


class UserCreate(BaseModel):
    username: str
    email: str
    password: str


class UserAuthenticate(BaseModel):
    username: str
    password: str


class UserRead(BaseModel):
    id: int
    username: str
    email: str

    model_config = ConfigDict(from_attributes=True)


class UserReadList(BaseModel):
    users: list[UserRead]
    model_config = ConfigDict(from_attributes=True)


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class TokenInput(BaseModel):
    """Only a token."""

    token: str


class Token(BaseModel):
    """Response for requests. Access token will live in cookies only."""

    token: str
    token_type: str

    @staticmethod
    def access_token_from_pair(token_pair: TokenPair) -> "Token":
        return Token(token=token_pair.access_token, token_type=token_pair.token_type)


class JwtUser(BaseModel):
    user_id: int

    model_config = ConfigDict(from_attributes=True)
