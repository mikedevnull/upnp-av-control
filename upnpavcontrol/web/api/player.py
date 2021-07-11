from fastapi import APIRouter, Request, HTTPException
import logging
from .json_api_response import JsonApiResponse
from .library import split_library_item_id
from .. import models
from ...core import playback, AVControlPoint
from typing import List

router = APIRouter(default_response_class=JsonApiResponse)
_logger = logging.getLogger(__name__)


def control_point_from_request(request) -> AVControlPoint:
    return request.app.av_control_point


@router.get('/', response_model=List[models.PlayerDevice], response_model_exclude_unset=True)
def player_device_list(request: Request):
    return [models.PlayerDevice.from_orm(d) for d in request.app.av_control_point.mediarenderers]


@router.get('/{udn}', response_model=models.PlayerDevice, response_model_exclude_unset=True)
def player_device(request: Request, udn: str):
    device = request.app.av_control_point.get_mediarenderer_by_UDN(udn)
    return models.PlayerDevice.from_orm(device)


@router.get('/{udn}/playback', response_model=models.PlaybackState, response_model_exclude_unset=True)
async def get_playback_info(request: Request, udn: str):
    try:
        renderer = control_point_from_request(request).get_mediarenderer_by_UDN(udn)
        return renderer.playback_info
    except Exception as e:
        _logger.exception(e)
        raise HTTPException(status_code=404)


@router.patch('/{udn}/playback', response_model_exclude_unset=True, response_model=models.PlaybackState)
async def patch_playback_info(request: Request, udn: str, info: models.PlaybackState):
    try:
        renderer = request.app.av_control_point.get_mediarenderer_by_UDN(udn)
        if info.volume_percent is not None:
            await renderer.set_volume(info.volume_percent)
        info = renderer.playback_info
        return info
    except Exception as e:
        _logger.exception(e)
        raise HTTPException(status_code=404)


# PlaybackItemRequest = json_api.create_request_model('playlistitem', PlaybackItem)


@router.post('/{udn}/queue', status_code=201)
async def add_item_to_queue(request: Request, udn: str, payload: models.PlaybackQueueItem):
    try:
        dms, playbackitemid = split_library_item_id(payload.library_item_id)
        renderer = request.app.av_control_point.get_mediarenderer_by_UDN(udn)
        server = request.app.av_control_point.get_mediaserver_by_UDN(dms)
        await playback.play(server, playbackitemid, renderer)
    except Exception as e:
        _logger.exception(e)
        raise HTTPException(status_code=404)
