import Console from 'global/console';
import KeplerglS3Icon from './keplergl-s3-icon';
import {formatCsv} from 'kepler.gl/processors';
import {Provider} from 'kepler.gl/cloud-providers';
import {createDataContainer} from 'kepler.gl/dist/utils/index';
import KeplerglS3Client from '../../service/keplergl-s3';

const NAME = 'keplergl-s3';
const DISPLAY_NAME = 'S3 Provider';
const THUMBNAIL = {width: 300, height: 200};
const ICON = KeplerglS3Icon;
export const FILE_CONFLICT_MSG = 'file_conflict';
/**
 * The default provider class
 * @param {object} props
 * @param {string} props.name
 * @param {string} props.displayName
 * @param {React.Component} props.icon - React element
 * @param {object} props.thumbnail - thumbnail size object
 * @param {number} props.thumbnail.width - thumbnail width in pixels
 * @param {number} props.thumbnail.height - thumbnail height in pixels
 * @public
 * @example
 *
 * const myProvider = new Provider({
 *  name: 'foo',
 *  displayName: 'Foo Storage'
 *  icon: Icon,
 *  thumbnail: {width: 300, height: 200}
 * })
 */
export default class S3Provider extends Provider {
  constructor(s3bucket) {
    super({name: NAME, displayName: DISPLAY_NAME, icon: ICON, thumbnail: THUMBNAIL});
    this.s3bucket = s3bucket;
    this.s3client = new KeplerglS3Client();
  }

  /**
   * Whether this provider support upload map to a private storage. If truthy, user will be displayed with the storage save icon on the top right of the side bar.
   * @returns
   * @public
   */
  hasPrivateStorage() {
    return true;
  }

  /**
   * Whether this provider support share map via a public url, if truthy, user will be displayed with a share map via url under the export map option on the top right of the side bar
   * @returns
   * @public
   */
  hasSharingUrl() {
    return true;
  }

  /**
   * This method is called after user share a map, to display the share url.
   * @param fullUrl - Whether to return the full url with domain, or just the location
   * @returns shareUrl
   * @public
   */
  getShareUrl(fullUrl = false) {
    return this.getMapUrl(fullUrl);
  }

  /**
   * This method is called by kepler.gl demo app to pushes a new location to history, becoming the current location.
   * @param fullURL - Whether to return the full url with domain, or just the location
   * @returns mapUrl
   * @public
   */
  getMapUrl(fullUrl = true, mapParams = null) {
    if (mapParams) {
      return this._getMapPermalinkFromParams(mapParams, fullUrl);
    } else if (this.currentMap) {
      return this._getMapPermalinkFromParams(
        {
          mapId: this.currentMap.id,
          owner: this.getUserName(),
          privateMap: this.currentMap.privateMap
        },
        fullUrl
      );
    }
  }

  /**
   * This method is called to determine whether user already logged in to this provider
   * @public
   * @returns true if a user already logged in
   */
  getAccessToken() {
    return true;
  }

  /**
   * This method is called to get the user name of the current user. It will be displayed in the cloud provider tile.
   * @public
   * @returns true if a user already logged in
   */
  getUserName() {
    return 'keplergl-s3-user';
  }

  /**
   * This return a standard error that will trigger the overwrite map modal
   */
  getFileConflictError() {
    return new Error(FILE_CONFLICT_MSG);
  }

  /**
   * This method will be called when user click the login button in the cloud provider tile.
   * Upon login success, `onCloudLoginSuccess` has to be called to notify kepler.gl UI
   * @param {function} onCloudLoginSuccess - callbacks to be called after login success
   * @public
   */
  async login(onCloudLoginSuccess) {
    onCloudLoginSuccess();
    return;
  }

  /**
   * This method will be called when user click the logout button under the cloud provider tile.
   * Upon login success, `onCloudLoginSuccess` has to be called to notify kepler.gl UI
   * @param {function} onCloudLogoutSuccess - callbacks to be called after logout success
   * @public
   */
  async logout(onCloudLogoutSuccess) {
    onCloudLogoutSuccess();
    return;
  }

