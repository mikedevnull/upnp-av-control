import logging
from .notification_backend import NotificationBackend
from async_upnp_client import UpnpStateVariable, UpnpDevice, UpnpService
import defusedxml.ElementTree as etree
from typing import Iterable, Optional, cast
import asyncio
from dataclasses import dataclass


@dataclass
class PlaybackInfo(object):
    volume_percent: int = 0


_nsmap = {
    'upnp': 'urn:schemas-upnp-org:metadata-1-0/upnp/',
    'dc': 'http://purl.org/dc/elements/1.1/',
    'avt': 'urn:schemas-upnp-org:metadata-1-0/AVT/',
    'rcs': 'urn:schemas-upnp-org:metadata-1-0/RCS/'
}


def update_playback_info_from_event(info: PlaybackInfo, event: str) -> bool:
    tree = etree.fromstring(event)
    any_value_changed = False
    vol = tree.find("./rcs:InstanceID[@val='0']/rcs:Volume[@channel='Master']", namespaces=_nsmap)
    if vol is not None:
        value = int(vol.attrib['val'])
        if value != info.volume_percent:
            info.volume_percent = value
            any_value_changed = True
    return any_value_changed


async def create_media_renderer(device: UpnpDevice, notification_backend: Optional[NotificationBackend] = None):
    """
    Factory function to create a MediaRenderer.

    Use this function instead of calling `MediaRenderer.__init__()` to construct new MediaRenderers.

    The rationale behind this is that this factory function will use some async functions to update the renderers
    internal state, and `__init__` methods cannot be async.
    """
    renderer = MediaRenderer(device, notification_backend)
    await renderer.update_playback_info()
    return renderer


class MediaRenderer(object):
    def __init__(self, device: UpnpDevice):
        self._device = device
        self._notify_backend = None
        self.rendering_control.on_event = self.notify

    def notify(self, service: UpnpService, variables: Iterable[UpnpStateVariable]):
        for variable in variables:
            logging.info('%s -> %s', variable.name, variable.value)

    def __repr__(self):
        return '<MediaRenderer {}>'.format(self.friendly_name)

    async def get_volume(self):
        response = await self.rendering_control.action('GetVolume').async_call(InstanceID=0, Channel='Master')
        return response['CurrentVolume']

    async def set_volume(self, value):
        return await self.rendering_control.action('SetVolume').async_call(InstanceID=0,
                                                                           Channel='Master',
                                                                           DesiredVolume=value)

    @property
    def playback_info(self):
        return self._playback_info

    async def update_playback_info(self):
        self._playback_info.volume_percent = await self.get_volume()

            return
        if self._notify_backend is not None:
            self.disable_notifications()
        self._notify_backend = backend
        if self._notify_backend is not None:
            if self.rendering_control:
                await self._notify_backend.subscribe(self.rendering_control)

    async def disable_notifications(self):
        try:
            if self._notify_backend is not None:
                if self.rendering_control:
                    await self._notify_backend.unsubscribe(self.rendering_control)
        except asyncio.TimeoutError:
            logging.warning('Failed to unsubscribe from notifications from %s', self.friendly_name)
        finally:
            # this is required to ensure notifications can be re-enabled
            self._notify_backend = None

    @property
    def udn(self):
        return self.upnp_device.udn.lstrip('uuid:')

    @property
    def rendering_control(self):
        return self._device.service('urn:schemas-upnp-org:service:RenderingControl:1')

    @property
    def av_transport(self):
        return self._device.service('urn:schemas-upnp-org:service:AVTransport:1')

    @property
    def connection_manager(self):
        return self._device.service('urn:schemas-upnp-org:service:ConnectionManager:1')

    @property
    def friendly_name(self):
        return self._device.friendly_name

    @property
    def upnp_device(self):
        return self._device
