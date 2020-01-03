from .discover import DeviceRegistry, is_media_renderer, is_media_server
import asyncio
import logging


class AVControlPoint(object):
    def __init__(self, device_registry=None):
        if device_registry is None:
            self._devices = DeviceRegistry()
        else:
            self._devices = device_registry
        self._active_renderer = None

    @property
    def mediaservers(self):
        return [entity.device for entity in self._devices._av_devices.values() if is_media_server(entity.device_type)]

    @property
    def mediarenderers(self):
        return [entity.device for entity in self._devices._av_devices.values() if is_media_renderer(entity.device_type)]

    @property
    def devices(self):
        return self._devices._av_devices

    @property
    def mediarenderer(self):
        return self._active_renderer

    def set_renderer(self, deviceUDN: str):
        if deviceUDN in self._devices._av_devices:
            entry = self._devices._av_devices[deviceUDN]
            if is_media_renderer(entry.device_type):
                self._active_renderer = entry.device
            else:
                logging.error('%s is not a media renderer', entry.device.friendly_name)
                raise KeyError('Not a media renderer')
        else:
            logging.error('Unkown device %s requested', deviceUDN)
            raise KeyError('Device not found')

    async def async_start(self):
        try:
            await self._devices.async_start()
        except asyncio.CancelledError:
            logging.debug('AV Control point cancelled')

    async def async_stop(self):
        await self._devices.async_stop()
