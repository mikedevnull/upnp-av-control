import pytest
import os.path
from async_upnp_client import UpnpRequester
from upnpavcontrol.core import discover
import asyncio
from .mock_utils import create_test_advertisement_listener
from .mock_utils import mock_async_search, create_test_requester
from .mock_utils import UpnpTestAdvertisementListener


class UpnpTestAdvertisementListener(object):
    def __init__(self, on_alive, on_byebye, on_update):
        self._on_alive = on_alive
        self._on_byebye = on_byebye
        self._on_update = on_update

    async def trigger_alive(self, payload):
        await self._on_alive(payload)

    async def trigger_byebye(self, payload):
        await self._on_byebye(payload)


def _read_data_file(filename):
    filepath = os.path.join('tests', 'data', filename)
    with open(filepath, 'r') as handle:
        return handle.read()


class UpnpTestRequester(UpnpRequester):
    def __init__(self, response_map):
        self._response_map = response_map

    async def async_do_http_request(self,
                                    method,
                                    url,
                                    headers=None,
                                    body=None,
                                    body_type='text'):

        key = (method, url)
        if key not in self._response_map:
            raise asyncio.TimeoutError('Unkown resource for request: %s' %
                                       str(key))

        return self._response_map[key]


_RESPONSES = {
    ('GET', 'http://192.168.99.1:1234/dmr.xml'):
    (200, {}, _read_data_file('dmr_99_1.xml')),
    ('GET', 'http://192.168.99.1:1234/dmr_rcs.xml'):
    (200, {}, _read_data_file('dmr_rcs_99_1.xml')),
    ('GET', 'http://192.168.99.1:1234/dmr_cms.xml'):
    (200, {}, _read_data_file('dmr_cms_99_1.xml')),
    ('GET', 'http://192.168.99.1:1234/dmr_avts.xml'):
    (200, {}, _read_data_file('dmr_avts_99_1.xml')),
    ('GET', 'http://192.168.99.2:9200/plugins/MediaServer.xml'):
    (200, {}, _read_data_file('dms_99_2.xml')),
    ('GET', 'http://192.168.99.2:9200/plugins/UPnP/MediaServer/ContentDirectory.xml'):  # noqa: E501
    (200, {}, _read_data_file('dms_cds_99_2.xml')),
    ('GET', 'http://192.168.99.2:9200/plugins/UPnP/MediaServer/ConnectionManager.xml'):  # noqa: E501
    (200, {}, _read_data_file('dms_cms_99_2.xml')),
    ('GET', 'http://192.168.99.2:9200/plugins/UPnP/MediaServer/MediaReceiverRegistrar.xml'):  # noqa: E501
    (200, {}, _read_data_file('dms_mrrs_99_2.xml'))
}


def _create_test_requester():
    return UpnpTestRequester(_RESPONSES)
@pytest.fixture
def mocked_device_registry():
    return discover.DeviceRegistry(
        create_advertisement_listener=create_test_advertisement_listener,
        create_requester=create_test_requester)


@pytest.fixture
def mock_discovery_backend(monkeypatch):
    monkeypatch.setattr(discover, 'UpnpAdvertisementListener',
                        UpnpTestAdvertisementListener)
    monkeypatch.setattr(discover, 'AiohttpRequester', _create_test_requester)




@pytest.fixture
def mock_scanned_devices(monkeypatch):
    monkeypatch.setattr(discover, 'async_search', mock_async_search)
