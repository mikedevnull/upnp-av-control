import upnpclient


class MediaRenderer(object):
    def __init__(self, location):
        self._device = upnpclient.Device(location=location)

    def __repr__(self):
        return '<MediaRenderer {}>'.format(self._device.friendly_name)
