# app/main.py
from fastapi import FastAPI

from .application import create_app
from .config import PROJECT_NAME, ENVIRONMENT

from .lib.logs import get_level_from_environment, setup_logging

setup_logging(level=get_level_from_environment(ENVIRONMENT))

app: FastAPI = create_app(PROJECT_NAME)
