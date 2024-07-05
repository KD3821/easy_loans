from fastapi import Request, Response
from .logger import logger
from starlette.concurrency import iterate_in_threadpool


async def log_requets_params(request: Request):
    """
    Logging request data
    The full data example:
    logger.info(
        f"{request.method} request to {request.url} metadata\n"
        f"\tHeaders: {request.headers}\n"
        f"\tBody: {request_body}\n"
        f"\tPath Params: {request.path_params}\n"
        f"\tQuery Params: {request.query_params}\n"
        f"\tCookies: {request.cookies}\n"
    )
    Example from: https://stackoverflow.com/a/70627497
    """
    try:
        try:
            request_body = await request.json()
        except Exception:
            request_body = await request.body()
    except Exception:
        request_body = None

    logger.info(
        f"{request.method} request to {request.url} metadata\n"
        f"\tHeaders: {request.headers}\n"
        f"\tBody: {request_body}\n"
        f"\tPath Params: {request.path_params}\n"
        f"\tQuery Params: {request.query_params}"
    )


async def log_response_params(request: Request, call_next) -> Response:
    """
    Logging response body
    Example from: https://github.com/encode/starlette/issues/874#issuecomment-1027743996
    """
    response = await call_next(request)
    response_body = [section async for section in response.body_iterator]
    response.body_iterator = iterate_in_threadpool(iter(response_body))
    if len(response_body) > 0:
        logger.info(f"Response_body: {response_body[0].decode()}")
    return response
