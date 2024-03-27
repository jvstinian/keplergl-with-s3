FROM ghcr.io/jvstinian/keplergl-s3/keplergl-s3-base:latest

VOLUME /opt/keplergl-s3-svc

ENTRYPOINT ["/opt/keplergl-s3-svc-site-packages/bin/uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

EXPOSE 8000

