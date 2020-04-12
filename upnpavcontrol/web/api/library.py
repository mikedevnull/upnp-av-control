from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from typing import List
import urllib.parse
import logging

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
    except Exception as e:
        _logger.exception(e)
        raise HTTPException(status_code=404)
