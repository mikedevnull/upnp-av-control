from upnpavcontrol.core.discovery import MediaDeviceDiscoveryEvent, MediaDeviceType
from .discovery import create_discovery_event_observable, DiscoveryEvent
from .discovery.events import filter_lost_device_events, filter_mediarenderer_events
from .discovery.events import filter_mediaserver_events, filter_new_device_events
from .mediarenderer import create_media_renderer, MediaRenderer
from .mediaserver import MediaServer
from .playback.controller import PlaybackController
from .playback.utils import PlaybackControllableWrapper
from .notification_backend import NotificationBackend, AiohttpNotificationEndpoint
from async_upnp_client.aiohttp import AiohttpRequester
from async_upnp_client.client_factory import UpnpFactory, UpnpDevice
from typing import Awaitable, Callable, Union, Dict, Optional
from .oberserver import Observable
from .typing_compat import Protocol
import logging
import reactivex as rx
import asyncio

_logger = logging.getLogger(__name__)

MediaDevice = Union[MediaServer, MediaRenderer]


def _wrap_async(c):

    def f(*args, **kwargs):
        return asyncio.get_running_loop().create_task(c(*args, **kwargs))

    return f


class UpnpDeviceFactory(Protocol):

    async def async_create_device(self, location: str) -> UpnpDevice:
        pass


class AVControlPoint(object):

    def __init__(self,
                 device_discovery_events: Optional[rx.Observable] = None,
                 notifcation_backend=None,
                 device_factory: UpnpDeviceFactory = None):
        self._device_discover_observer = Observable[MediaDeviceDiscoveryEvent]()
        self._renderers: Dict[str, MediaRenderer] = {}
        self._servers: Dict[str, MediaServer] = {}
        self._playback_controller: Dict[str, PlaybackController] = {}
        if device_factory is None:
            self._upnp_device_factory = UpnpFactory(AiohttpRequester())
        else:
            self._upnp_device_factory = device_factory or UpnpFactory(AiohttpRequester())
        self._setup_discovery(device_discovery_events)

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
        _logger.debug("Start Control Point core")
        self._discovery_subscription = self._device_discovery_events.connect()
        await self._notify_receiver.async_start()

    async def async_stop(self):
        self._discovery_subscription.dispose()
        self._discovery_subscription = None
        await self._notify_receiver.async_stop()

    async def _notify_discovery(self, event: MediaDeviceDiscoveryEvent):
        await self._device_discover_observer.notify(event)

    async def _add_renderer(self, event: DiscoveryEvent):
        _logger.debug("Loading renderer description from %s", event.location)
        raw_device = await self._upnp_device_factory.async_create_device(event.location)
        renderer = await create_media_renderer(raw_device, self._notify_receiver)
        self._renderers[event.udn] = renderer
        self._playback_controller[event.udn] = PlaybackController()
        wrapped_device = PlaybackControllableWrapper(renderer, self.get_mediaserver_by_UDN)
        await self._playback_controller[event.udn].setup_player(wrapped_device)
        _logger.info("New renderer %s [%s]", renderer.friendly_name, renderer.udn)
        forward_event = MediaDeviceDiscoveryEvent(event_type=event.event_type,
                                                  device_type=MediaDeviceType.MEDIARENDERER,
                                                  udn=event.udn,
                                                  friendly_name=renderer.friendly_name)
        await self._notify_discovery(forward_event)

    async def _remove_renderer(self, event: DiscoveryEvent):
        if event.udn not in self._renderers:
            return
        renderer = self._renderers.pop(event.udn)
        self._playback_controller.pop(event.udn)
        _logger.info("Renderer gone %s [%s]", renderer.friendly_name, renderer.udn)
        forward_event = MediaDeviceDiscoveryEvent(event_type=event.event_type,
                                                  device_type=MediaDeviceType.MEDIARENDERER,
                                                  udn=event.udn,
                                                  friendly_name=renderer.friendly_name)
        await self._notify_discovery(forward_event)

    async def _add_server(self, event: DiscoveryEvent):
        _logger.debug("Loading server description from: %s", event.location)
        raw_device = await self._upnp_device_factory.async_create_device(event.location)
        server = MediaServer(raw_device)
        self._servers[event.udn] = MediaServer(raw_device)
        _logger.info("New server %s [%s]", server.friendly_name, server.udn)
        forward_event = MediaDeviceDiscoveryEvent(event_type=event.event_type,
                                                  device_type=MediaDeviceType.MEDIASERVER,
                                                  udn=event.udn,
                                                  friendly_name=server.friendly_name)
        await self._notify_discovery(forward_event)

    async def _remove_server(self, event: DiscoveryEvent):
        if event.udn not in self._servers:
            return
        server = self._servers.pop(event.udn)
        _logger.info("Server gone %s [%s]", server.friendly_name, server.udn)
        forward_event = MediaDeviceDiscoveryEvent(event_type=event.event_type,
                                                  device_type=MediaDeviceType.MEDIASERVER,
                                                  udn=event.udn,
                                                  friendly_name=server.friendly_name)
        await self._notify_discovery(forward_event)

    def _setup_discovery(self, device_discovery_events: Optional[rx.Observable[DiscoveryEvent]] = None):
        o = device_discovery_events or create_discovery_event_observable()
        self._device_discovery_events = o.pipe(rx.operators.publish())
        self._discovery_subscription = None
        scheduler = rx.scheduler.eventloop.AsyncIOScheduler(loop=asyncio.get_running_loop())

        self._device_discovery_events.pipe(filter_new_device_events(),
                                           filter_mediarenderer_events()).subscribe(_wrap_async(self._add_renderer),
                                                                                    scheduler=scheduler)
        self._device_discovery_events.pipe(filter_new_device_events(),
                                           filter_mediaserver_events()).subscribe(_wrap_async(self._add_server),
                                                                                  scheduler=scheduler)
        self._device_discovery_events.pipe(filter_lost_device_events()).subscribe(_wrap_async(self._remove_renderer),
                                                                                  scheduler=scheduler)
        self._device_discovery_events.pipe(filter_lost_device_events(),
                                           filter_mediaserver_events()).subscribe(_wrap_async(self._remove_server),
                                                                                  scheduler=scheduler)
