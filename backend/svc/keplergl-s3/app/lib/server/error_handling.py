import logging

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from starlette.requests import Request
from starlette.responses import JSONResponse

from ..dto.errors import ApiError
from .exceptions import ServerError, NotFoundError, CloudResourceError


async def handle_http_exception(exc: StarletteHTTPException):
    logging.error(str(exc))
    err: ApiError = ApiError.create_server_error(exc)
    logging.error(f"{err.err_type}:{err.detail}")
    return JSONResponse(status_code=err.err_code, content=err.dict())


async def handle_request_validation_exception(exc: RequestValidationError):
    for error in exc.errors():
        for item in error.items():
            logging.debug(item)
    err: ApiError = ApiError.create_validation_error(exc)
    logging.error(f"{err.err_type}:{err.detail}")

    return JSONResponse(status_code=err.err_code, content=err.dict())


async def handle_value_errors(exc: ValueError):
    err: ApiError = ApiError.create_validation_error(exc)
    logging.debug(f"{err.err_type}:{err.detail}")
    return JSONResponse(status_code=err.err_code, content=err.dict())


async def handle_not_found_error(exc):
    logging.error(str(exc))
    err: ApiError = ApiError.create_not_found_error(exc)
    logging.error(f"{err.err_type}:{err.detail}")
    return JSONResponse(status_code=err.err_code, content=err.dict())


async def handle_cloud_resource_error(exc):
    logging.error(str(exc))
    err: ApiError = ApiError.create_cloud_resource_error(exc)
    logging.error(f"{err.err_type}:{err.detail}")
    return JSONResponse(status_code=err.err_code, content=err.dict())


async def handle_server_error(exc):
    logging.error(str(exc))
    err: ApiError = ApiError.create_server_error(exc)
    logging.error(f"{err.err_type}:{err.detail}")
    return JSONResponse(status_code=err.err_code, content=err.dict())


def add_error_handling(app: FastAPI):
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(_request: Request, exc: StarletteHTTPException) -> JSONResponse:
        return await handle_http_exception(exc)

    @app.exception_handler(ValueError)
    async def value_error_handler(_request: Request, exc: ValueError) -> JSONResponse:
        return await handle_value_errors(exc)

    @app.exception_handler(RequestValidationError)
    async def request_validation_error_handler(_request: Request, exc: RequestValidationError) -> JSONResponse:
        return await handle_request_validation_exception(exc)

    @app.exception_handler(Exception)
    async def exception_handler(_request: Request, exc: ServerError) -> JSONResponse:
        return await handle_server_error(exc)

    @app.exception_handler(ServerError)
    async def server_error_handler(_request: Request, exc: ServerError) -> JSONResponse:
        return await handle_server_error(exc)

    @app.exception_handler(NotFoundError)
    async def not_found_error_handler(_request: Request, exc: NotFoundError) -> JSONResponse:
        return await handle_not_found_error(exc)

    @app.exception_handler(CloudResourceError)
    async def cloud_resource_error_handler(_request: Request, exc: CloudResourceError) -> JSONResponse:
        return await handle_cloud_resource_error(exc)
