import uvicorn
import settings
from core import logger, get_application  # noqa # pylint: disable=unused-import


# use 'api:fast_api' to run using uvicorn/gunicorn like the following:
# gunicorn -w 4 -k uvicorn.workers.UvicornWorker api:fast_api
# instead of using uvicorn/gunicorn directly in python like below

fast_api = get_application()

if __name__ == "__main__":
    logger.info(f"Application is working on {settings.PORT} port\n")
    uvicorn.run("api:fast_api", host=settings.HOST, port=settings.PORT,
                log_level=settings.LOG_LEVEL.lower(), reload=settings.HOT_RELOAD
                )
