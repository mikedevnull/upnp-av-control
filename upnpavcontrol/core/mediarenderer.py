class MediaRenderer(object):
    def __init__(self, device):
        self._device = device

    def __repr__(self):
        return '<MediaRenderer {}>'.format(self.friendly_name)

    async def get_volume(self):
        response = await self.rendering_control.action('GetVolume').async_call(
            InstanceID=0, Channel='Master')
        return response['CurrentVolume']

    async def set_volume(self, value):
        return await self.rendering_control.action('SetVolume').async_call(
            InstanceID=0, Channel='Master', DesiredVolume=value)

    @property
    def rendering_control(self):
        return self._device.service(
            'urn:schemas-upnp-org:service:RenderingControl:1')

    @property
    def av_transport(self):
        return self._device.service(
            'urn:schemas-upnp-org:service:AVTransport:1')

    @property
    def connection_manager(self):
        return self._device.service(
            'urn:schemas-upnp-org:service:ConnectionManager:1')

    @property
    def friendly_name(self):
        return self._device.friendly_name

    @property
    def location(self):
        return self._device.location

    @property
    def upnp_device(self):
        return self._device
