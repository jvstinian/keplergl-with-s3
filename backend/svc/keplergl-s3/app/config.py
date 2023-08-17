# app/config.py
import os
from starlette.config import Config as StarletteConfig, environ
from starlette.datastructures import Secret

get_config: StarletteConfig = StarletteConfig()

PROJECT_NAME = "Kepler.gl S3 Service"
SECRET_KEY = os.getenvb(b"SECRET_KEY") # TODO: Is this needed?
if not SECRET_KEY:
    SECRET_KEY = os.urandom(32)

ENVIRONMENT = environ.get("ENVIRONMENT", "development")
TESTING = get_config("TESTING", cast=bool, default=False)
SQLECHO = get_config("SQLECHO", cast=bool, default=None) # TODO: Is this needed?

S3_ENDPOINT_URL = get_config("S3_ENDPOINT_URL", cast=str, default=None)

def set_environment(env: str):
    environ["ENVIRONMENT"] = env

KEPLERGL_S3_BUCKET = environ.get("KEPLERGL_S3_BUCKET", None)
KEPLERGL_S3_USER = "keplergl-s3-user" # TODO: Make into an environment variable, perhaps as a prefix

