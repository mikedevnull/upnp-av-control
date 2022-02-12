from .fake_upnp_service import UpnpServiceMock


class FakeRenderingControlService(UpnpServiceMock):

    def __init__(self, device):
        super().__init__(service_type="urn:schemas-upnp-org:service:RenderingControl:1", device=device)
        self.add_async_action('GetVolume', self._get_volume)
        self.add_async_action('SetVolume', self._set_volume)
        self._volume = 42

    @property
    def volume(self):
        return self._volume

    async def _set_volume(self, DesiredVolume, InstanceID=0, Channel='Master'):
        self._volume = DesiredVolume
        await self.trigger_notification(instance_xml_namespace='{urn:schemas-upnp-org:metadata-1-0/RCS/}',
                                        variables={'Volume': self._volume})

    async def _get_volume(self, InstanceID, Channel):
        return {'CurrentVolume': self._volume}
