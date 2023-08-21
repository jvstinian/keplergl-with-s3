# app/lib/logs/logs.py

import datetime
import logging
import time
from typing import Any, Optional
from logging import StreamHandler

from pythonjsonlogger import jsonlogger


allowed_scope_values = [
    "type",
    "http_version",
    "server",
    "client",
    "scheme",
    "method",
    "root_path",
    "path",
    "raw_path",
    "query_string",
    "headers",
    "path_params",
]


class AccessLogFilter(logging.Filter):
    def filter(self, record):
        # We use a slightly different approach here as we handle uvicorn.acccess logs
        if hasattr(record, "scope"):
            return record.scope.get("path", None) not in ["/health"]
        else:
            return True


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def formatTime(self, record, datefmt=None):
        ct = self.converter(record.created)
        if datefmt:
            s = time.strftime(datefmt, ct)
        else:
            t = datetime.datetime.utcnow()
            s = t.isoformat(" ")
        return s

    def process_log_record(self, log_record):
        if "scope" in log_record:
            log_record["scope"] = {k: v for (k, v) in log_record.pop("scope").items() if k in allowed_scope_values}
        if "name" in log_record:
            log_record["module"] = log_record.pop("name")
        log_record["level"] = log_record.pop("levelname", "info").lower()
        log_record["msg"] = log_record.pop("message", "no message")
        log_record["time"] = log_record.pop("asctime", datetime.datetime.utcnow().isoformat(" "))
        return jsonlogger.JsonFormatter.process_log_record(self, log_record)


def setup_logging(level: Optional[int] = logging.INFO, stream: Optional[Any] = None, json_formatting=True) -> Any:
    handler = StreamHandler(stream=stream)
    format_str = "%(message)%(levelname)%(name)%(asctime)"

    if json_formatting:
        formatter = CustomJsonFormatter(format_str)
        handler.setFormatter(formatter)

    handler.setLevel(level)
    handler.propagate = False
    logging.basicConfig()
    logging.getLogger("boto3").setLevel(logging.CRITICAL)
    logging.getLogger("botocore").setLevel(logging.CRITICAL)
    logging.getLogger("s3transfer").setLevel(logging.CRITICAL)
    logging.getLogger("s3regionredirector").setLevel(logging.CRITICAL)
    logging.getLogger("urllib3").setLevel(logging.CRITICAL)
    logging.getLogger("uvicorn").setLevel(logging.WARN)
    logging.getLogger("gunicorn.access").addFilter(AccessLogFilter())
    logging.getLogger("uvicorn.access").addFilter(AccessLogFilter())
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.handlers = []
    root_logger.addHandler(handler)

    # We use a slightly different approach here as we handle uvicorn.acccess logs
    uvicorn_logger = logging.getLogger("uvicorn.access")
    uvicorn_logger.handlers = []
    uvicorn_logger.addHandler(handler)


def get_level_from_environment(environment: str) -> int:
    level: int = logging.DEBUG if environment in ["development"] else logging.INFO
    return level


def get_logger(name: str) -> logging.Logger:
    import logging

    return logging.getLogger(name)
