import upnpclient


class MediaServer(object):
    def __init__(self, location):
        self._device = upnpclient.Device(location=location)

    def __repr__(self):
        return '<MediaServer {}>'.format(self._device.friendly_name)

