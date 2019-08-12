class MediaServer(object):
    def __init__(self, device):
        self._device = device

    @property
    def upnp_device(self):
        return self._device

    @property
    def udn(self):
        return self.upnp_device.udn

    def __repr__(self):
        return '<MediaServer {}>'.format(self._device.friendly_name)
