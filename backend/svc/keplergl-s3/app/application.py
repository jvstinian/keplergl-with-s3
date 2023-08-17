# app/application.py
import logging
from fastapi import FastAPI
from .config import ENVIRONMENT
from .controllers import keplergl_s3_controller
from .lib.logs import get_level_from_environment, setup_logging
from .lib.server.error_handling import add_error_handling
from .lib.server.health import add_health_check
from .lib.server.middleware import add_session_middleware


def create_app(title: str, environment=None, **kwargs) -> FastAPI:
    """Creates FastApi app, adds middleware, and health endpoint.
    :param title:
    :return:
    :raises: OperationalError
    """
    if not environment:
        environment = ENVIRONMENT

    try:
        setup_logging(get_level_from_environment(environment), json_formatting=environment != "testing")
    except OperationalError as dberr:
        logging.error(f"Error with database connection: {dberr}", exc_info=True)
        raise dberr

    if ENVIRONMENT == "development":
        kwargs["openapi_url"] = "/_openapi.json"
        kwargs["docs_url"] = "/_docs"
        kwargs["redoc_url"] = "/_redoc"
    else:
        kwargs["openapi_url"] = None
        kwargs["docs_url"] = None
        kwargs["redoc_url"] = None

    app: FastAPI = FastAPI(title=title, **kwargs)

    add_health_check(app)
    add_error_handling(app)

    app.include_router(keplergl_s3_controller.router, prefix="/keplergl-s3")

    add_session_middleware(app)

    return app

