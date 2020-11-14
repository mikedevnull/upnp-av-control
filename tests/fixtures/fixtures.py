import pytest
from upnpavcontrol.core import discovery
import upnpavcontrol.core.discovery.scan
from upnpavcontrol.core.discovery.registry import DeviceEntry
from upnpavcontrol.core.mediarenderer import MediaRenderer
from upnpavcontrol.core.mediaserver import MediaServer
from .discovery_mocks import TestingAdvertisementListener
from .discovery_mocks import mock_async_search, create_test_requester  # noqa
from . import upnp_device_mocks, upnp_event_mocks
import typing


@pytest.fixture
async def mocked_device_registry():
    registry = discovery.DeviceRegistry(advertisement_listener=TestingAdvertisementListener,
                                        upnp_requester=create_test_requester())

    registry.trigger_renderer_alive = registry._listener.trigger_renderer_alive
    registry.trigger_renderer_byebye = registry._listener.trigger_renderer_byebye
    registry.trigger_server_alive = registry._listener.trigger_server_alive
    registry.trigger_printer_alive = registry._listener.trigger_printer_alive

    return registry


@pytest.fixture
async def started_mocked_device_registry(mocked_device_registry):
    await mocked_device_registry.async_start()
    yield mocked_device_registry
    await mocked_device_registry.async_stop()


@pytest.fixture
def mock_scanned_devices(monkeypatch):
    monkeypatch.setattr(upnpavcontrol.core.discovery.scan, 'async_search', mock_async_search)


@pytest.fixture
def mocked_notification_backend(event_loop):
    return upnp_event_mocks.create_test_notification_backend()


@pytest.fixture
async def testing_av_control_point(event_loop, mocked_device_registry, mocked_notification_backend):
    from upnpavcontrol.core import AVControlPoint
    test_control_point = AVControlPoint(device_registry=mocked_device_registry,
                                        notifcation_backend=mocked_notification_backend)

    yield test_control_point


@pytest.fixture
async def webapi_client(event_loop, testing_av_control_point):
    from upnpavcontrol.web import application
    from async_asgi_testclient import TestClient
    application.app.av_control_point = testing_av_control_point

    async with TestClient(application.app) as test_client:
        yield test_client


@pytest.fixture
async def mocked_renderer_device(testing_av_control_point):
    renderer = MediaRenderer(upnp_device_mocks.UpnpMediaRendererDevice())
    mockedRendererEntry = DeviceEntry(device=renderer, device_type="urn:schemas-upnp-org:device:MediaRenderer:1")
    udn = mockedRendererEntry.device.udn
    testing_av_control_point._devices._av_devices[udn] = mockedRendererEntry
    return mockedRendererEntry.device


@pytest.fixture
async def mocked_server_device(testing_av_control_point):
    server = MediaServer(upnp_device_mocks.UpnpMediaServerDevice())
    mockedServerEntry = DeviceEntry(device=server, device_type="urn:schemas-upnp-org:device:MediaServer:1")
    udn = mockedServerEntry.device.udn
    testing_av_control_point._devices._av_devices[udn] = mockedServerEntry
    return mockedServerEntry.device
