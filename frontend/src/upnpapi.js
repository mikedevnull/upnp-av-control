import axios from "axios";

const baseURL = "/api";

export const upnpApi = axios.create({
  baseURL
});

function convertDeviceEntry(deviceEntryFromApi) {
  return {
    friendlyName: deviceEntryFromApi.friendly_name,
    udn: deviceEntryFromApi.udn
  };
}

export default {
  getMediaRenderers() {
    const url = "/player/devices";
    return upnpApi
      .get(url)
      .then(response => response.data.data)
      .then(devices => devices.map(convertDeviceEntry));
  },
  getLibraryDevices() {
    const url = "/library/devices";
    return upnpApi
      .get(url)
      .then(response => response.data)
      .then(devices => devices.map(convertDeviceEntry));
  },
  setCurrentVolume(udn, volumePercent) {
    const url = `/player/${udn}/volume`;
    return upnpApi.put(url, {
      // eslint-disable-next-line @typescript-eslint/camelcase
      volume_percent: volumePercent
    });
  },
  getCurrentPlaybackInfo() {
    const url = "/player";
    return upnpApi.get(url).then(response => response.data);
  },
  browseServer(udn, objectID) {
    const url = `/library/${udn}/browse`;
    let params = {};
    if (objectID !== undefined) {
      params = { objectID: objectID };
    }

    return upnpApi.get(url, { params }).then(response => response.data);
  },
  getObjectMetadata(udn, objectID) {
    const url = `/library/${udn}/metadata`;
    let params = {};
    if (objectID !== undefined) {
      params = { objectID: objectID };
    }

    return upnpApi.get(url, { params }).then(response => response.data);
  }
};
