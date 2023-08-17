# app/dto/DownloadMap.py


from typing import Optional
from pydantic import BaseModel, Field

from app.dto.UploadMap import MapDetailResponse


class DownloadMapDetailResponse(BaseModel):
    success: bool = Field(..., description="Success flag")
    message: Optional[str] = Field(
        default=None, 
        description="Message providing additional info, particularly when an error is encountered"
    )
    mapDetail: Optional[MapDetailResponse] = Field(default=None, description="Map Detail")

