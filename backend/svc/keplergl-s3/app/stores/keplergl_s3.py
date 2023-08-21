# app/stores/keplergl_s3.py
from typing import List
from os import path
import logging
import boto3
from botocore.response import StreamingBody
from botocore.exceptions import ClientError
from io import BytesIO
from fastapi import UploadFile
from app.config import ENVIRONMENT, KEPLERGL_S3_BUCKET, KEPLERGL_S3_USER
from app.lib.logs import get_level_from_environment, setup_logging
from app.lib.utils.s3helpers import getKeysStartingWithPrefixToNextDelimiter
from app.lib.server.exceptions import NotFoundError, CloudResourceError
from app.dto.UploadMap import MapDetailResponse


setup_logging(get_level_from_environment(ENVIRONMENT), json_formatting=ENVIRONMENT != "testing")

def getPreviousMapVersions(s3client, mapId: str) -> List[int]:
    keyPrefix = f"userzone/{KEPLERGL_S3_USER}/{mapId}/archive/"
    mapVersionKeys = getKeysStartingWithPrefixToNextDelimiter(
        s3client, 
        KEPLERGL_S3_BUCKET, 
        keyPrefix, 
        4, 
        include_contents=False, 
        include_common_prefixes=True
    )
    mapVersions = list(map(int, mapVersionKeys))
    logging.debug(f"map versions: {mapVersions}")
    return mapVersions

def getNextMapVersion(s3client, mapId: str) -> int:
    mapVersions = getPreviousMapVersions(s3client, mapId)
    if len(mapVersions) > 0:
        return max(mapVersions) + 1
    else: 
        return 1

def moveS3Object(s3client, sourceKey: str, targetKey: str):
    try:
        s3client.copy(CopySource={"Bucket": KEPLERGL_S3_BUCKET, "Key": sourceKey}, Bucket=KEPLERGL_S3_BUCKET, Key=targetKey)
        s3client.delete_object(Bucket=KEPLERGL_S3_BUCKET, Key=sourceKey)
    except ClientError as error:
        clientErrorCode = error.response['Error']['Code']
        raise CloudResourceError(f"S3 Client Error {clientErrorCode}")

def moveCurrentMapToArchive(s3client, mapId: str) -> int:
    archiveVersion = getNextMapVersion(s3client, mapId)
    
    sourcePrefix = f"userzone/{KEPLERGL_S3_USER}/{mapId}/current/"
    targetPrefix = f"userzone/{KEPLERGL_S3_USER}/{mapId}/archive/{archiveVersion}/"

    # We get a list of the datasets directly from the S3 object store
    keylist = [f"userzone/{KEPLERGL_S3_USER}/{mapId}/current/mapdetail.json"]
    keyPrefix = f"userzone/{KEPLERGL_S3_USER}/{mapId}/current/datasets/"
    datasetIds = getKeysStartingWithPrefixToNextDelimiter(
        s3client, 
        KEPLERGL_S3_BUCKET, 
        keyPrefix, 
        5,
        include_contents=False,
        include_common_prefixes=True
    )
    for datasetId in datasetIds:
        keylist.append(f"{keyPrefix}{datasetId}/data.csv")
        keylist.append(f"{keyPrefix}{datasetId}/columns.json")

    for sourceKey in keylist:
        targetKey = path.join(targetPrefix, path.relpath(sourceKey, sourcePrefix))
        logging.debug(f"Moving {sourceKey} to {targetKey}")
        moveS3Object(s3client, sourceKey, targetKey)
    return archiveVersion

def uploadMapDetailToS3(s3client, mapId: str, mapDetail: MapDetailResponse):
    logging.info("Uploading map detail file to S3")
    try: 
        mdh = BytesIO(mapDetail.json().encode('utf-8'))
        s3client.upload_fileobj(
            mdh, 
            KEPLERGL_S3_BUCKET, 
            f"userzone/{KEPLERGL_S3_USER}/{mapId}/current/mapdetail.json"
        )
    except ClientError as error:
        clientErrorCode = error.response['Error']['Code']
        raise CloudResourceError(f"S3 Client Error {clientErrorCode}")

def uploadDatasetToS3(s3client, mapId: str, datasetId: str, dataset: UploadFile):
    try:
        logging.info(f"Uploading file {dataset.filename} to S3 with content type {dataset.content_type}")
        s3client.upload_fileobj(
            dataset.file, 
            KEPLERGL_S3_BUCKET, 
            f"userzone/{KEPLERGL_S3_USER}/{mapId}/current/datasets/{datasetId}/data.csv"
        )
    except ClientError as error:
        clientErrorCode = error.response['Error']['Code']
        raise CloudResourceError(f"S3 Client Error {clientErrorCode}")