  /**
   * This method will be called to upload map for saving and sharing. Kepler.gl will package map data, config, title, description and thumbnail for upload to storage.
   * With the option to overwrite already saved map, and upload as private or public map.
   *
   * @param {Object} param
   * @param {Object} param.mapData - the map object
   * @param {Object} param.mapData.map - {datasets. config, info: {title, description}}
   * @param {Blob} param.mapData.thumbnail - A thumbnail of current map. thumbnail size can be defined by provider by this.thumbnail
   * @param {object} [param.options]
   * @param {boolean} [param.options.overwrite] - whether user choose to overwrite already saved map under the same name
   * @param {boolean} [param.options.isPublic] - whether user wish to share the map with others. if isPublic is truthy, kepler will call this.getShareUrl() to display an URL they can share with others
   * @public
   */
  async uploadMap({
    mapData,
    options = {}
  }
  ) {
    // We follow the approach for carto
    try {
      const {isPublic = true, overwrite = true} = options;
      const {map: {config, datasets, info} = {}, thumbnail} = mapData;

      const s3Datasets = datasets.map(this._convertDataset);

      const {title, description} = info;
      const name = title;

      const thumbnailBase64 =
        mapData && thumbnail ? await this._blobToBase64(mapData.thumbnail) : null;

      let result;
      if (overwrite) {
        result = await this.s3client.uploadMap(
          {
            id: this.currentMap.id,
            name,
            description,
            thumbnail: thumbnailBase64,
            config: config,
            privateMap: this.currentMap.privateMap ? this.currentMap.privateMap : !isPublic
          },
          s3Datasets
        );
      } else {
        // Check public name generation and replace
        const regex = /(?:^keplergl_)([a-z0-9]+)(?:.json$)/;
        const capturedName = name.match(regex);
        const visName = capturedName ? `sharedmap_${capturedName[1]}` : name;

        result = await this.s3client.uploadMap(
          {
            name: visName,
            description,
            thumbnail: thumbnailBase64,
            config: config,
            privateMap: !isPublic
          },
          s3Datasets
        );
      }

      if (result) {
        this.currentMap = result;
      }

      return {
        shareUrl: this._getMapPermalinkFromParams(
          {
            mapId: result.id,
            owner: this.getUserName(),
            privateMap: !isPublic
          },
          true
        ),
        folderLink: this._getFolderLinkFromParams(
          {
            mapId: result.id,
            owner: this.getUserName(),
            privateMap: !isPublic
          }
        )
      };
    } catch (error) {
      this._manageErrors(error);
    }
  }

  /**
   * This method is called to get a list of maps saved by the current logged in user.
   * @returns visualizations an array of Viz objects
   * @public
   * @example
   *  async listMaps() {
   *    return [
   *      {
   *        id: 'a',
   *        title: 'My map',
   *        description: 'My first kepler map',
   *        imageUrl: 'http://',
   *        lastModification: 1582677787000,
   *        privateMap: false,
   *        loadParams: {}
   *      }
   *    ];
   *  }
   */
  async listMaps() {
    try {
      const username = this.getUserName();

      const visualizations = await this.s3client.listMaps();
      
      let formattedVis = [];

      // Format visualization object
      for (const vis of visualizations) {
        formattedVis.push({
          ...vis,
          lastModification: new Date(Date.parse(vis.lastModification)),
          loadParams: {
            owner: username,
            mapId: vis.id,
            privateMap: vis.privateMap.toString()
          }
        });
      }

      formattedVis = formattedVis.sort((a, b) => b.lastModification - a.lastModification);

      return formattedVis;
    } catch (error) {
      this._manageErrors(error);
    }
  }

  /**
   * @typedef {Object} Viz
   * @property {string} id - An unique id
   * @property {string} title - The title of the map
   * @property {string} description - The description of the map
   * @property {string} imageUrl - The imageUrl of the map
   * @property {number} lastModification - An epoch timestamp in milliseconds
   * @property {boolean} privateMap - Optional, whether if this map is private to the user, or can be accessed by others via URL
   * @property {*} loadParams - A property to be passed to `downloadMap`
   * @public
   */

