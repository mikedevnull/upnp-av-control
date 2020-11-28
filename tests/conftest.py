import pytest
from upnpavcontrol.core import discovery
from upnpavcontrol.core.notification_backend import NotificationBackend
from upnpavcontrol.core.mediarenderer import MediaRenderer
from upnpavcontrol.core.mediaserver import MediaServer
from .testsupport.upnp_test_requester import UpnpTestRequester
from .testsupport.notification_test_endpoint import NotificationTestEndpoint
from .testsupport.null_advertisement_listener import NullAdvertisementListener
from .testsupport.upnp_device_mocks import UpnpMediaServerDevice, UpnpMediaRendererDevice
from typing import cast, Any


@pytest.fixture
def upnp_test_requester():
    return UpnpTestRequester()


@pytest.fixture
async def mocked_av_control_point(event_loop, upnp_test_requester):
    registry = discovery.DeviceRegistry(advertisement_listener=NullAdvertisementListener)
    endpoint = NotificationTestEndpoint()
    notification_backend = NotificationBackend(endpoint=endpoint, requester=upnp_test_requester)

    from upnpavcontrol.core import AVControlPoint
    test_control_point = AVControlPoint(device_registry=registry, notifcation_backend=notification_backend)

    return test_control_point


@pytest.fixture
async def webapi_client(event_loop, mocked_av_control_point):
    from upnpavcontrol.web import application
    from async_asgi_testclient import TestClient
    application.app.av_control_point = mocked_av_control_point

    async with TestClient(application.app) as test_client:
        yield test_client


@pytest.fixture
async def mocked_server_device(mocked_av_control_point):
    device = MediaServer(UpnpMediaServerDevice())
    mocked_av_control_point._servers[device.udn] = device
    yield device
    mocked_av_control_point._servers.pop(device.udn)


@pytest.fixture
async def mocked_renderer_device(mocked_av_control_point):
    device = MediaRenderer(cast(Any, UpnpMediaRendererDevice()))
    mocked_av_control_point._renderers[device.udn] = device
    yield device
    mocked_av_control_point._renderers.pop(device.udn)
