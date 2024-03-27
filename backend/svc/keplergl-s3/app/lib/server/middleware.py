# app/lib/server/middleware/store.py
import logging
from typing import List, Tuple
from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import Response


def debug_log_state(request: Request, fieldname: str) -> None:
    if hasattr(request.state, fieldname) and getattr(request.state, fieldname, None):
        logging.debug(f"Added {fieldname} to state")
    else:
        logging.debug(f"Fieldname: {fieldname} missing from state")


def add_session_middleware(app: FastAPI, additional_state: List[Tuple] = None) -> FastAPI:
    """Middleware that adds certain important objects to request.state.
       Objects can be passed as a list of tuples.
    :param app:
    :param additional_state:
    :return:
    """

    @app.middleware("http")
    async def object_session_middleware(request: Request, call_next) -> Response:
        """Session middleware that adds objects to request.state.
        :param request:
        :param call_next:
        :return:
        """
        try:
            if additional_state:
                for k, v in additional_state:
                    setattr(request.state, k, v)
                    debug_log_state(request, k)
            response: Response = await call_next(request)
            return response
        finally:
            pass

    return app
