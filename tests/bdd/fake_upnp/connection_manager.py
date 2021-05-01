from .fake_upnp_service import UpnpServiceMock


class FakeConnectionManagerService(UpnpServiceMock):
    def __init__(self, device):
        super().__init__(service_type="urn:schemas-upnp-org:service:ConnectionManager:1", device=device)
        self.add_async_action('GetProtocolInfo', self._protoinfo)
        self.sink_protocols = 'http-get:*:audio/mpeg:*'
        self.source_protocols = ''

    async def _protoinfo(self):
        return {'Sink': self.sink_protocols, 'Source': self.source_protocols}
