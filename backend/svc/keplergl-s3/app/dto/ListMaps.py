# app/dto/ListMaps.py
from typing import Optional, List
from pydantic import BaseModel, Field

from app.dto.UploadMap import MapDetailResponse


class ListMapsResponse(BaseModel):
    success: bool = Field(..., description="Success flag")
    message: Optional[str] = Field(
        default=None, 
        description="Message providing additional info, particularly when an error is encountered"
    )
    mapDetails: Optional[List[MapDetailResponse]] = Field(default=None, description="Map Detail List")

