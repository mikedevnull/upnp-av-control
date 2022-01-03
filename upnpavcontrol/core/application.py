from upnpavcontrol.core.discovery import MediaDeviceDiscoveryEvent
from upnpavcontrol.core.discovery.registry import MediaDeviceType
from .discovery import DeviceRegistry, DeviceEntry, DiscoveryEventType
from .mediarenderer import create_media_renderer, MediaRenderer
from .mediaserver import MediaServer
from .playback.controller import PlaybackController
from .playback.utils import PlaybackControllableWrapper
from .notification_backend import NotificationBackend, AiohttpNotificationEndpoint
from async_upnp_client.aiohttp import AiohttpRequester
from async_upnp_client import UpnpFactory, UpnpDevice
from typing import Awaitable, Callable, Union, Dict, cast
from .oberserver import Observable
from .typing_compat import Protocol
import logging

MediaDevice = Union[MediaServer, MediaRenderer]
DiscoveryEventCallback = Callable[[DiscoveryEventType, MediaDevice], Awaitable]

_logger = logging.getLogger(__name__)


class UpnpDeviceFactory(Protocol):
    async def async_create_device(self, location: str) -> UpnpDevice:
        pass


class AVControlPoint(object):
    def __init__(self,
                 device_registry: DeviceRegistry = None,
                 notifcation_backend=None,
                 device_factory: UpnpDeviceFactory = None):
        self._device_discover_observer = Observable[MediaDeviceDiscoveryEvent]()
        self._renderers: Dict[str, MediaRenderer] = {}
        self._servers: Dict[str, MediaServer] = {}
        self._playback_controller: Dict[str, PlaybackController] = {}
        if device_factory is None:
            self._upnp_device_factory = UpnpFactory(AiohttpRequester())
        else:
            self._upnp_device_factory = device_factory
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

    def get_mediaserver_by_UDN(self, udn: str) -> MediaServer:
        return self._servers[udn]

    @property
    def mediarenderers(self):
        return self._renderers.values()

    def get_mediarenderer_by_UDN(self, udn: str) -> MediaRenderer:
        return self._renderers[udn]

    def get_controller_for_renderer(self, udn: str) -> PlaybackController:
        return self._playback_controller[udn]

    def on_device_discovery_event(self, callback: Callable[[MediaDeviceDiscoveryEvent], Awaitable[None]]):
        return self._device_discover_observer.subscribe(callback)

    async def async_start(self):
        await self._device_registry.async_start()
        await self._notify_receiver.async_start()

    async def async_stop(self):
        await self._device_registry.async_stop()
        await self._notify_receiver.async_stop()

    async def _handle_discovery_event(self, event_type: DiscoveryEventType, entry: DeviceEntry):
        try:
            event = MediaDeviceDiscoveryEvent(event_type=event_type, device_type=entry.device_type, udn=entry.udn)
            if event_type == DiscoveryEventType.NEW_DEVICE:
                device = await self._create_device(entry)
                if entry.device_type == MediaDeviceType.MEDIASERVER:
                    self._add_new_server(entry.udn, cast(MediaServer, device))
                elif entry.device_type == MediaDeviceType.MEDIARENDERER:
                    await self._add_new_renderer(entry.udn, cast(MediaRenderer, device))
                await self._notify_discovery(event)
            elif event_type == DiscoveryEventType.DEVICE_LOST:
                if entry.device_type == MediaDeviceType.MEDIASERVER:
                    self._remove_lost_server(entry.udn)
                elif entry.device_type == MediaDeviceType.MEDIARENDERER:
                    self._remove_lost_renderer(entry.udn)
                await self._notify_discovery(event)
        except Exception:
            _logger.exception('Failed to handle device discovery event')

    async def _notify_discovery(self, event: MediaDeviceDiscoveryEvent):
        await self._device_discover_observer.notify(event)

    async def _create_device(self, entry: DeviceEntry) -> MediaDevice:
        _logger.debug('Loading device description from %s', entry.location)
        raw_device = await self._upnp_device_factory.async_create_device(entry.location)
        if entry.device_type == MediaDeviceType.MEDIASERVER:
            return MediaServer(raw_device)
        elif entry.device_type == MediaDeviceType.MEDIARENDERER:
            return await create_media_renderer(raw_device, self._notify_receiver)
        raise RuntimeError('Cannot create device, is neither Renderer nor Server')

    async def _add_new_renderer(self, udn: str, device: MediaRenderer):
        self._renderers[udn] = device
        self._playback_controller[udn] = PlaybackController()
        wrapped_device = PlaybackControllableWrapper(device, self.get_mediaserver_by_UDN)
        await self._playback_controller[udn].setup_player(wrapped_device)

    def _remove_lost_renderer(self, udn: str):
        self._renderers.pop(udn)
        self._playback_controller.pop(udn)

    def _add_new_server(self, udn: str, device: MediaServer):
        self._servers[udn] = device

    def _remove_lost_server(self, udn: str):
        self._servers.pop(udn)
