from apps.users.models import User
from apps.users.schemas.user import TokenUser
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer


def get_current_user(request: Request) -> TokenUser:
    return request.state.user


class IsAuthenticated(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    def __call__(self, user: TokenUser = Depends(get_current_user)) -> TokenUser:
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"type": "auth.not_authorized"},
            )
        return user


class HasManagerRole(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    def __call__(self, user: TokenUser = Depends(get_current_user)) -> TokenUser:
        if not user:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"type": "auth.not_authenticated"},
            )
        if user.role != User.MANAGER:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"type": "auth.not_authorized"},
            )
        return user


def is_active():
    pass


def is_admin():
    pass
