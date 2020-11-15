import pytest
from upnpavcontrol.core import discovery
from upnpavcontrol.core.discovery.registry import DeviceEntry
from upnpavcontrol.core.mediarenderer import MediaRenderer
from upnpavcontrol.core.mediaserver import MediaServer
from .discovery_mocks import TestingAdvertisementListener
from .discovery_mocks import create_test_requester  # noqa
from . import upnp_device_mocks, upnp_event_mocks


@pytest.fixture
async def mocked_av_control_point(event_loop):
    registry = discovery.DeviceRegistry(advertisement_listener=TestingAdvertisementListener,
                                        upnp_requester=create_test_requester())

    from upnpavcontrol.core import AVControlPoint
    test_control_point = AVControlPoint(device_registry=registry,
                                        notifcation_backend=upnp_event_mocks.create_test_notification_backend())

    yield test_control_point


@pytest.fixture
async def webapi_client(event_loop, mocked_av_control_point):
    from upnpavcontrol.web import application
    from async_asgi_testclient import TestClient
    application.app.av_control_point = mocked_av_control_point

    async with TestClient(application.app) as test_client:
        yield test_client


@pytest.fixture
async def mocked_renderer_device(mocked_av_control_point):
    renderer = MediaRenderer(upnp_device_mocks.UpnpMediaRendererDevice())
    mockedRendererEntry = DeviceEntry(device=renderer, device_type="urn:schemas-upnp-org:device:MediaRenderer:1")
    udn = mockedRendererEntry.device.udn
    mocked_av_control_point._devices._av_devices[udn] = mockedRendererEntry
    return mockedRendererEntry.device


@pytest.fixture
async def mocked_server_device(mocked_av_control_point):
    server = MediaServer(upnp_device_mocks.UpnpMediaServerDevice())
    mockedServerEntry = DeviceEntry(device=server, device_type="urn:schemas-upnp-org:device:MediaServer:1")
    udn = mockedServerEntry.device.udn
    mocked_av_control_point._devices._av_devices[udn] = mockedServerEntry
    return mockedServerEntry.device
