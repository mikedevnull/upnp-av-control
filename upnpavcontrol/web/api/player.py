from fastapi import APIRouter, Request, HTTPException
import logging
from pydantic import BaseModel, validator
import urllib.parse
from .. import json_api
from ...core import playback

router = APIRouter()
_logger = logging.getLogger(__name__)


class RendererDevice(BaseModel):
    udn: str


def _format_device(device):
    return {'name': device.friendly_name, 'udn': device.udn}


class Volume(BaseModel):
    volume_percent: int

    @validator('volume_percent')
    def volume_percent_range(cls, v):  # pylint: disable=no-self-argument
        if v < 0 or v > 100:
            raise ValueError('Volume out of range (0 <= volume <= 100)')
        return v


@router.get('/devices')
def device_list(request: Request):
    return {'data': [_format_device(s) for s in request.app.av_control_point.mediarenderers]}


@router.put('/{udn}/volume', status_code=204)
async def set_player_volume(request: Request, udn: str, volume: Volume):
    try:
        udn = urllib.parse.unquote_plus(udn)
        renderer = request.app.av_control_point.get_mediarenderer_by_UDN(udn)
        await renderer.set_volume(volume.volume_percent)
    except Exception as e:
        _logger.exception(e)
        raise HTTPException(status_code=404)

    return ''


@router.get('/{udn}/volume', response_model=Volume)
async def get_player_volume(request: Request, udn: str):
    try:
        udn = urllib.parse.unquote_plus(udn)
        renderer = request.app.av_control_point.get_mediarenderer_by_UDN(udn)
        value = await renderer.get_volume()
        return Volume(volume_percent=value)
    except Exception as e:
        _logger.exception(e)
        raise HTTPException(status_code=404)


class PlaybackItem(BaseModel):
    dms: str
    object_id: str


PlaybackItemRequest = json_api.create_request_model('playlistitem', PlaybackItem)


@router.post('/{udn}/queue', status_code=201)
async def add_item_to_queue(request: Request, udn: str, payload: PlaybackItemRequest):
    try:
        udn = urllib.parse.unquote_plus(udn)
        playbackitem = payload.data.attributes
        renderer = request.app.av_control_point.get_mediarenderer_by_UDN(udn)
        server = request.app.av_control_point.get_mediaserver_by_UDN(playbackitem.dms)
        await playback.play(server, playbackitem.object_id, renderer)
    except Exception as e:
        _logger.exception(e)
        raise HTTPException(status_code=404)

    return ''
