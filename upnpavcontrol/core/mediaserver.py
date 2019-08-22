class MediaServer(object):
    def __init__(self, device):
        self._device = device

    @property
    def friendly_name(self):
        return self._device.friendly_name

    @property
    def upnp_device(self):
        return self._device

    @property
    def udn(self):
        return self._device.udn

    @property
    def av_transport(self):
        return self._device.service(
            'urn:schemas-upnp-org:service:AVTransport:1')

    @property
    def connection_manager(self):
        return self._device.service(
            'urn:schemas-upnp-org:service:ConnectionManager:1')

    @property
    def content_directory(self):
        return self._device.service(
            'urn:schemas-upnp-org:service:ContentDirectory:1')

    def __repr__(self):
        return '<MediaServer {}>'.format(self._device.friendly_name)
