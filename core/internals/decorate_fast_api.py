from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi import status
from settings import LOG_RESPONSE
from ..loggers.log_request import log_response_params
from .get_openapi_schema import get_openapi_schema


def decorate_fast_api(fast_api):
    @fast_api.on_event("startup")
    async def startup():
        # do smth
        pass

    @fast_api.on_event("shutdown")
    async def shutdown():
        # do smth
        pass

    @fast_api.exception_handler(RequestValidationError)
    async def validation_exception_handler(request, exc: RequestValidationError):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=jsonable_encoder({"detail": exc.errors()}),
        )

    fast_api.openapi = get_openapi_schema(fast_api)

    if LOG_RESPONSE:
        # Based on the settings logging response body
        fast_api.middleware("http")(log_response_params)
