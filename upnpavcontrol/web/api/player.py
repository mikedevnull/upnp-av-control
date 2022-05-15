from fastapi import APIRouter, Request, HTTPException
import logging
from .json_api_response import JsonApiResponse
from .library import split_library_item_id, create_library_item_id, get_item_artwork_url
from .. import models
from ...core import AVControlPoint
from ...core.mediarenderer import TransportState
from ...core.playback.queue import PlaybackItem
from typing import List

router = APIRouter(default_response_class=JsonApiResponse)
_logger = logging.getLogger(__name__)


async def _resolve_queue_item(cp: AVControlPoint, item: models.PlaybackQueueItem):
    dms_udn, object_id = split_library_item_id(item.id)
    dms = cp.get_mediaserver_by_UDN(dms_udn)
    didl = await dms.browse_metadata(object_id)
    meta = didl.objects[0]
    img = get_item_artwork_url(meta)
    return PlaybackItem(dms_udn,
                        object_id,
                        meta.title,
                        album=getattr(meta, 'album', None),
                        artist=getattr(meta, 'artist', None),
                        image=img)


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
        items = [{
            'id': create_library_item_id(x.dms, x.object_id),
            'title': x.title,
            'album': x.album,
            'artist': x.artist,
            'image': x.image
        } for x in pc.queue.items]
        return {'items': items, 'current_item_index': pc.queue.current_item_index}
    except Exception as e:
        _logger.exception(e)
        raise HTTPException(status_code=404)


@router.post('/{udn}/queue', status_code=201)
async def append_items_to_queue(request: Request, udn: str, payload: models.PlaybackQueueIn):
    try:
        pc = request.app.av_control_point.get_controller_for_renderer(udn)
        if payload.items is not None:
            items = [await _resolve_queue_item(request.app.av_control_point, i) for i in payload.items]
            for item in items:
                pc.queue.appendItem(item)
        if payload.current_item_index is not None:
            await pc.set_current_item(payload.current_item_index)

    except Exception as e:
        _logger.exception(e)
        raise HTTPException(status_code=404)


@router.put('/{udn}/queue', status_code=200)
async def set_queue_items(request: Request, udn: str, payload: models.PlaybackQueue):
    try:
        pc = request.app.av_control_point.get_controller_for_renderer(udn)
        items = [await _resolve_queue_item(request.app.av_control_point, i) for i in payload.items]
        pc.clear()
        for item in items:
            pc.queue.appendItem(item)
        if payload.current_item_index:
            await pc.set_current_item(payload.current_item_index)

    except Exception as e:
        _logger.exception(e)
        raise HTTPException(status_code=404)
