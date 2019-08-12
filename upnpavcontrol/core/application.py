from .discover import DeviceRegistry, is_media_renderer, is_media_server
import asyncio


class AVControlPoint(object):
    def __init__(self):
        self._devices = DeviceRegistry()

    @property
    def media_servers(self):
        return [
            entity.device for entity in self._devices._av_devices.values()
            if is_media_server(entity.device_type)
        ]

    @property
    def media_renderer(self):
        return [
            entity.device for entity in self._devices._av_devices.values()
            if is_media_renderer(entity.device_type)
        ]

    async def run(self):
        loop = asyncio.get_running_loop()
        loop.create_task(self._devices.start())