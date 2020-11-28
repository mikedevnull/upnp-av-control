import pytest
from upnpavcontrol.core import discovery
from upnpavcontrol.core.discovery.registry import DeviceEntry, MediaDeviceType
from upnpavcontrol.core.mediarenderer import MediaRenderer
from upnpavcontrol.core.mediaserver import MediaServer
from .discovery_mocks import TestingAdvertisementListener
from . import upnp_device_mocks, upnp_event_mocks
from .upnp_test_requester import UpnpTestRequester
from .upnp_event_mocks import NotificationTestEndpoint
from upnpavcontrol.core.notification_backend import NotificationEndpointBase, NotificationBackend
from .upnp_device_mocks import UpnpMediaRendererDevice


@pytest.fixture
def upnp_test_requester():
    return UpnpTestRequester()


@pytest.fixture
async def mocked_av_control_point(event_loop, upnp_test_requester):
    registry = discovery.DeviceRegistry(advertisement_listener=TestingAdvertisementListener)
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
    device = MediaServer(upnp_device_mocks.UpnpMediaServerDevice())
    mocked_av_control_point._servers[device.udn] = device
    yield device
    mocked_av_control_point._servers.pop(device.udn)


# @pytest.fixture
# async def mediarenderer_http_responses():
#     with aioresponses() as m:
#         m.get('http://192.168.99.1:1234/dmr.xml', body=_read_data_file('dmr_99_1.xml'))
#         m.get('http://192.168.99.1:1234/dmr_rcs.xml', status=200, body=_read_data_file('dmr_rcs_99_1.xml')),
#         m.get('http://192.168.99.1:1234/dmr_cms.xml', status=200, body=_read_data_file('dmr_cms_99_1.xml')),
#         m.get('http://192.168.99.1:1234/dmr_avts.xml', status=200, body=_read_data_file('dmr_avts_99_1.xml')),
#         yield

#from upnpavcontrol.core.discovery.registry import DeviceEntry, MediaDeviceType


@pytest.fixture
async def mocked_renderer_device(mocked_av_control_point):
    device = MediaRenderer(UpnpMediaRendererDevice())
    mocked_av_control_point._renderers[device.udn] = device
    yield device
    mocked_av_control_point._renderers.pop(device.udn)
