# app/processors/keplergl_s3_processor.py
from typing import List
import logging
import datetime
from uuid import UUID, uuid4
from fastapi import UploadFile
from fastapi.responses import StreamingResponse

from app.config import ENVIRONMENT
from app.lib.logs import get_level_from_environment, setup_logging
from app.dto.UploadMap import MapDetailRequest, DatasetDetailList, MapDetailResponse, UploadMapResponse
from app.dto.ListMaps import ListMapsResponse
from app.dto.DownloadMap import DownloadMapDetailResponse
from app.dto.DeleteMap import DeleteMapResponse
from app.stores.keplergl_s3 import (
    moveCurrentMapToArchive,
    uploadDatasetToS3,
    uploadColumnsJsonToS3,
    uploadMapDetailToS3,
    getMapDetailFromS3,
    getMapDetailsListFromS3,
    getDatasetFromS3,
    getColumnsFromS3,
    softDeleteMapFromS3,
)


setup_logging(get_level_from_environment(ENVIRONMENT), json_formatting=ENVIRONMENT != "testing")


class UploadMapProcessor:
    def __init__(self):
        pass

    def upload_maps(
        self, s3client, mapDetail: str, datasetDetails: str, datasets: List[UploadFile], datasetsColumns: List[UploadFile]
    ) -> UploadMapResponse:
        mapDetailReq = MapDetailRequest.parse_raw(mapDetail)
        req_id = mapDetailReq.id
        logging.info(f"uploading map for ID {req_id}")

        id = None
        overwrite = False
        if req_id is None:
            id = str(uuid4())
        else:
            # The following can raise a ValueError, which
            # is treated as a validation error
            id = str(UUID(req_id, version=4))
            overwrite = True

        parsedDatasetDetails = DatasetDetailList.parse_raw(datasetDetails).__root__

        if len(parsedDatasetDetails) != len(datasets):
            raise ValueError("The number of datasets does not match the number of ids")

        if len(parsedDatasetDetails) != len(datasetsColumns):
            raise ValueError("The number of dataset schemas does not match the number of ids")

        if overwrite:
            moveCurrentMapToArchive(s3client, id)

        for datasetDetail, dataset, columns in zip(parsedDatasetDetails, datasets, datasetsColumns):
            datasetId = datasetDetail.id
            uploadDatasetToS3(s3client, id, datasetId, dataset)
            uploadColumnsJsonToS3(s3client, id, datasetId, columns)

        mapDetail = MapDetailResponse(
            id=id,
            name=mapDetailReq.name,
            description=mapDetailReq.description,
            thumbnail=mapDetailReq.thumbnail,
            config=mapDetailReq.config,
            privateMap=mapDetailReq.privateMap,
            datasetDetails=parsedDatasetDetails,
            lastModification=datetime.datetime.now().isoformat(timespec="seconds"),
            active=True,
        )
        uploadMapDetailToS3(s3client, id, mapDetail)

        msg = f"Received {len(datasets)} datasets"
        return UploadMapResponse(success=True, message=msg, mapDetail=mapDetail)


def get_upload_map_processor() -> UploadMapProcessor:
    logging.debug("In get_upload_map_processor, returning new instance of UploadMapProcessor")
    return UploadMapProcessor()


class ListMapsProcessor:
    def __init__(self):
        pass

    def list_maps(self, s3client) -> ListMapsResponse:
        mapDetails = getMapDetailsListFromS3(s3client)
        activeMapDetails = list(filter(lambda mapDetail: (mapDetail.active is None) or mapDetail.active, mapDetails))
        return ListMapsResponse(success=True, message=None, mapDetails=activeMapDetails)


def get_list_maps_processor() -> ListMapsProcessor:
    logging.debug("In get_list_maps_processor, returning new instance of ListMapsProcessor")
    return ListMapsProcessor()


class DownloadMapProcessor:
    def __init__(self):
        pass

    def download_map_detail(self, s3client, map_id: str) -> DownloadMapDetailResponse:
        mapDetail = getMapDetailFromS3(s3client, map_id)
        logging.info(f"Got map detail for {mapDetail.id}")
        return DownloadMapDetailResponse(success=True, message=None, mapDetail=mapDetail)

    def download_map_dataset(self, s3client, map_id: str, dataset_id: str) -> StreamingResponse:
        body = getDatasetFromS3(s3client, map_id, dataset_id)
        return StreamingResponse(
            content=body.iter_chunks(), media_type="text/csv", headers={"Content-Disposition": 'inline; filename="data.csv"'}
        )

    def download_map_columns(self, s3client, map_id: str, dataset_id: str) -> StreamingResponse:
        body = getColumnsFromS3(s3client, map_id, dataset_id)
        return StreamingResponse(
            content=body.iter_chunks(), media_type="application/json", headers={"Content-Disposition": 'inline; filename="columns.json"'}
        )


def get_download_map_processor() -> DownloadMapProcessor:
    logging.debug("In get_download_map_processor, returning new instance of DownloadMapProcessor")
    return DownloadMapProcessor()


class SoftDeleteMapProcessor:
    def __init__(self):
        pass

    def soft_delete(self, s3client, map_id: str) -> DeleteMapResponse:
        mapDetail = softDeleteMapFromS3(s3client, map_id)
        logging.info(f"Got map detail for {mapDetail.id}")
        return DeleteMapResponse(success=True, message=None, mapId=mapDetail.id)


def get_soft_delete_map_processor() -> SoftDeleteMapProcessor:
    logging.debug("In get_soft_delete_map_processor, returning new instance of DeleteMapProcessor")
    return SoftDeleteMapProcessor()
