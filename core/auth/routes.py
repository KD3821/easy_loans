from fastapi import Response, Request
from fastapi.routing import APIRoute
from typing import Callable

from .auth_token import AuthToken

from apps.users.schemas.user import User


class BaseRoute(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            authorization_header = request.headers.get('authorization', None)

            if not authorization_header:
                request.state.user = None
            else:
                token = authorization_header.split(' ')[-1]
                request.state.user = User(**AuthToken.decrypt_token(token))
            response = await original_route_handler(request)
            return response

        return custom_route_handler
