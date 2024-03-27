# tests/test_environment.py


def test_environment():
    from app.config import ENVIRONMENT

    assert ENVIRONMENT == "testing"
