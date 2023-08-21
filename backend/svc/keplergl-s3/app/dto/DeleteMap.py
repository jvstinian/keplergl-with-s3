# app/dto/DeleteMap.py
from typing import Optional
from pydantic import BaseModel, Field


class DeleteMapResponse(BaseModel):
    success: bool = Field(..., description="Success flag")
    message: Optional[str] = Field(default=None, description="Message providing additional info, particularly when an error is encountered")
    mapId: Optional[str] = Field(default=None, description="Map ID of deleted map")
