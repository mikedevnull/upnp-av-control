import axios from 'axios'

const baseURL = '/api';

var upnpApi = axios.create({baseURL});

export default {
    getMediaRenderers() {
        const url = '/player/devices';
        return upnpApi
            .get(url)
            .then(response => response.data.data)
            .catch(error => console.log(error));
    },
    setActiveRenderer(udn) {
        const url = '/player/device';
        upnpApi
            .put(url, {udn: udn})
            .catch(error => console.log(error));
    },
    getCurrentPlaybackInfo() {
        const url = '/player';
        return upnpApi
            .get(url)
            .then(response => response.data)
            .catch(error => console.log(error));
    }
}