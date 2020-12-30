from upnpavcontrol.core.discovery.registry import MediaDeviceType
from .discovery import DeviceRegistry, DeviceEntry, DiscoveryEventType
from .mediarenderer import MediaRenderer
from .mediaserver import MediaServer
from .notification_backend import NotificationBackend, AiohttpNotificationEndpoint
from async_upnp_client.aiohttp import AiohttpRequester
from async_upnp_client import UpnpFactory
from typing import Awaitable, Callable, Union, Optional, Dict, cast
import logging

MediaDevice = Union[MediaServer, MediaRenderer]
DiscoveryEventCallback = Callable[[DiscoveryEventType, MediaDevice], Awaitable]

_logger = logging.getLogger(__name__)


class AVControlPoint(object):
    def __init__(self, device_registry: DeviceRegistry = None, notifcation_backend=None):
        self._device_discovery_callback: Optional[DiscoveryEventCallback] = None
        self._renderers: Dict[str, MediaRenderer] = {}
        self._servers: Dict[str, MediaServer] = {}
        self._upnp_device_factory = UpnpFactory(AiohttpRequester())
        if device_registry is None:
            self._device_registry = DeviceRegistry()
        else:
            self._device_registry = device_registry
        self._device_registry.set_event_callback(self._handle_discovery_event)
        self._active_renderer = None
        if notifcation_backend is None:
            self._notify_receiver = NotificationBackend(AiohttpNotificationEndpoint(), AiohttpRequester())
        else:
            self._notify_receiver = notifcation_backend

    @property
    def mediaservers(self):
        return self._servers.values()

    def get_mediaserver_by_UDN(self, udn: str):
        return self._servers[udn]

    @property
    def mediarenderers(self):
        return self._renderers.values()

    def get_mediarenderer_by_UDN(self, udn: str):
        return self._renderers[udn]

    def set_discovery_event_callback(self, callback: Optional[DiscoveryEventCallback]):
        self._device_discovery_callback = callback

    async def async_start(self):
        await self._device_registry.async_start()
        await self._notify_receiver.async_start()

    async def async_stop(self):
        await self._device_registry.async_stop()
        await self._notify_receiver.async_stop()

    async def _handle_discovery_event(self, event_type: DiscoveryEventType, entry: DeviceEntry):
        try:
            if event_type == DiscoveryEventType.NEW_DEVICE:
                device = await self._create_device(entry)
                if entry.device_type == MediaDeviceType.MEDIASERVER:
                    self._servers[entry.udn] = cast(MediaServer, device)
                elif entry.device_type == MediaDeviceType.MEDIARENDERER:
                    self._renderers[entry.udn] = cast(MediaRenderer, device)
                if self._device_discovery_callback is not None:
                    await self._device_discovery_callback(DiscoveryEventType.NEW_DEVICE, device)
            elif event_type == DiscoveryEventType.DEVICE_LOST:
                if entry.device_type == MediaDeviceType.MEDIASERVER:
                    device = self._servers.pop(entry.udn)
                    await self._device_discovery_callback(DiscoveryEventType.DEVICE_LOST, device)
                elif entry.device_type == MediaDeviceType.MEDIARENDERER:
                    device = self._renderers.pop(entry.udn)
                    if self._device_discovery_callback is not None:
                        await self._device_discovery_callback(DiscoveryEventType.DEVICE_LOST, device)
        except Exception:
            _logger.exception('Failed to handle device discovery event')

    async def _create_device(self, entry: DeviceEntry) -> MediaDevice:
        raw_device = await self._upnp_device_factory.async_create_device(entry.location)
        if entry.device_type == MediaDeviceType.MEDIASERVER:
            return MediaServer(raw_device)
        elif entry.device_type == MediaDeviceType.MEDIARENDERER:
            return MediaRenderer(raw_device)
        raise RuntimeError('Cannot create device, is neither Renderer nor Server')
