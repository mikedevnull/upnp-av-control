from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, validator
import logging
from upnpavcontrol.core.discover import is_media_server
import urllib.parse


class AVControlPointAPI(FastAPI):
    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self._av_control_point = None

    @property
    def av_control_point(self):
        return self._av_control_point

    @av_control_point.setter
    def av_control_point(self, control_point):
        self._av_control_point = control_point


app = AVControlPointAPI()


class RendererDevice(BaseModel):
    udn: str


class PlaybackInfo(BaseModel):
    player: str = None
    volume: int = None


def _format_device(device):
    return {'name': device.upnp_device.friendly_name, 'udn': device.udn}


def _format_server(device):
    return {'name': device.friendly_name, 'udn': device.udn,
            'links': {'browse': _format_browse_url(device.udn)}
            }


def _format_browse_url(udn: str, objectId: str = None):
    browseUrl = app.url_path_for('browse_library', udn=udn)
    if objectId is not None:
        query = urllib.parse.urlencode({'objectID': objectId})
        browseUrl = browseUrl + '?' + query
    return browseUrl


def _format_didl_entry(udn: str, entry):
    data = {values[1]: getattr(entry, values[1])
            for values in entry.didl_properties_defs if
            hasattr(entry, values[1])}
    data['tag'] = entry.tag
    if entry.tag == 'container':
        data['browseChildren'] = _format_browse_url(udn, entry.id)
    return data


def _format_didl_entries(udn, entries):
    return [_format_didl_entry(udn, x) for x in entries]


@app.get('/player/devices')
def device_list():
    return {'data': [_format_device(s)
                     for s in app.av_control_point.mediarenderers]}


@app.put('/player/device')
def set_active_player(device: RendererDevice):
    try:
        logging.info('Select device: %s', device.udn)
        app.av_control_point.set_renderer(device.udn)
    except KeyError as e:
        raise HTTPException(status_code=400, detail=str(e))


class Volume(BaseModel):
    volume_percent: int

    @validator('volume_percent')
    def volume_percent_range(cls, v):
        if v < 0 or v > 100:
            raise ValueError('Volume out of range (0 <= volume <= 100)')
        return v


@app.put('/player/volume', status_code=204)
async def set_player_volume(volume: Volume):
    if app.av_control_point.mediarenderer is None:
        raise HTTPException(status_code=404)
    await app.av_control_point.mediarenderer.set_volume(volume.volume_percent)
    return ''


@app.get('/player', response_model=PlaybackInfo)
async def current_playback_info():
    if app.av_control_point.mediarenderer is None:
        return {'player': None}
    else:
        volume = await app.av_control_point.mediarenderer.get_volume()
        return {'player': app.av_control_point.mediarenderer.udn,
                'volume': volume}


@app.get('/library/devices')
def get_media_library_devices():
    return {'data': [_format_server(x)
                     for x in app.av_control_point.mediaservers]}


@app.get('/library/browse/{udn}')
async def browse_library(udn: str, objectID: str = '0'):
    if udn not in app.av_control_point.devices or not \
            is_media_server(app._av_control_point.devices[udn].device_type):
        raise HTTPException(status_code=404)
    server = app.av_control_point.devices[udn].device
    result = await server.browse(objectID)
    return _format_didl_entries(udn, result)
