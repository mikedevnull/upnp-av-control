from .media_proxy import get_media_proxy_url
from ...core.mediaserver import BrowseFlags
from fastapi import APIRouter, Request, HTTPException
import urllib.parse
import logging
import asyncio
from .. import models
from .. import json_api

router = APIRouter()
_logger = logging.getLogger(__name__)

DevicesResponse = json_api.create_list_response_model('mediaserver', id_field='udn', PayloadModel=models.DeviceModel)
DeviceResponse = json_api.create_response_model('mediaserver', models.DeviceModel)

MetadataResponse = json_api.create_response_model('itemmetadata', models.LibraryItemMetadata)
LibraryListingResponse = json_api.create_list_response_model('itemlist',
                                                             id_field='id',
                                                             PayloadModel=models.LibraryListItem)


def _fixup_item_media_urls(item):
    albumArtURI = getattr(item, 'albumArtURI', None)
    if albumArtURI is not None:
        item.albumArtURI = get_media_proxy_url(albumArtURI.uri)
    artistDiscographyURI = getattr(item, 'artistDiscographyURI', None)
    if artistDiscographyURI is not None:
        item.artistDiscographyURI = get_media_proxy_url(artistDiscographyURI.uri)
    return item


def _fixup_didl_items(items):
    return (_fixup_item_media_urls(x) for x in items)


@router.get('/', response_model=DevicesResponse)
def get_media_library_devices(request: Request):
    def create_links(d: models.DeviceModel):
        return {'self': request.url_for('get_media_library_device', udn=d.udn)}

    resp = DevicesResponse.create(request.app.av_control_point.mediaservers, links_factory=create_links)
    return resp


@router.get('/{udn}', response_model=DeviceResponse)
def get_media_library_device(request: Request, udn: str):
    device = request.app.av_control_point.get_mediaserver_by_UDN(udn)
    relationships = {
        'browse': {
            'links': {
                'related': request.url_for('browse_library', udn=udn)
            }
        },
        'metadata': {
            'links': {
                'related': request.url_for('get_object_metadata', udn=udn)
            }
        }
    }
    return DeviceResponse.create(device.udn, device, request.url_for('get_media_library_device', udn=udn),
                                 relationships)


def _url_for_query(request, path, params, query):
    url = request.url_for(path, **params)
    parsed = list(urllib.parse.urlparse(url))
    parsed[4] = urllib.parse.urlencode(query)
    return urllib.parse.urlunparse(parsed)


def _browse_list_relationship_factory(request, udn, item):
    relationships = {
        'browse': {
            'links': {
                'related': _url_for_query(request, 'browse_library', {'udn': udn}, {'objectID': item.id})
            }
        },
        'metadata': {
            'links': {
                'related': _url_for_query(request, 'get_object_metadata', {'udn': udn}, {'objectID': item.id})
            }
        }
    }
    return relationships


@router.get('/{udn}/browse')
async def browse_library(request: Request, udn: str, objectID: str = '0', page: int = 0, pagesize: int = 0):
    try:
        udn = urllib.parse.unquote_plus(udn)
        objectID = urllib.parse.unquote_plus(objectID)
        server = request.app.av_control_point.get_mediaserver_by_UDN(udn)
        result = await server.browse(objectID, starting_index=page * pagesize, requested_count=pagesize)

        payload = [models.LibraryItemMetadata.from_orm(_fixup_item_media_urls(x)) for x in result.objects]
        return LibraryListingResponse.create(
            payload, relationship_factory=lambda x: _browse_list_relationship_factory(request, udn, x))
    except asyncio.TimeoutError:
        _logger.error('Mediaserver browse request timed out')
        raise HTTPException(status_code=504, detail="Request to mediaserver timed out")
    except Exception as e:
        _logger.exception(e)
        raise HTTPException(status_code=404)


@router.get('/{udn}/metadata', response_model_exclude_unset=True)
async def get_object_metadata(request: Request, udn: str, objectID: str = '0'):
    try:
        udn = urllib.parse.unquote_plus(udn)
        objectID = urllib.parse.unquote_plus(objectID)
        server = request.app.av_control_point.get_mediaserver_by_UDN(udn)
        result = await server.browse(objectID, browse_flag=BrowseFlags.BrowseMetadata)
        payload = models.LibraryItemMetadata.from_orm(_fixup_item_media_urls(result.objects[0]))
        return MetadataResponse.create(objectID, payload)
    except asyncio.TimeoutError:
        _logger.error('Mediaserver metadata request timed out')
        raise HTTPException(status_code=504, detail="Request to mediaserver timed out")
    except Exception as e:
        _logger.exception(e)
        raise HTTPException(status_code=404)