def uploadColumnsJsonToS3(s3client, mapId: str, datasetId: str, columns: UploadFile):
    try:
        logging.info(f"Uploading file {columns.filename} to S3 with content type {columns.content_type}")
        s3client.upload_fileobj(
            columns.file, 
            KEPLERGL_S3_BUCKET, 
            f"userzone/{KEPLERGL_S3_USER}/{mapId}/current/datasets/{datasetId}/columns.json"
        )
    except ClientError as error:
        clientErrorCode = error.response['Error']['Code']
        raise CloudResourceError(f"S3 Client Error {clientErrorCode}")

def getMapDetailFromS3(s3client, mapId: str) -> MapDetailResponse:
    try:
        mdh = BytesIO()
        s3client.download_fileobj(
            KEPLERGL_S3_BUCKET,
            f"userzone/{KEPLERGL_S3_USER}/{mapId}/current/mapdetail.json",
            mdh
        )
        return MapDetailResponse.parse_raw(mdh.getvalue().decode(encoding='utf-8'))
    except ClientError as error:
        clientErrorCode = error.response['Error']['Code']
        if clientErrorCode == 'NoSuchKey':
            raise NotFoundError(f"S3 No Such Key Error")
        else:
            raise CloudResourceError(f"S3 Client Error {clientErrorCode}")
    
def getMapDetailsListFromS3(s3client) -> List[MapDetailResponse]:
    try:
        keyPrefix = f"userzone/{KEPLERGL_S3_USER}/"
        mapIds = getKeysStartingWithPrefixToNextDelimiter(
            s3client,
            KEPLERGL_S3_BUCKET,
            keyPrefix, 
            2, 
            include_contents=False, 
            include_common_prefixes=True
        )

        mapDetails = []

        for mapId in mapIds:
            mapDetail = getMapDetailFromS3(s3client, mapId)
            mapDetails.append(mapDetail)
        
        return mapDetails
    except ClientError as error:
        clientErrorCode = error.response['Error']['Code']
        # We anticipate 'NoSuchKey' will not occur here, so we 
        # raise a CloudResourceError
        raise CloudResourceError(f"S3 Client Error {clientErrorCode}")

def getDatasetFromS3(s3client, mapId: str, datasetId: str) -> StreamingBody:
    try:
        result = s3client.get_object(
            Bucket=KEPLERGL_S3_BUCKET, 
            Key=f"userzone/{KEPLERGL_S3_USER}/{mapId}/current/datasets/{datasetId}/data.csv"
        )
        return result["Body"]
    except ClientError as error:
        clientErrorCode = error.response['Error']['Code']
        if clientErrorCode == 'NoSuchKey':
            raise NotFoundError(f"S3 No Such Key Error")
        else:
            raise CloudResourceError(f"S3 Client Error {clientErrorCode}")

def getColumnsFromS3(s3client, mapId: str, datasetId: str) -> StreamingBody:
    try:
        result = s3client.get_object(
            Bucket=KEPLERGL_S3_BUCKET, 
            Key=f"userzone/{KEPLERGL_S3_USER}/{mapId}/current/datasets/{datasetId}/columns.json"
        )
        return result["Body"]
    except ClientError as error:
        clientErrorCode = error.response['Error']['Code']
        if clientErrorCode == 'NoSuchKey':
            raise NotFoundError(f"S3 No Such Key Error")
        else:
            raise CloudResourceError(f"S3 Client Error {clientErrorCode}")

def deleteS3Object(s3client, s3key: str):
    try:
        s3client.delete_object(Bucket=KEPLERGL_S3_BUCKET, Key=s3key)
    except ClientError as error:
        clientErrorCode = error.response['Error']['Code']
        raise CloudResourceError(f"S3 Client Error {clientErrorCode}")

def softDeleteMapFromS3(s3client, mapId: str) -> MapDetailResponse:
    # retrieve current map detail
    mapDetail = getMapDetailFromS3(s3client, mapId)
    # set inactive
    mapDetail.active = False
    # delete current map detail
    deleteS3Object(
        s3client,
        f"userzone/{KEPLERGL_S3_USER}/{mapId}/current/mapdetail.json"
    )
    # upload updated map detail
    uploadMapDetailToS3(s3client, mapId, mapDetail)
    return mapDetail

