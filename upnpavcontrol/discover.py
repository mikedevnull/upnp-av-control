import logging
from .mediaserver import MediaServer
from .mediarenderer import MediaRenderer
import re
from async_upnp_client.search import async_search
from async_upnp_client.aiohttp import AiohttpRequester
from async_upnp_client.advertisement import UpnpAdvertisementListener
import async_upnp_client
import asyncio
import functools

media_server_regex = re.compile(
    r'urn:schemas-upnp-org:device:MediaServer:[1-9]')
media_renderer_regex = re.compile(
    r'urn:schemas-upnp-org:device:MediaRenderer:[1-9]')

_logger = logging.getLogger(__name__)


def is_media_server(service_type):
    return media_server_regex.match(service_type)


def is_media_renderer(service_type):
    return media_renderer_regex.match(service_type)


async def _create_device(factory, description):
    device = await factory.async_create_device(description['Location'])
    if media_server_regex.match(description['ST']):
        server = MediaServer(device)
        return server
    elif media_renderer_regex.match(description['ST']):
        renderer = MediaRenderer(device)
        return renderer


async def async_scan(factory, timeout=3):
    device_tasks = []
    create_device = functools.partial(_create_device, factory)

    # async def create_device(description):
    #     return _create_device(factory, description)
    async def handle_discovery(description):
        _logger.info('Found %s at %s', description['ST'],
                     description['Location'])

        device_task = asyncio.create_task(create_device(description))
        device_tasks.append(device_task)

    renderer_search = async_search(
        handle_discovery,
        service_type='urn:schemas-upnp-org:device:MediaRenderer:1')

    server_search = async_search(
        handle_discovery,
        service_type='urn:schemas-upnp-org:device:MediaServer:1')

    await asyncio.wait([renderer_search, server_search])
    devices = await asyncio.gather(*device_tasks)

    return devices


class DeviceRegistry(object):
    def __init__(self):
        self._listener = UpnpAdvertisementListener(on_alive=self._on_alive,
                                                   on_byebye=self._on_byebye,
                                                   on_update=self._on_update)
        self._av_devices = {}
        self._factory = async_upnp_client.UpnpFactory(AiohttpRequester())

    async def start(self):
        _logger.info("Starting device registry")
        loop = asyncio.get_event_loop()
        loop.create_task(self.scan())
        loop.create_task(self._listener.async_start())

    async def scan(self):
        devices = await async_scan(self._factory)
        for device in devices:
            usn = device.upnp_device.udn
            if usn not in self._av_devices:
                self._av_devices[usn] = device
                _logger.info("Found new device: %s", device)

    async def _on_alive(self, resource):
        if is_media_renderer(resource['NT']) or is_media_server(
                resource['NT']):
            device = await _create_device(self._factory, resource)
            if resource['USN'] not in self._av_devices:
                _logger.info("Found new device: %s %s", resource['Location'],
                             resource['NT'])

                self._av_devices[resource['USN']] = device
            else:
                # todo: update last_seen timestamp
                pass
        else:
            _logger.warning('Ignored: %s', resource['NT'])
            _logger.info('Known devices: %s', self._av_devices.keys())

    async def _on_byebye(self, resource):
        if resource['USN'] in self._av_devices:
            self._av_devices.pop(resource['USN'])
            _logger.info("ByeBye: %s: %s", resource['NT'], resource['USN'])

    async def _on_update(self, resource):
        _logger.info("Update: %s: %s", resource['NT'], resource['USN'])
