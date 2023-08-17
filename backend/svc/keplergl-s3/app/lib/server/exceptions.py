# app/lib/server/exceptions.py


class BaseServerException(Exception):
    def __init__(self, name: str):
        self.name = name


class ServerError(BaseServerException):
    pass


class DatabaseError(ServerError):
    pass


class TooManyMatchingRecords(DatabaseError):
    pass


class NoMatchingRecordFound(DatabaseError):
    pass


class NoResultSetProducedByQuery(DatabaseError):
    pass


class DataLookupError(DatabaseError):
    pass


class NotFoundError(BaseServerException):
    pass


class CloudResourceError(BaseServerException):
    pass

