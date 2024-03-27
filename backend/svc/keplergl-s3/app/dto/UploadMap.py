# app/dto/UploadMap.py
from typing import Optional, List
from pydantic import BaseModel, Field
import datetime


class MapDetailRequest(BaseModel):
    id: Optional[str] = Field(default=None)
    name: str = Field(...)
    description: Optional[str] = Field(default=None)
    thumbnail: str = Field(...)
    config: dict = Field(...)
    privateMap: bool = Field(...)


class DatasetDetail(BaseModel):
    id: str = Field(...)
    label: Optional[str] = Field(default=None)


class DatasetDetailList(BaseModel):
    __root__: List[DatasetDetail]


class MapDetailResponse(BaseModel):
    id: str = Field(...)
    name: str = Field(...)
    description: Optional[str] = Field(default=None)
    thumbnail: str = Field(...)
    config: dict = Field(...)
    privateMap: bool = Field(...)
    datasetDetails: List[DatasetDetail] = Field(...)
    lastModification: datetime.datetime = Field(...)
    active: Optional[bool] = Field(default=True)


class UploadMapResponse(BaseModel):
    success: bool = Field(..., description="Success flag")
    message: Optional[str] = Field(default=None, description="Message providing additional info, particularly when an error is encountered")
    mapDetail: Optional[MapDetailResponse] = Field(default=None, description="Map metadata")
