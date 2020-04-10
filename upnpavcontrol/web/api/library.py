from fastapi import APIRouter, Request, HTTPException
import urllib.parse
from upnpavcontrol.core.discover import is_media_server

router = APIRouter()


def _format_server(device, request):
    return {
        'name': device.friendly_name,
        'udn': device.udn,
        'links': {
            'browse': _format_browse_url(device.udn, None, request)
        }
    }


def _format_browse_url(udn: str, objectId: str, request):
    browseUrl = request.app.url_path_for('browse_library', udn=udn)
    if objectId is not None:
        query = urllib.parse.urlencode({'objectID': objectId})
        browseUrl = browseUrl + '?' + query
    return browseUrl


def _format_didl_entry(udn: str, entry, request):
    data = {values[1]: getattr(entry, values[1]) for values in entry.didl_properties_defs if hasattr(entry, values[1])}
    data['tag'] = entry.tag
    if entry.tag == 'container':
        data['browseChildren'] = _format_browse_url(udn, entry.id, request)
    return data


def _format_didl_entries(udn, entries, request):
    return [_format_didl_entry(udn, x, request) for x in entries]


@router.get('/devices')
def get_media_library_devices(request: Request):
    return {'data': [_format_server(x, request) for x in request.app.av_control_point.mediaservers]}


@router.get('/browse/{udn}')
async def browse_library(request: Request, udn: str, objectID: str = '0'):
    if udn not in request.app.av_control_point.devices or not \
            is_media_server(request.app._av_control_point.devices[udn].device_type):
        raise HTTPException(status_code=404)
    server = request.app.av_control_point.devices[udn].device
    result = await server.browse(objectID)
    return _format_didl_entries(udn, result, request)
