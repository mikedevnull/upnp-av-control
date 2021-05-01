from .fake_upnp_device import FakeDeviceDescriptor, FakeAsyncUpnpDevice
from .fake_upnp_service import UpnpServiceMock, _format_last_change_notification, _format_last_change_payload
from .connection_manager import FakeConnectionManagerService
from urllib.parse import urlparse

_descriptor = FakeDeviceDescriptor(name="AcmeRenderer",
                                   friendly_name="Acme Super Blast Renderer",
                                   location='http://192.168.99.1:5000',
                                   udn='13bf6358-00b8-101b-8000-74dfbfed7306',
                                   device_type='MediaRenderer',
                                   service_types=['RenderingControl:1', 'ConnectionManager:1', 'AVTransport:1'])


class FakeAVTransportService(UpnpServiceMock):
    def __init__(self, device):
        super().__init__(service_type="urn:schemas-upnp-org:service:AVTransport:1", device=device)
        self.add_async_action('SetAVTransportURI', self._set_transport)
        self.add_async_action('Play', self._play)

    async def _set_transport(self, InstanceID, CurrentURI, CurrentURIMetaData):
        pass

    async def _play(self, InstanceID, Speed):
        pass


class FakeRenderingControlService(UpnpServiceMock):
    def __init__(self, device):
        super().__init__(service_type="urn:schemas-upnp-org:service:RenderingControl:1", device=device)
        self.add_async_action('GetVolume', self._get_volume)
        self.add_async_action('SetVolume', self._set_volume)
        self._volume = 42
        self._seq = 0

    async def _set_volume(self, DesiredVolume, InstanceID=0, Channel='Master'):
        self._volume = DesiredVolume
        await self.trigger_notification(variables={'Volume': self._volume})

    async def _get_volume(self, InstanceID, Channel):
        return {'CurrentVolume': self._volume}

    async def trigger_notification(self, variables):
        path = self._event_endpoint.callback_url
        host = urlparse(path).netloc
        last_change_value = _format_last_change_payload(variables)
        body = _format_last_change_notification(last_change_value)
        for sid in self._event_subscritions:
            headers = {
                'host': host,
                'content-type': 'text/xml',
                'content-length': str(len(body)),
                'NT': 'upnp:event',
                'NTS': 'upnp:propchange',
                'SID': sid,
                'seq': str(self._seq)
            }
            await self._event_endpoint.trigger_notification(headers, body)
        self._seq = self._seq + 1


def factory():
    device = FakeAsyncUpnpDevice(_descriptor)
    device.mock_add_service(FakeConnectionManagerService(device))
    device.mock_add_service(FakeAVTransportService(device))
    device.mock_add_service(FakeRenderingControlService(device))
    return device