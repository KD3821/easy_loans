from fastapi import Depends, FastAPI
from settings import LOG_REQUEST
from starlette.middleware.cors import CORSMiddleware

from ..loggers.log_request import log_requets_params
from .decorate_fast_api import decorate_fast_api
from .get_routers import GetRouters

SUPPORTED_VERSIONS = ("v1",)


def get_application() -> FastAPI:
    """
    Makes Fast API instance,
    Add middlewares,
    Import all routers and are in router_<x>.py files
    """
    app = FastAPI()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    for version in SUPPORTED_VERSIONS:
        routers_data = GetRouters.call(version)

        for router_data in routers_data:
            if router_data.get("prefix"):
                prefix = f"/api/{version}/{router_data.get('prefix')}"
            else:
                prefix = f"/api/{version}"

            extra_params = router_data.get("extra_params", {})

            if LOG_REQUEST:
                # Based on settings logging request with body and headers
                dependencies = extra_params.pop("dependencies", [])
                dependencies.append(Depends(log_requets_params))

            app.include_router(
                router_data["router"],
                prefix=prefix,
                **extra_params,
                dependencies=dependencies,
            )

    # decorate Fast API application with some additional handlers for events, requests, etc
    decorate_fast_api(app)

    return app
