import os.path
from async_upnp_client import UpnpRequester
import asyncio
from upnpavcontrol.core import discover


class UpnpTestAdvertisementListener(object):
    def __init__(self, on_alive, on_byebye, on_update):
        self._on_alive = on_alive
        self._on_byebye = on_byebye
        self._on_update = on_update

    async def trigger_alive(self, payload):
        await self._on_alive(payload)
        return payload

    async def trigger_byebye(self, payload):
        await self._on_byebye(payload)
        return payload

    async def async_start(self):
        pass


def _read_data_file(filename):
    filepath = os.path.join('tests', 'data', filename)
    with open(filepath, 'r') as handle:
        return handle.read()


class UpnpTestRequester(UpnpRequester):
    def __init__(self, response_map):
        self._response_map = response_map

    async def async_do_http_request(self, method, url, headers=None, body=None, body_type='text'):

        key = (method, url)
        if key not in self._response_map:
            raise asyncio.TimeoutError('Unkown resource for request: %s' % str(key))

        return self._response_map[key]


_RESPONSES = {
    ('GET', 'http://192.168.99.1:1234/dmr.xml'): (200, {}, _read_data_file('dmr_99_1.xml')),
    ('GET', 'http://192.168.99.1:1234/dmr_rcs.xml'): (200, {}, _read_data_file('dmr_rcs_99_1.xml')),
    ('GET', 'http://192.168.99.1:1234/dmr_cms.xml'): (200, {}, _read_data_file('dmr_cms_99_1.xml')),
    ('GET', 'http://192.168.99.1:1234/dmr_avts.xml'): (200, {}, _read_data_file('dmr_avts_99_1.xml')),
    ('GET', 'http://192.168.99.2:9200/plugins/MediaServer.xml'): (200, {}, _read_data_file('dms_99_2.xml')),
    ('GET', 'http://192.168.99.2:9200/plugins/UPnP/MediaServer/ContentDirectory.xml'):  # noqa: E501
    (200, {}, _read_data_file('dms_cds_99_2.xml')),
    ('GET', 'http://192.168.99.2:9200/plugins/UPnP/MediaServer/ConnectionManager.xml'):  # noqa: E501
    (200, {}, _read_data_file('dms_cms_99_2.xml')),
    ('GET', 'http://192.168.99.2:9200/plugins/UPnP/MediaServer/MediaReceiverRegistrar.xml'):  # noqa: E501
    (200, {}, _read_data_file('dms_mrrs_99_2.xml'))
}


def create_test_requester():
    return UpnpTestRequester(_RESPONSES)


def create_test_advertisement_listener(on_alive, on_byebye, on_update):
    return UpnpTestAdvertisementListener(on_alive=on_alive, on_byebye=on_byebye, on_update=on_update)


ssdp_alive_renderer_device_data = {
    'Host': '239.255.255.250:1900',
    'Cache-Control': 'max-age=1800',
    'Location': 'http://192.168.99.1:1234/dmr.xml',
    'NT': 'urn:schemas-upnp-org:device:MediaRenderer:1',
    'NTS': 'ssdp:alive',
    'Server': 'foonix/1.2 UPnP/1.0 FooRender/1.50',
    'USN': 'uuid:13bf6358-00b8-101b-8000-74dfbfed7306::urn:schemas-upnp-org:device:MediaRenderer:1'  # noqa: E501
}

ssdp_alive_printer_device_data = {
    'Host': '239.255.255.250:1900',
    'Cache-Control': 'max-age=1800',
    'Location': 'http://192.168.99.3:1234/device.xml',
    'NT': 'urn:schemas-upnp-org:device:printer:1',
    'Server': 'foonix/1.2 UPnP/1.0 FooPrinter/1.50',
    'NTS': 'ssdp:alive',
    'USN': 'uuid:92b65aa0-c1dc-11e9-8a7b-705681aa5dfd::urn:schemas-upnp-org:device:printer:1'  # noqa: E501
}

ssdp_alive_server_device_data = {
    'Host': '239.255.255.250:1900',
    'Cache-Control': 'max-age=1800',
    'Location': 'http://192.168.99.2:9200/plugins/MediaServer.xml',
    'NT': 'urn:schemas-upnp-org:device:MediaServer:1',
    'NTS': 'ssdp:alive',
    'Server': 'foonix/1.2 UPnP/1.0 FooServer/1.50',
    'USN': 'uuid:f5b1b596-c1d2-11e9-af8b-705681aa5dfd::urn:schemas-upnp-org:device:MediaServer:1'  # noqa: E501
}

ssdp_byebye_renderer_device_data = {
    'Host': '239.255.255.250:1900',
    'Location': 'http://192.168.99.1:1234/dmr.xml',
    'NT': 'urn:schemas-upnp-org:device:MediaRenderer:1',
    'NTS': 'ssdp:byebye',
    'USN': 'uuid:13bf6358-00b8-101b-8000-74dfbfed7306::urn:schemas-upnp-org:device:MediaRenderer:1'  # noqa: E501
}

ssdp_scan_server_device_data = {
    'Host': '239.255.255.250:1900',
    'Cache-Control': 'max-age=1800',
    'Location': 'http://192.168.99.2:9200/plugins/MediaServer.xml',
    'ST': 'urn:schemas-upnp-org:device:MediaServer:1',
    'NTS': 'ssdp:alive',
    'Server': 'foonix/1.2 UPnP/1.0 FooServer/1.50',
    'USN': 'uuid:f5b1b596-c1d2-11e9-af8b-705681aa5dfd::urn:schemas-upnp-org:device:MediaServer:1'  # noqa: E501
}

ssdp_scan_renderer_device_data = {
    'Cache-Control': 'max-age=1800',
    'Ext': None,
    'Location': 'http://192.168.99.1:1234/dmr.xml',
    'ST': 'urn:schemas-upnp-org:device:MediaRenderer:1',
    'NTS': 'ssdp:alive',
    'Server': 'foonix/1.2 UPnP/1.0 FooRender/1.50',
    'USN': 'uuid:13bf6358-00b8-101b-8000-74dfbfed7306::urn:schemas-upnp-org:device:MediaRenderer:1'  # noqa: E501
}


async def mock_async_search(async_callback, timeout, service_type):
    if discover.is_media_renderer(service_type):
        await async_callback(ssdp_scan_renderer_device_data)
    elif discover.is_media_server(service_type):
        await async_callback(ssdp_scan_server_device_data)


async def find_dummy_renderer_server(av_control_point):
    await av_control_point._devices._listener.trigger_alive(ssdp_alive_renderer_device_data)  # noqa: E501
    await av_control_point._devices._listener.trigger_alive(ssdp_alive_server_device_data)  # noqa: E501
