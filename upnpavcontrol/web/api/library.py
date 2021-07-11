from .media_proxy import get_media_proxy_url
from ...core.mediaserver import BrowseFlags
from fastapi import APIRouter, Request, HTTPException
import urllib.parse
import logging
import asyncio
from .. import models
import typing

router = APIRouter()
_logger = logging.getLogger(__name__)


def create_library_item_id(udn: str, objectID: typing.Optional[str] = None):
    assert '.' not in udn
    if objectID is not None:
        # extra escaping of '/' in objectID required due to
        # https://github.com/encode/starlette/issues/826
        # and https://github.com/tiangolo/fastapi/issues/791
        return urllib.parse.quote_plus(udn) + '.' + urllib.parse.quote_plus(objectID.replace('/', '%2F'))
    else:
        return urllib.parse.quote_plus(udn)


def split_library_item_id(id: str):
    parts = id.split('.', 1)
    if len(parts) == 1:
        return urllib.parse.unquote_plus(parts[0]), None
    else:
        udn = urllib.parse.unquote_plus(parts[0])
        # extra escaping of '/' in objectID required due to
        # https://github.com/encode/starlette/issues/826
        # and https://github.com/tiangolo/fastapi/issues/791
        objectID = urllib.parse.unquote_plus(parts[1]).replace('%2F', '/')
        return udn, objectID


def _fixup_item_media_urls(item):
    albumArtURI = getattr(item, 'albumArtURI', None)
    if albumArtURI is not None:
        item.albumArtURI = get_media_proxy_url(albumArtURI.uri)
    artistDiscographyURI = getattr(item, 'artistDiscographyURI', None)
    if artistDiscographyURI is not None:
        item.artistDiscographyURI = get_media_proxy_url(artistDiscographyURI.uri)
    return item


def _fixup_item_ids(item, udn):
    item.id = create_library_item_id(udn, item.id)
    if item.parentID == '-1':
        item.parentID = None
    else:
        item.parentID = create_library_item_id(udn, item.parentID)
    return item


def _map_item_class(itemclass: str):
    if itemclass.startswith('object.container'):
        return models.LibraryItemType.CONTAINER
    else:
        return models.LibraryItemType.ITEM


def format_library_item(item, udn: str):
    item = _fixup_item_media_urls(item)
    item = _fixup_item_ids(item, udn)
    return {'title': item.title, 'id': item.id, 'parentID': item.parentID, 'upnpclass': _map_item_class(item.upnpclass)}


@router.get('/', response_model=typing.List[models.LibraryListItem])
def get_library_collections(request: Request):
    items = [{
        'title': x.friendly_name,
        'id': create_library_item_id(x.udn),
        'upnpclass': models.LibraryItemType.CONTAINER
    } for x in request.app.av_control_point.mediaservers]
    return items


@router.get('/{id}/metadata', response_model=models.LibraryItemMetadata)
async def get_library_item(request: Request, id: str):
    try:
        udn, objectID = split_library_item_id(id)
        if objectID is None:
            objectID = '0'
        device = request.app.av_control_point.get_mediaserver_by_UDN(udn)
        result = await device.browse(objectID, browse_flag=BrowseFlags.BrowseMetadata)
        payload = models.LibraryItemMetadata.from_orm(_fixup_item_ids(_fixup_item_media_urls(result.objects[0]), udn))
        return payload
    except Exception as e:
        _logger.exception(e)
        raise HTTPException(status_code=404)


@router.get('/{id}')
async def browse_library(request: Request, id: str, page: int = 0, pagesize: int = 0):
    try:
        # id = urllib.parse.unquote_plus(id)
        udn, objectID = split_library_item_id(id)
        if objectID is None:
            objectID = '0'
        device = request.app.av_control_point.get_mediaserver_by_UDN(udn)
        result = await device.browse(objectID, starting_index=page * pagesize, requested_count=pagesize)

        payload = [format_library_item(x, udn) for x in result.objects]
        return payload
    except asyncio.TimeoutError:
        _logger.error('Mediaserver browse request timed out')
        raise HTTPException(status_code=504, detail="Request to mediaserver timed out")
    except Exception as e:
        _logger.exception(e)
        raise HTTPException(status_code=404)
