from fastapi import HTTPException


class TokenExpired(HTTPException): ...

# raised in service layer
class CredentialsAlreadyUsed(Exception): ...