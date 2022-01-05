from fastapi import APIRouter, Request, HTTPException
import logging
from .json_api_response import JsonApiResponse
from .library import split_library_item_id, create_library_item_id
from .. import models
from ...core import AVControlPoint
from ...core.mediarenderer import TransportState
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


@router.get('/{udn}/playback', response_model=models.PlaybackState)
async def get_playback_info(request: Request, udn: str):
    try:
        cp = control_point_from_request(request)
        renderer = cp.get_mediarenderer_by_UDN(udn)
        data = renderer.playback_info
        return data
    except Exception as e:
        _logger.exception(e)
        raise HTTPException(status_code=404)


@router.patch('/{udn}/playback', response_model_exclude_unset=True, response_model=models.PlaybackState)
async def change_player_playback_state(request: Request, udn: str, info: models.PlaybackStateIn):
    try:
        renderer = request.app.av_control_point.get_mediarenderer_by_UDN(udn)
        if info.volume_percent is not None:
            await renderer.set_volume(info.volume_percent)
        if info.transport is not None:
            controller = request.app.av_control_point.get_controller_for_renderer(udn)
            if info.transport == TransportState.PLAYING:
                await controller.play()
            if info.transport == TransportState.STOPPED:
                await controller.stop()
        info = renderer.playback_info
        return info
    except Exception as e:
        _logger.exception(e)
        raise HTTPException(status_code=404)


@router.get('/{udn}/queue', status_code=200, response_model=models.PlaybackQueue)
async def get_queued_items(request: Request, udn: str):
    try:
        pc = request.app.av_control_point.get_controller_for_renderer(udn)
        items = [{'library_item_id': create_library_item_id(x.dms, x.object_id)} for x in pc.queue.items]
        return {'items': items, 'current_item_index': pc.queue.current_item_index}
    except Exception as e:
        _logger.exception(e)
        raise HTTPException(status_code=404)


@router.post('/{udn}/queue', status_code=201)
async def append_items_to_queue(request: Request, udn: str, payload: models.PlaybackQueueIn):
    try:
        pc = request.app.av_control_point.get_controller_for_renderer(udn)
        for item in payload.items:
            dms, playbackitemid = split_library_item_id(item.library_item_id)
            pc.queue.append(dms, playbackitemid, '')

    except Exception as e:
        _logger.exception(e)
        raise HTTPException(status_code=404)


@router.put('/{udn}/queue', status_code=200)
async def set_queue_items(request: Request, udn: str, payload: models.PlaybackQueueIn):
    try:
        pc = request.app.av_control_point.get_controller_for_renderer(udn)
        pc.clear()
        for item in payload.items:
            dms, playbackitemid = split_library_item_id(item.library_item_id)
            pc.queue.append(dms, playbackitemid, '')

    except Exception as e:
        _logger.exception(e)
        raise HTTPException(status_code=404)
