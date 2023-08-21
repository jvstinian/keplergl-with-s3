# app/config.py
from starlette.config import Config as StarletteConfig, environ

get_config: StarletteConfig = StarletteConfig()

PROJECT_NAME = "Kepler.gl S3 Service"
ENVIRONMENT = environ.get("ENVIRONMENT", "development")

S3_ENDPOINT_URL = get_config("S3_ENDPOINT_URL", cast=str, default=None)

KEPLERGL_S3_BUCKET = environ.get("KEPLERGL_S3_BUCKET", None)
KEPLERGL_S3_USER = "keplergl-s3-user"
