from .discover import DeviceRegistry, is_media_renderer, is_media_server
import asyncio
import logging


class AVControlPoint(object):
    def __init__(self):
        self._devices = DeviceRegistry()
        self._active_renderer = None

    @property
    def mediaservers(self):
        return [
            entity.device for entity in self._devices._av_devices.values()
            if is_media_server(entity.device_type)
        ]

    @property
    def mediarenderers(self):
        return [
            entity.device for entity in self._devices._av_devices.values()
            if is_media_renderer(entity.device_type)
        ]

    @property
    def mediarenderer(self):
        return self._active_renderer

    def set_renderer(self, deviceUDN: str):
        if deviceUDN in self._devices._av_devices:
            entry = self._devices._av_devices[deviceUDN]
            if is_media_renderer(entry.device_type):
                self._active_renderer = entry.device
            else:
                logging.error('%s is not a media renderer',
                              entry.device.friendly_name)
        else:
            logging.error('Unkown device %s requested', deviceUDN)

    async def run(self):
        loop = asyncio.get_running_loop()
        loop.create_task(self._devices.start())
