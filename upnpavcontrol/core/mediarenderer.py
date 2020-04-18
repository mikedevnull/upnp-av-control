import logging
from .notification_backend import NotificationBackend
from async_upnp_client import UpnpStateVariable, UpnpDevice, UpnpService
from typing import Iterable
import asyncio


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

    async def enable_notifications(self, backend: NotificationBackend):
        if self._notify_backend == backend:
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
    def location(self):
        return self._device.location

    @property
    def upnp_device(self):
        return self._device
