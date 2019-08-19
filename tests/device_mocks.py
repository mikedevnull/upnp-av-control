from unittest import mock
from upnpavcontrol.core.discover import DeviceEntry
from upnpavcontrol.core.mediarenderer import MediaRenderer


class _UpnpDeviceMock(object):
    """
    A base class designed to mock a async_upnp_client.Device.

    Add mocked services with mocked actions, which can be called
    async and checked.
    """

    def __init__(self, friendly_name: str, udn: str, location: str):
        self._services = {}
        self.friendly_name = friendly_name
        self.udn = udn
        self.location = location

        self.add_service_mock(RenderingControlService())

    def service(self, service_type):
        return self._services[service_type]

    def add_service_mock(self, service):
        self._services[service.service_type] = service


class _UpnpServiceMock(object):
    def __init__(self):
        self._actions = {}

    def action(self, name):
        return self._actions[name]

    def add_action_mock(self, name, *args, **kwargs):
        self._actions[name] = _AsyncActionMock(*args, **kwargs)


class _AsyncActionMock(object):
    def __init__(self, *args, **kwargs):
        self.mock = mock.MagicMock(*args, **kwargs)

    async def async_call(self, *args, **kwargs):
        return self.mock(*args, **kwargs)


class RenderingControlService(_UpnpServiceMock):
    def __init__(self):
        super().__init__()
        self.add_action_mock('GetVolume')

    @property
    def service_type(self):
        return "urn:schemas-upnp-org:service:RenderingControl:1"


class UpnpMediaRendererDevice(_UpnpDeviceMock):
    def __init__(self):
        self._services = {}
        self.friendly_name = "FooRenderer"
        self.udn = "e094faa8-c2bb-11e9-b72e-705681aa5dfd"
        self.location = "http:://localhost:12342"

        self.add_service_mock(RenderingControlService())

    def service(self, service_type):
        return self._services[service_type]

    def add_service_mock(self, service):
        self._services[service.service_type] = service


def addMockedMediaRenderer(av_control_point):
    renderer = MediaRenderer(UpnpMediaRendererDevice())
    mockedRendererEntry = DeviceEntry(
        device=renderer,
        device_type="urn:schemas-upnp-org:device:MediaRenderer:1")
    udn = mockedRendererEntry.device.udn
    av_control_point._devices._av_devices[udn] = mockedRendererEntry
    return mockedRendererEntry.device
