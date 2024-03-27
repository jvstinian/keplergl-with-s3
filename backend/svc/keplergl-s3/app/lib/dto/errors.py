# app/lib/dto/errors.py
from pydantic import BaseModel, Field


class ApiErrorType(BaseModel):
    err_type: str
    err_code: int


class ApiErrorTypes:
    VALIDATION_ERROR = ApiErrorType(err_code=422, err_type="Validation Error")
    NOT_FOUND_ERROR = ApiErrorType(err_code=404, err_type="Not Found Error")
    SERVER_ERROR = ApiErrorType(err_code=500, err_type="Server Error")
    CLOUD_RESOURCE_ERROR = ApiErrorType(err_code=503, err_type="Cloud Resource Error")


class ApiError(BaseModel):  # pydantic cannot flatten inherited models
    err_code: int = Field(..., description="HTTP Status code")
    err_type: str = Field(..., description="Type of error. User facing")
    detail: str = Field(..., description="Detailed error message - user facing")

    class Config:
        validate_assignment = True

    @classmethod
    def create_error(cls, exc, api_error_type: ApiErrorType, detail=None):
        if not detail:
            detail = str(exc)
        api_err = api_error_type.dict()

        return ApiError(**api_err, detail=detail)

    @classmethod
    def create_server_error(cls, exc, detail=None):
        return ApiError.create_error(exc, api_error_type=ApiErrorTypes.SERVER_ERROR, detail=detail)

    @classmethod
    def create_validation_error(cls, exc, detail=None):
        return ApiError.create_error(exc, api_error_type=ApiErrorTypes.VALIDATION_ERROR, detail=detail)

    @classmethod
    def create_not_found_error(cls, exc, detail=None):
        return ApiError.create_error(exc, api_error_type=ApiErrorTypes.NOT_FOUND_ERROR, detail=detail)

    @classmethod
    def create_cloud_resource_error(cls, exc, detail=None):
        return ApiError.create_error(exc, api_error_type=ApiErrorTypes.CLOUD_RESOURCE_ERROR, detail=detail)
