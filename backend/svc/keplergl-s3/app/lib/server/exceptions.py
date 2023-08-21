# app/lib/server/exceptions.py


class BaseServerException(Exception):
    def __init__(self, name: str):
        self.name = name


class ServerError(BaseServerException):
    pass


class NotFoundError(BaseServerException):
    pass


class CloudResourceError(BaseServerException):
    pass
