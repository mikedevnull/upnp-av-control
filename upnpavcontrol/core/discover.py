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
from attr import attrs, attrib
from enum import Enum


class DiscoveryEventType(Enum):
    NEW_DEVICE = 0
    DEVICE_UPDATE = 1
    DEVICE_LOST = 2


_logger = logging.getLogger(__name__)

media_server_regex = re.compile(
    r'urn:schemas-upnp-org:device:MediaServer:[1-9]')
media_renderer_regex = re.compile(
    r'urn:schemas-upnp-org:device:MediaRenderer:[1-9]')


def is_media_server(service_type):
    return media_server_regex.match(service_type)


def is_media_renderer(service_type):
    return media_renderer_regex.match(service_type)


def udn_from_usn(usn, device_type):
    return usn.replace(f'::{device_type}', '')


@attrs
class DeviceEntry(object):
    device = attrib()
    device_type = attrib()
    expires_at = attrib(default=None)


async def quick_scan(timeout: int = 3):
    factory = async_upnp_client.UpnpFactory(AiohttpRequester())
    return await async_scan(factory, timeout)


async def _create_device_entry(factory, location, device_type):
    device = await factory.async_create_device(location)
    if media_server_regex.match(device_type):
        server = MediaServer(device)
        return DeviceEntry(device=server, device_type=device_type)
    elif media_renderer_regex.match(device_type):
        renderer = MediaRenderer(device)
        return DeviceEntry(device=renderer, device_type=device_type)


async def async_scan(factory, timeout: int = 3):
    device_tasks = []
    create_device_entry = functools.partial(_create_device_entry, factory)

    async def handle_discovery(description):
        description_url = description['Location']
        device_type = description['ST']
        _logger.debug('Got scan result %s at %s', device_type, description_url)
        device_task = asyncio.create_task(
            create_device_entry(description_url, device_type))
        device_tasks.append(device_task)

    _logger.debug('Start scan for media renderers')
    renderer_search = async_search(
        handle_discovery,
        timeout=timeout,
        service_type='urn:schemas-upnp-org:device:MediaRenderer:1')

    _logger.debug('Start scan for media servers')
    server_search = async_search(
        handle_discovery,
        timeout=timeout,
        service_type='urn:schemas-upnp-org:device:MediaServer:1')

    await asyncio.wait([renderer_search, server_search])
    devices = await asyncio.gather(*device_tasks)

    return devices


def create_aiohttp_requester():
    return AiohttpRequester()


def create_upnp_advertisement_listener(on_alive, on_byebye, on_update):
    return UpnpAdvertisementListener(on_alive=on_alive,
                                     on_byebye=on_byebye,
                                     on_update=on_update)


class DeviceRegistry(object):
    def __init__(
        self,
        create_advertisement_listener=create_upnp_advertisement_listener,
        create_requester=create_aiohttp_requester):
        self._listener = create_advertisement_listener(
            on_alive=self._on_alive,
            on_byebye=self._on_byebye,
            on_update=self._on_update)
        self._av_devices = {}
        self._factory = async_upnp_client.UpnpFactory(create_requester())
        self._event_callback = None

    @property
    def mediaservers(self):
        return [
            entity.device for entity in self._av_devices.values()
            if is_media_server(entity.device_type)
        ]

    @property
    def mediarenderers(self):
        return [
            entity.device for entity in self._av_devices.values()
            if is_media_renderer(entity.device_type)
        ]

    def get_device(self, udn: str):
        return self._av_devices[udn]

    def set_event_callback(self, callback):
        self._event_callback = callback

    async def start(self):
        _logger.info("Starting device registry")
        loop = asyncio.get_running_loop()
        loop.create_task(self.scan())
        loop.create_task(self._listener.async_start())

    async def scan(self):
        _logger.info('Searching for AV devices')
        device_entries = await async_scan(self._factory)
        for entry in device_entries:
            usn = entry.device.udn
            if usn not in self._av_devices:
                self._av_devices[usn] = entry
                _logger.info("Scan found new device: %s", entry.device)
        if len(device_entries) > 0:
            self._notify_on_update(DiscoveryEventType.NEW_DEVICE, usn)

    async def _on_alive(self, resource):
        device_type = resource['NT']
        device_location = resource['Location']
        device_udn = resource['USN'].replace('::%s' % device_type, '')
        if is_media_renderer(device_type) or is_media_server(device_type):
            if device_udn not in self._av_devices:

                entry = await _create_device_entry(self._factory,
                                                   device_location,
                                                   device_type)
                _logger.info("New device sent alive message: %s", entry.device)
                self._av_devices[device_udn] = entry
                self._notify_on_update(DiscoveryEventType.NEW_DEVICE,
                                       device_udn)
            else:
                entry = self._av_devices[device_udn]
                _logger.debug("Got a sign of life from: %s", entry.device)
                # todo: update last_seen timestamp
                pass
        else:
            _logger.debug('Ignored: %s (type not of interest)', device_type)

    async def _on_byebye(self, resource):
        device_type = resource['NT']
        device_udn = udn_from_usn(resource['USN'], device_type)
        if device_udn in self._av_devices:
            entry = self._av_devices.pop(device_udn)
            _logger.info("ByeBye: %s", entry.device)
            self._notify_on_update(DiscoveryEventType.DEVICE_LOST, device_udn)

    async def _on_update(self, resource):
        _logger.info("Update: %s: %s", resource['NT'], resource['USN'])

    def _notify_on_update(self, event, udn):
        if self._event_callback:
            self._event_callback(event, udn)
