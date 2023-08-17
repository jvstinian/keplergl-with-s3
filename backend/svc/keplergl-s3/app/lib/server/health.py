from fastapi import FastAPI
from starlette.responses import Response


def add_health_check(app: FastAPI):
    @app.get("/health", tags=["health"], summary="Health check")
    def health():
        return Response(content="OK")
