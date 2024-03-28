import {KEPLERGL_S3_CLIENT_URL} from '../constants/default-settings'

export default class KeplerglS3Client {
  constructor() {
    this.url = KEPLERGL_S3_CLIENT_URL;
  }

  async uploadMap(
    mapDetail, datasets
  ) {
    const uploadMapUrl = `${this.url}/uploadMap`;

    var datasetDetails = [];

    const formdata = new FormData();

    formdata.append('mapDetail', JSON.stringify(mapDetail));

    for (const dataset of datasets) {
        datasetDetails.push({id: dataset.id, label: dataset.label});
        const fileData = new Blob([dataset.file], {type: 'text/csv'});
        formdata.append('datasets', fileData, 'data.csv');
        const colData = new Blob([JSON.stringify(dataset.columns)], {type: 'application/json'});
        formdata.append('datasetsColumns', colData, 'columns.json');
    }

    formdata.append('datasetDetails', JSON.stringify(datasetDetails));

    return fetch(
        uploadMapUrl,
        {
            method: 'POST',
            body: formdata,
        }
    ).then(
        response => response.json() // if the response is a JSON object
    ).then(
        success => success.mapDetail // Handle the success response object
    ).catch(error => {
        console.log(`KeplerglS3Client error in uploadMap: ${error.message}`); // Handle the error response object
        throw error;
    });
  }

  async listMaps() {
    const listMapsUrl = `${this.url}/listMaps`;
    return fetch(listMapsUrl).then(
        response => response.json() // if the response is a JSON object
    ).then(
        success => success.mapDetails // Handle the success response object
    ).catch(error => {
        console.log(`KeplerglS3Client error in listMaps: ${error.message}`); // Handle the error response object
        throw error;
    });
  }
  
  async downloadMapDetail(mapId) {
    const downloadMapDetailUrl = `${this.url}/downloadMapDetail/${mapId}/mapdetail.json`;
    return fetch(downloadMapDetailUrl).then(
        response => response.json() // if the response is a JSON object
    ).then(
        success => success.mapDetail // Handle the success response object
    ).catch(error => {
        console.log(`KeplerglS3Client error in downloadMapDetail: ${error.message}`); // Handle the error response object
        throw(error);
    });
  }
  
  async downloadMapDataset(mapId, datasetId) {
    const downloadMapDatasetUrl = `${this.url}/downloadMapDataset/${mapId}/${datasetId}/data.csv`;
    return fetch(downloadMapDatasetUrl).catch(error => {
        console.log(`KeplerglS3Client error in downloadMapDataset: ${error.message}`); // Handle the error response object
        throw(error);
    });
  }

  async downloadMap(mapId) { 
    return this.downloadMapDetail(mapId).then(
        mapDetail => Promise.all(mapDetail.datasetDetails.map(datasetDetail => {
            const {id: datasetId} = datasetDetail;
            return this.downloadMapDataset(mapId, datasetId).then(
                datasetResponse => datasetResponse.text()
            ).catch(error => {
                console.log(`KeplerglS3Client error downloading dataset for map ID ${mapId} with dataset ID ${datasetId}`);
                throw(error);
            });
        })).then(
            datasets => { return { mapDetail, datasets } ; }
        ).catch(error => {
                console.log(`KeplerglS3Client error downloading one of the datasets for map ID ${mapId}`);
                throw(error);
        })
    ).catch(error => {
        console.log(`KeplerglS3Client error downloading map for map ID ${mapId}: ${error.message}`); // Handle the error response object
        throw(error);
    })
  }
}
