from fastapi import Request, Depends, HTTPException, status
from apps.users.schemas.user import User
from fastapi.security import HTTPBearer


def get_current_user(request: Request) -> User:
    return request.state.user


class IsAuthenticated(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    def __call__(self, user: User = Depends(get_current_user)) -> User:
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"type": "auth.not_authorized"},
            )
        return user


def is_active():
    pass


def is_admin():
    pass