  /**
   * This method will be called when user select a map to load from the storage map viewer
   * @param {*} loadParams - the loadParams property of each visualization object
   * @returns mapResponse - the map object containing dataset config info and format option
   * @public
   * @example
   * async downloadMap(loadParams) {
   *  const mockResponse = {
   *    map: {
   *      datasets: [],
   *      config: {},
   *      info: {
   *        app: 'kepler.gl',
   *        created_at: ''
   *        title: 'test map',
   *        description: 'Hello this is my test dropbox map'
   *      }
   *    },
   *    // pass csv here if your provider currently only support save / load file as csv
   *    format: 'keplergl'
   *  };
   *
   *  return downloadMap;
   * }
   */
  async downloadMap(queryParams) {
    try {
      const {owner: username, mapId, privateMap} = queryParams;

      if (!username || !mapId) {
        return;
      }

      let visualization;

      if (privateMap.trim().toLowerCase() === 'true') {
        const currentUsername = this.getUserName();
        if (currentUsername && currentUsername === username) {
          visualization = await this.s3client.downloadMap(mapId);
        }
      } else {
        visualization = await this.s3client.downloadMap(mapId);
      }

      if (!visualization) {
        throw new Error(`Can't find map with ID: ${mapId}`);
      }

      // These are the options required for the action.
      // For now, all datasets that come from the kepler.gl S3 service are CSV
      const datasets = visualization.datasets.map((dataset, i)=> {
        const {id: datasetId, label: datasetLabel} = visualization.mapDetail.datasetDetails[i];

        return {
          info: {
            id: datasetId,
            label: datasetLabel,
            panelDisabled: true
          },
          data: dataset
        };
      });

      this.currentMap = visualization.mapDetail;

      return {
        map: {
          datasets,
          config: visualization.mapDetail.config,
          info: {
            title: visualization.mapDetail.name, 
            description: visualization.mapDetail.description
          },
        },
        format: 'csv'
      };
    } catch (error) {
      this._manageErrors(error);
    }
  }

  /**
   * The returned object of `downloadMap`. The response object should contain: datasets: [], config: {}, and info: {}
   * each dataset object should be {info: {id, label}, data: {...}}
   * to inform how kepler should process your data object, pass in `format`
   * @typedef {Object} MapResponse
   * @property {Object} map
   * @property {Array<Object>} map.datasets
   * @property {Object} map.config
   * @property {Object} map.info
   * @property {string} format - one of 'csv': csv file string, 'geojson': geojson object, 'row': row object, 'keplergl': datasets array saved using KeplerGlSchema.save
   * @public
   */
  
  _composeURL({mapId, owner, privateMap}) {
    return `demo/map/keplergl-s3?mapId=${mapId}&owner=${owner}&privateMap=${privateMap}`;
  }

  _getMapPermalinkFromParams({mapId, owner, privateMap}, fullURL = true) {
    const mapLink = this._composeURL({mapId, owner, privateMap});
    return fullURL
      ? `${window.location.protocol}//${window.location.host}/${mapLink}`
      : `/${mapLink}`;
  }
  
  _getFolderLinkFromParams({mapId, owner}) {
    return `s3://${this.s3bucket}/userzone/${owner}/${mapId}/current`;
  }

  _convertDataset({data: dataset}) {
    const {allData, fields, id, label} = dataset;
    // NOTE (JS): Not sure of the exact interface for a "field", but am 
    //            copying all the keys known at this time for "column".
    const columns = fields.map(field => ({
      name: field.name,
      type: field.type,
      format: field.format,
      analyzerType: field.analyzerType
    }));

    const dataContainer = createDataContainer([...allData]);

    const file = formatCsv(dataContainer, fields);

    return {
      id,
      label,
      columns,
      file
    };
  }
  
  // eslint-disable-next-line complexity
  _manageErrors(error, throwException = true) {
    let message;
    if (error && error.message) {
      message = error.message;

      switch (error.message) {
        default:
          Console.error(`kepler.gl S3 provider: ${message}`);
      }
    } else {
      message = 'General error in kepler.gl S3 provider';
      Console.error(message);
    }

    if (throwException) {
      throw new Error(message);
    }
  }
  
  _blobToBase64(blob) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onloadend = () => {
        if (!reader.error) {
          resolve(reader.result);
        } else {
          reject(reader.error);
        }
      };
      reader.readAsDataURL(blob);
    });
  }
}

