import pytest
from upnpavcontrol.core import discover
from upnpavcontrol.core.discover import DeviceEntry
from upnpavcontrol.core.mediarenderer import MediaRenderer
from upnpavcontrol.core.mediaserver import MediaServer
from .discovery_mocks import create_test_advertisement_listener  # noqa
from .discovery_mocks import mock_async_search, create_test_requester  # noqa
from .discovery_mocks import ssdp_alive_renderer_device_data
from .discovery_mocks import ssdp_byebye_renderer_device_data
from .discovery_mocks import ssdp_alive_server_device_data
from .discovery_mocks import ssdp_alive_printer_device_data
from . import upnp_device_mocks

import functools


@pytest.fixture
def mocked_device_registry():
    registry = discover.DeviceRegistry(
        create_advertisement_listener=create_test_advertisement_listener,
        create_requester=create_test_requester)

    registry.trigger_renderer_alive = functools.partial(
        registry._listener.trigger_alive, ssdp_alive_renderer_device_data)
    registry.trigger_renderer_byebye = functools.partial(
        registry._listener.trigger_byebye, ssdp_byebye_renderer_device_data)
    registry.trigger_server_alive = functools.partial(
        registry._listener.trigger_alive, ssdp_alive_server_device_data)
    registry.trigger_printer_alive = functools.partial(
        registry._listener.trigger_alive, ssdp_alive_printer_device_data)
    return registry


@pytest.fixture
def mock_scanned_devices(monkeypatch):
    monkeypatch.setattr(discover, 'async_search', mock_async_search)


@pytest.fixture
async def testing_av_control_point(mocked_device_registry):
    from upnpavcontrol.core import AVControlPoint
    test_control_point = AVControlPoint(mocked_device_registry)
    return test_control_point


@pytest.fixture
async def webapi_client(testing_av_control_point):
    from upnpavcontrol.web import application
    from async_asgi_testclient import TestClient
    application.app.av_control_point = testing_av_control_point

    async with TestClient(application.app) as test_client:
        yield test_client


@pytest.fixture
async def mocked_renderer_device(testing_av_control_point):
    renderer = MediaRenderer(upnp_device_mocks.UpnpMediaRendererDevice())
    mockedRendererEntry = DeviceEntry(
        device=renderer,
        device_type="urn:schemas-upnp-org:device:MediaRenderer:1")
    udn = mockedRendererEntry.device.udn
    testing_av_control_point._devices._av_devices[udn] = mockedRendererEntry
    return mockedRendererEntry.device


@pytest.fixture
async def mocked_server_device(testing_av_control_point):
    server = MediaServer(upnp_device_mocks.UpnpMediaServerDevice())
    mockedServerEntry = DeviceEntry(
        device=server, device_type="urn:schemas-upnp-org:device:MediaServer:1")
    udn = mockedServerEntry.device.udn
    testing_av_control_point._devices._av_devices[udn] = mockedServerEntry
    return mockedServerEntry.device
