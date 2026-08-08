from fastapi import HTTPException


class TokenExpired(HTTPException): ...


class CredentialsAlreadyUsed(Exception): ...


class TokenAlreadyBlacklisted(Exception): ...
