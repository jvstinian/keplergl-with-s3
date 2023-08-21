from io import StringIO
import json
import logging

import pytest

from app.lib.logs import setup_logging, get_level_from_environment


@pytest.mark.parametrize(
    "log_level,level_call,expected_level",
    [(logging.INFO, logging.info, "info"), (logging.WARNING, logging.warning, "warning"), (logging.ERROR, logging.error, "error")],
)
def test_logging_format(log_level, level_call, expected_level):
    from app.config import ENVIRONMENT

    buffer = StringIO()
    setup_logging(level=get_level_from_environment(ENVIRONMENT), stream=buffer)

    logging.getLogger().setLevel(log_level)
    level_call("This is a test")
    logJson = json.loads(buffer.getvalue())
    assert logJson.get("level", "") == expected_level
    assert logJson.get("msg", "") == "This is a test"
    assert logJson.get("time", False)
