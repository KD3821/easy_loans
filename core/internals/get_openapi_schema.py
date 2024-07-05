from fastapi.openapi.utils import get_openapi
from settings import APP_API_NAME, APP_VERSION


def get_openapi_schema(fast_api):
    def inner_function():
        if fast_api.openapi_schema:
            return fast_api.openapi_schema

        openapi_schema = get_openapi(
            title=APP_API_NAME,
            version=APP_VERSION,
            routes=fast_api.routes,
        )

        # replaces 422 response with 400 in open api schema
        for method in openapi_schema["paths"]:
            try:
                for path in openapi_schema["paths"]:
                    for method in openapi_schema["paths"][path]:
                        if openapi_schema["paths"][path][method]["responses"].get("422"):
                            openapi_schema["paths"][path][method]["responses"][
                                "400"
                            ] = openapi_schema["paths"][path][method]["responses"]["422"]
                            openapi_schema["paths"][path][method]["responses"].pop("422")
                fast_api.openapi_schema = openapi_schema
                return fast_api.openapi_schema
            except KeyError:
                pass

        fast_api.openapi_schema = openapi_schema
        return fast_api.openapi_schema

    return inner_function
