from .media_proxy import get_media_proxy_url
from ...core.mediaserver import BrowseFlags
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from typing import List
import urllib.parse
import logging
import asyncio

router = APIRouter()
_logger = logging.getLogger(__name__)


class MediaServer(BaseModel):
    friendly_name: str
    udn: str

    class Config:
        orm_mode = True


def _fixup_media_server(x):
    x.udn = urllib.parse.quote_plus(x.udn)
    return x


def _fixup_didl_item(item):
    item.id = urllib.parse.quote_plus(item.id)
    item.parentID = urllib.parse.quote_plus(item.parentID)
    albumArtURI = getattr(item, 'albumArtURI', None)
    if albumArtURI is not None:
        item.albumArtURI = get_media_proxy_url(albumArtURI)
    artistDiscographyURI = getattr(item, 'artistDiscographyURI', None)
    if artistDiscographyURI is not None:
        item.artistDiscographyURI = get_media_proxy_url(artistDiscographyURI)
    return item


def _fixup_didl_items(items):
    return (_fixup_didl_item(x) for x in items)


@router.get('/devices', response_model=List[MediaServer])
def get_media_library_devices(request: Request):
    return [_fixup_media_server(MediaServer.from_orm(x)) for x in request.app.av_control_point.mediaservers]


@router.get('/{udn}/browse')
async def browse_library(request: Request, udn: str, objectID: str = '0'):
    try:
        udn = urllib.parse.unquote_plus(udn)
        objectID = urllib.parse.unquote_plus(objectID)
        server = request.app.av_control_point.getMediaServerByUDN(udn)
        result = await server.browse(objectID)
        return _fixup_didl_items(result)
    except asyncio.TimeoutError:
        _logger.error('Mediaserver browse request timed out')
        raise HTTPException(status_code=504, detail="Request to mediaserver timed out")
    except Exception as e:
        _logger.exception(e)
        raise HTTPException(status_code=404)


@router.get('/{udn}/metadata')
async def get_object_metadata(request: Request, udn: str, objectID: str = '0'):
    try:
        udn = urllib.parse.unquote_plus(udn)
        objectID = urllib.parse.unquote_plus(objectID)
        server = request.app.av_control_point.getMediaServerByUDN(udn)
        result = await server.browse(objectID, browse_flag=BrowseFlags.BrowseMetadata)
        return _fixup_didl_items(result)
    except asyncio.TimeoutError:
        _logger.error('Mediaserver metadata request timed out')
        raise HTTPException(status_code=504, detail="Request to mediaserver timed out")
    except Exception as e:
        _logger.exception(e)
        raise HTTPException(status_code=404)
