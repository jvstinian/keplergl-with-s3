# app/controllers/keplergl_s3_controller.py
from typing import List
import logging
from fastapi import APIRouter, Depends, UploadFile, File, Form
import boto3

from app.config import ENVIRONMENT, S3_ENDPOINT_URL
from app.lib.logs import get_level_from_environment, setup_logging
from app.dto.UploadMap import UploadMapResponse
from app.dto.ListMaps import ListMapsResponse
from app.dto.DownloadMap import DownloadMapDetailResponse
from app.dto.DeleteMap import DeleteMapResponse
from app.processors.keplergl_s3_processor import (
    UploadMapProcessor,
    get_upload_map_processor,
    ListMapsProcessor,
    get_list_maps_processor,
    DownloadMapProcessor,
    get_download_map_processor,
    SoftDeleteMapProcessor,
    get_soft_delete_map_processor,
)


router = APIRouter()

setup_logging(get_level_from_environment(ENVIRONMENT), json_formatting=ENVIRONMENT != "testing")

logging.debug(f"S3_ENDPOINT_URL: {S3_ENDPOINT_URL}") # TODO

s3client = boto3.client('s3', endpoint_url=S3_ENDPOINT_URL)

@router.post("/uploadMap", response_model=UploadMapResponse, tags=["keplergl-s3"])
def upload_map(
    *,
    mapDetail: str = Form(...),
    datasetDetails: str = Form(...),
    datasets: List[UploadFile] = File(...),
    datasetsColumns: List[UploadFile] = File(...),
    proc: UploadMapProcessor = Depends(get_upload_map_processor),
):
    logging.debug("keplergl-s3 controller upload map request")
    return proc.upload_maps(s3client, mapDetail, datasetDetails, datasets, datasetsColumns)

@router.get("/listMaps", response_model=ListMapsResponse, tags=["keplergl-s3"])
def list_maps(
    proc: ListMapsProcessor = Depends(get_list_maps_processor),
):
    logging.debug("keplergl-s3 controller list maps request")
    return proc.list_maps(s3client)

@router.get("/downloadMapDetail/{map_id}/mapdetail.json", response_model=DownloadMapDetailResponse, tags=["keplergl-s3"])
def download_map_detail(
    map_id: str,
    proc: DownloadMapProcessor = Depends(get_download_map_processor),
): 
    logging.debug("keplergl-s3 controller download map detail request")
    return proc.download_map_detail(s3client, map_id)

@router.get("/downloadMapDataset/{map_id}/{dataset_id}/data.csv", tags=["keplergl-s3"])
async def download_map_dataset(
    map_id: str, 
    dataset_id: str,
    proc: DownloadMapProcessor = Depends(get_download_map_processor),
):
    logging.debug("keplergl-s3 controller download map dataset request")
    return proc.download_map_dataset(s3client, map_id, dataset_id)

@router.get("/downloadMapColumns/{map_id}/{dataset_id}/columns.json", tags=["keplergl-s3"])
async def download_map_columns(
    map_id: str, 
    dataset_id: str,
    proc: DownloadMapProcessor = Depends(get_download_map_processor),
):
    logging.debug("keplergl-s3 controller download map columns request")
    return proc.download_map_columns(s3client, map_id, dataset_id)

@router.delete("/deleteMap/{map_id}", tags=["keplergl-s3"])
async def delete_map(
    map_id: str, 
    proc: SoftDeleteMapProcessor = Depends(get_soft_delete_map_processor),
):
    logging.debug("keplergl-s3 controller delete map request")
    return proc.soft_delete(s3client, map_id)

