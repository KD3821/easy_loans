from datetime import timedelta
from fastapi import HTTPException, status
from fastapi_jwt import (
    JwtAccessBearer,
)
from jose import jwt
from settings import (
    AUTH_ACCESS_TOKEN_EXPIRE_MINUTES,
    AUTH_SECRET_KEY,
    AUTH_REFRESH_TOKEN_EXPIRE_MINUTES,
)


access_security = JwtAccessBearer(
    secret_key=AUTH_SECRET_KEY,
    auto_error=False,
    access_expires_delta=timedelta(minutes=AUTH_ACCESS_TOKEN_EXPIRE_MINUTES),
)


class AuthToken:
    """
    Using fastapi-jwt-auth
    https://indominusbyte.github.io/fastapi-jwt-auth/usage/basic/
    """

    def generate_access_token(data: dict) -> str:
        return access_security.create_access_token(subject=data)

    @staticmethod
    def generate_pair(data: dict) -> dict:
        expires_refresh_token = timedelta(minutes=AUTH_REFRESH_TOKEN_EXPIRE_MINUTES)
        return {
            "access_token": access_security.create_access_token(subject=data),
            "refresh_token": access_security.create_refresh_token(
                subject=data, expires_delta=expires_refresh_token
            ),
        }

    @staticmethod
    def decrypt_token(token: str) -> dict:
        if token:
            try:
                encoded = jwt.decode(token, key=AUTH_SECRET_KEY)
            except Exception:
                encoded = None

            data = type(encoded) is dict and encoded.get("subject")

            if not data:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail={"type": "auth.token_invalid"},
                )

            return data

        return None
