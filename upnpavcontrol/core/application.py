from .discover import DeviceRegistry, is_media_renderer, is_media_server
import logging
from .notification_backend import NotificationBackend, AiohttpNotificationEndpoint
from async_upnp_client.aiohttp import AiohttpRequester


class AVControlPoint(object):
    def __init__(self, device_registry=None, notifcation_backend=None):
        if device_registry is None:
            self._devices = DeviceRegistry()
        else:
            self._devices = device_registry
        self._active_renderer = None
        if notifcation_backend is None:
            self._notify_receiver = NotificationBackend(AiohttpNotificationEndpoint(), AiohttpRequester())
        else:
            self._notify_receiver = notifcation_backend

    @property
    def mediaservers(self):
        return [entity.device for entity in self._devices._av_devices.values() if is_media_server(entity.device_type)]

    def getMediaServerByUDN(self, udn: str):
        device = self.devices[udn]
        if not is_media_server(device):
            raise KeyError('No mediaserver with given UDN found')

    @property
    def mediarenderers(self):
        return [entity.device for entity in self._devices._av_devices.values() if is_media_renderer(entity.device_type)]

    @property
    def devices(self):
        return self._devices._av_devices

    @property
    def mediarenderer(self):
        return self._active_renderer

    async def set_renderer(self, deviceUDN: str):
        if deviceUDN in self._devices._av_devices:
            if self._active_renderer is not None:
                await self._active_renderer.disable_notifications()
            entry = self._devices._av_devices[deviceUDN]
            if is_media_renderer(entry.device_type):
                self._active_renderer = entry.device
                await self._active_renderer.enable_notifications(self._notify_receiver)
            else:
                logging.error('%s is not a media renderer', entry.device.friendly_name)
                raise KeyError('Not a media renderer')
        else:
            logging.error('Unkown device %s requested', deviceUDN)
            raise KeyError('Device not found')

    async def async_start(self):
        await self._devices.async_start()
        await self._notify_receiver.async_start()

    async def async_stop(self):
        await self._devices.async_stop()
        await self._notify_receiver.async_stop()
