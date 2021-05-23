from fastapi import APIRouter, Request, HTTPException
import logging
from pydantic import BaseModel
import urllib.parse
from .json_api_response import JsonApiResponse
from .. import json_api, models
from ...core import playback, mediarenderer
from ...core.typing_compat import Literal

router = APIRouter(default_response_class=JsonApiResponse)
_logger = logging.getLogger(__name__)

DevicesResponse = json_api.create_list_response_model('mediarenderer', id_field='udn', PayloadModel=models.DeviceModel)
DeviceResponse = json_api.create_response_model('mediarenderer', models.DeviceModel)


@router.get('/', response_model=DevicesResponse, response_model_exclude_unset=True)
def player_device_list(request: Request):
    def create_links(d: models.DeviceModel):
        return {'self': request.url_for('player_device', udn=d.udn)}

    resp = DevicesResponse.create(request.app.av_control_point.mediarenderers, links_factory=create_links)
    return resp


@router.get('/{udn}', response_model=DeviceResponse, response_model_exclude_unset=True)
def player_device(request: Request, udn: str):
    device = request.app.av_control_point.get_mediarenderer_by_UDN(udn)
    relationships = {
        'queue': {
            'links': {
                'related': request.url_for('add_item_to_queue', udn=udn)
            }
        },
        'playbackinfo': {
            'links': {
                'related': request.url_for('get_playback_info', udn=udn)
            }
        }
    }
    return DeviceResponse.create(device.udn, device, request.url_for('player_device', udn=udn), relationships)


PlaybackInfoResponse = json_api.create_response_model('playbackinfo', mediarenderer.PlaybackInfo)
PlaybackInfoPatchRequest = json_api.create_request_patch_model(Literal['playbackinfo'], mediarenderer.PlaybackInfo)


@router.get('/{udn}/playback', response_model=PlaybackInfoResponse, response_model_exclude_unset=True)
async def get_playback_info(request: Request, udn: str):
    try:
        udn = urllib.parse.unquote_plus(udn)
        renderer = request.app.av_control_point.get_mediarenderer_by_UDN(udn)
        info = renderer.playback_info
        response = PlaybackInfoResponse.create(udn, info, request.url_for('get_playback_info', udn=udn))
        return response
    except Exception as e:
        _logger.exception(e)
        raise HTTPException(status_code=404)


@router.patch('/{udn}/playback', response_model_exclude_unset=True, response_model=PlaybackInfoResponse)
async def patch_playback_info(request: Request, udn: str, info: PlaybackInfoPatchRequest):
    try:
        udn = urllib.parse.unquote_plus(udn)
        renderer = request.app.av_control_point.get_mediarenderer_by_UDN(udn)
        if info.data.attributes.volume_percent is not None:
            await renderer.set_volume(info.data.attributes.volume_percent)
        info = renderer.playback_info
        return PlaybackInfoResponse.create(udn, info, request.url_for('get_playback_info', udn=udn))
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
