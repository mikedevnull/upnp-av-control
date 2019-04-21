import upnpclient


class MediaRenderer(object):
    def __init__(self, location):
        self._device = upnpclient.Device(location=location)

    def __repr__(self):
        return '<MediaRenderer {}>'.format(self.friendly_name)

    @property
    def volume(self):
        response = self.rendering_control.GetVolume(InstanceID=0, Channel='Master')
        return response['CurrentVolume']

    @volume.setter
    def volume(self, value):
        return self.rendering_control.SetVolume(InstanceID=0, Channel='Master', DesiredVolume=value)
    
    @property
    def mute(self):
        response = self.rendering_control.GetMute(InstanceID=0, Channel='Master')
        return response['CurrentMute']

    @mute.setter
    def mute(self, value):
        self.rendering_control.SetMute(InstanceID=0, Channel='Master', DesiredMute=str(bool(value)))

    @property
    def rendering_control(self):
        return self._device.RenderingControl

    @property
    def av_transport(self):
        return self._device.avTransport

    @property
    def connection_manager(self):    
        return self._device.ConnectionManager

    @property
    def friendly_name(self):
        return self._device.friendly_name

    @property
    def location(self):
        return self._device.location

    @property
    def upnp_device(self):
        return self._device
