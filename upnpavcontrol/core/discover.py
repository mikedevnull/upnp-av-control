import logging
from .mediaserver import MediaServer
from .mediarenderer import MediaRenderer
import re
import async_upnp_client
import asyncio
import typing
from attr import attrs, attrib
from enum import Enum
import inspect
from dataclasses import dataclass

_logger = logging.getLogger(__name__)


class DiscoveryEventType(Enum):
    """
    Different type of upnp events that might occur
    """
    NEW_DEVICE = 'NEW_DEVICE'
    DEVICE_UPDATE = 'DEVICE_UPDATE'
    DEVICE_LOST = 'DEVICE_LOST'


@dataclass(frozen=True)
class DeviceDiscoveryEvent:
    """
    Provides all required information to handle discovery
    events in a uniform way.
    This includes advertisements via SSDP (alive, update, bybye) and
    but also responses to search requests.

    Attributes
    ----------
    event_type : DiscoveryEventType
        The type of discovery represented by this event
    device_type : str
        A UPnP device type descriptor of the form 'urn:schemas-upnp-org:device:{deviceType}:{ver}'
    udn : str
        UUID of the device
    location: str or None
        URL to the UPnP description of the device. Only available for `NEW_DEVICE` or `DEVICE_UPDATE`
        event types.
    """
    event_type: DiscoveryEventType
    device_type: str
    udn: str
    location: typing.Optional[str] = None


DiscoveryEventCallback = typing.Callable[[DiscoveryEventType, str], None]

_media_server_regex = re.compile(r'urn:schemas-upnp-org:device:MediaServer:[1-9]')
_media_renderer_regex = re.compile(r'urn:schemas-upnp-org:device:MediaRenderer:[1-9]')
_media_device_type_regex = re.compile(r'urn:schemas-upnp-org:device:Media(Server|Renderer):[1-9]')


def is_media_server(device_type: str) -> bool:
    """
    Check if the device type descriptor (e.g. from a Notification Type or Search Target)
    is a MediaServer.

    Parameters
    ----------
    device_type : str
        Descriptor, e.g. from an advertisement or search result

    Returns
    -------
    bool
        True if a MediaServer device, False otherwise
    """
    return _media_server_regex.match(device_type)


def is_media_renderer(device_type: str) -> bool:
    """
    Check if the device type descriptor (e.g. from a Notification Type or Search Target)
    is a MediaRenderer.

    Parameters
    ----------
    device_type : str
        Descriptor, e.g. from an advertisement or search result

    Returns
    -------
    bool
        True if a MediaRenderer device, False otherwise
    """
    return _media_renderer_regex.match(device_type)


def is_media_device(device_type: str) -> bool:
    """
    Check if the device type descriptor (e.g. from a Notification Type or Search Target)
    is either a MediaRenderer or MediaServer

    Parameters
    ----------
    device_type : str
        Descriptor, e.g. from an advertisement or search result

    Returns
    -------
    bool
        True if a MediaServer or MediaRenderer device, False otherwise
    """
    return _media_device_type_regex.match(device_type)


def udn_from_usn(usn: str, device_type: str):
    """
    Extract the device UUID from a Unique Service Name.

    This only works for USNs that describe devices include the device type, not services or root devices

    Parameters
    -----------
    usn : str
        Unique Service Name in the form 'uuid:{device-UUID}::rn:schemas-upnp-org:device:{deviceType}:{ver}'
    device_type : str
        Device type descriptor in the form 'urn:schemas-upnp-org:device:{deviceType}:{ver}'

    Returns
    -------
    str
        Device UUID
    """
    return usn.replace(f'::{device_type}', '')


@attrs
class DeviceEntry(object):
    device = attrib()
    device_type = attrib()
    expires_at = attrib(default=None)


async def _create_device_entry(factory, location):
    device = await factory.async_create_device(location)
    device_type = device._device_info.device_type
    if is_media_server(device_type):
        server = MediaServer(device)
        return DeviceEntry(device=server, device_type=device_type)
    elif is_media_renderer(device_type):
        renderer = MediaRenderer(device)
        return DeviceEntry(device=renderer, device_type=device_type)


async def async_scan(factory, timeout: int = 3):
    device_tasks = []
    devices = []

    # create_device_entry = functools.partial(_create_device_entry, factory)
    async def handle_discovery(description):
        description_url = description['Location']
        device_type = description['ST']
        device_udn = udn_from_usn(description['USN'], device_type)
        event = DeviceDiscoveryEvent(DiscoveryEventType.NEW_DEVICE, device_type, device_udn, description_url)

        _logger.debug('Got scan result %s at %s', device_type, description_url)
        # device_task = asyncio.create_task(create_device_entry(description_url))
        devices.append(event)
        # device_tasks.append(device_task)

    try:
        _logger.debug('Start scan for media renderers')
        renderer_search = asyncio.create_task(
            async_upnp_client.search.async_search(handle_discovery,
                                                  timeout=timeout,
                                                  service_type='urn:schemas-upnp-org:device:MediaRenderer:1'))

        _logger.debug('Start scan for media servers')
        server_search = asyncio.create_task(
            async_upnp_client.search.async_search(handle_discovery,
                                                  timeout=timeout,
                                                  service_type='urn:schemas-upnp-org:device:MediaServer:1'))

        await asyncio.gather(renderer_search, server_search)
        # devices = await asyncio.gather(*device_tasks)
        return devices
    except asyncio.CancelledError:
        _logger.debug('Device scan cancelled')
        for task in device_tasks:
            task.cancel()
        renderer_search.cancel()
        server_search.cancel()
        await asyncio.gather(renderer_search, server_search, return_exceptions=True)

    return []


class DeviceAdvertisementHandler(object):
    """
    Handles advertisement messages produced by a `async_upnp_client.UpnpAdvertisementListener`
    and transforms them into `DeviceDiscoveryEvents`.

    These discovery events are put into a queue so they can be processed
    by a consumer.
    """
    def __init__(self, event_queue: asyncio.Queue):
        """
        Constructor

        Parameters
        ----------
        event_queue : asyncio.Queue
            Target queue, will be used to push discovery events
        """
        self.queue = event_queue

    async def on_alive(self, resource: typing.Mapping[str, str]):
        device_type = resource['NT']
        if not is_media_device(device_type):
            return
        device_location = resource['Location']
        device_udn = udn_from_usn(resource['USN'], device_type)
        event = DeviceDiscoveryEvent(DiscoveryEventType.NEW_DEVICE, device_type, device_udn, device_location)
        await self.queue.put(event)

    async def on_byebye(self, resource: typing.Mapping[str, str]):
        device_type = resource['NT']
        if not is_media_device(device_type):
            return
        device_udn = udn_from_usn(resource['USN'], device_type)
        event = DeviceDiscoveryEvent(DiscoveryEventType.DEVICE_LOST, device_type, device_udn)
        await self.queue.put(event)

    async def on_update(self, resource: typing.Mapping[str, str]):
        device_type = resource['NT']
        if not is_media_device(device_type):
            return
        device_location = resource['Location']
        device_udn = udn_from_usn(resource['USN'], device_type)
        event = DeviceDiscoveryEvent(DiscoveryEventType.DEVICE_UPDATE, device_type, device_udn, device_location)
        await self.queue.put(event)


AdvertisementListenerCallback = typing.Callable[[typing.Mapping[str, str]], typing.Awaitable]
""" Type of the callbacks for `async_upnp_client.UpnpAdvertisementListener """

AdvertisementListenerFactory = typing.Callable[
    [AdvertisementListenerCallback, AdvertisementListenerCallback, AdvertisementListenerCallback],
    async_upnp_client.advertisement.UpnpAdvertisementListener]
""" Type of a factory to create an `async_upnp_client.UpnpAdvertisementListener` """

UpnpRequesterFactory = typing.Callable[[], async_upnp_client.UpnpRequester]
""" Factory function for implementations of `async_upnp_client.UpnpRequester` """


def create_aiohttp_requester() -> async_upnp_client.UpnpRequester:
    """ Default factory for `async_upnp_client.UpnpRequester` instances

    Returns
    -------
    async_upnp_client.AiohttpRequester
    """
    return async_upnp_client.aiohttp.AiohttpRequester()


def create_upnp_advertisement_listener(
        on_alive: AdvertisementListenerCallback, on_byebye: AdvertisementListenerCallback,
        on_update: AdvertisementListenerCallback) -> async_upnp_client.advertisement.UpnpAdvertisementListener:
    """
    Default factory to create `UpnpAdvertisementListener` instances
    """
    return async_upnp_client.advertisement.UpnpAdvertisementListener(on_alive=on_alive,
                                                                     on_byebye=on_byebye,
                                                                     on_update=on_update)


class DeviceRegistry(object):
    """
    Upnp device registry, main point that handles discovery of upnp av devices.

    The device registry will react on upnp advertisement messages.
    Furthermore, it will initiate a search request for upnp av devices on the network.
    This search can be repeated in regular intervals. This is optional, but has proven to be
    usefull in some cases where new upnp devices on the network don't advertise their presence on
    the network correctly.

    It's possible to access the current list of detected av devices.
    Additionally, clients can register a discovery event callback so they will be notified about
    new, updated or lost devices.

    This class uses `asyncio` and *must* be constructed from within a running event loop to function properly.
    `async_start()` must be called to start the actual discovery.
    `async_stop()` must be called to ensure all async operations are cleaned up properly.

    Notes
    -----
    Currently, only a single event callback can be registered at a given time.
    """
    def __init__(self,
                 advertisement_listener_factory: AdvertisementListenerFactory = create_upnp_advertisement_listener,
                 http_requester_factory: UpnpRequesterFactory = create_aiohttp_requester):
        """
        Constructor

        Parameters
        ----------
        advertisement_listener_factory : AdvertisementListenerFactory
            Factory function to define how the underlying advertisement listener should be created.
            This is mostly useful for testing or similar purposes, as other implementations can be injected.
        http_requester_factory : UpnpRequesterFactory
            Factory function to define how the underlying http requester used by the
            `async_upnp_client` framework should be created.
            This is mostly useful for testing or similar purposes, as other implementations can be injected.
        """
        self._event_queue = asyncio.Queue()
        self._advertisement_handler = DeviceAdvertisementHandler(self._event_queue)
        self._listener = advertisement_listener_factory(on_alive=self._advertisement_handler.on_alive,
                                                        on_byebye=self._advertisement_handler.on_byebye,
                                                        on_update=self._advertisement_handler.on_update)
        self._av_devices = {}
        self._factory = async_upnp_client.UpnpFactory(http_requester_factory())
        self._event_callback = None
        self._scan_task = None
        self._process_task = None

    @property
    def mediaservers(self) -> typing.Iterable[MediaServer]:
        """ Currently available av media servers """
        return [entity.device for entity in self._av_devices.values() if is_media_server(entity.device_type)]

    @property
    def mediarenderers(self) -> typing.Iterable[MediaRenderer]:
        """ Currently available av media renderers """
        return [entity.device for entity in self._av_devices.values() if is_media_renderer(entity.device_type)]

    def get_device(self, udn: str) -> typing.Union[MediaRenderer, MediaServer]:
        """
        Get an instance for a specific devices

        Parameters
        ----------
        udn : str
            UDN of the requested device

        Returns
        -------
        MediaRenderer or MediaServer instance

        Raises
        ------
        Raises an exception if no device with the given UDN is known to the registry
        """
        return self._av_devices[udn]

    def set_event_callback(self, callback: typing.Union[DeviceDiscoveryEvent, None]):
        """
        Set client callback to be notified about discovery events.
        If another callback has already been set it will be replaced.
        Use `None` as callback paremet to unset the event callback.

        The callback can be either a coroutine or a normal callable.

        The callback will receive the type of event (new, lost, update) and the UDN of
        the affected device.

        The DeviceRegistry itself has already been updated when this callback is triggered.
        """
        self._event_callback = callback

    async def async_start(self):
        """
        Start device registry operation, listen for advertisements and search for devices
        """
        _logger.info("Starting device registry")
        loop = asyncio.get_running_loop()
        self._scan_task = loop.create_task(self.scan())
        self._process_task = loop.create_task(self._consume_events())
        await self._listener.async_start()

    async def async_stop(self):
        """
        Stop device registry operation and cancel all pending tasks
        """
        _logger.debug("Begin device registry shutdown")
        self._scan_task.cancel()
        self._process_task.cancel()
        await self._listener.async_stop()
        await asyncio.gather(self._scan_task, self._process_task, return_exceptions=True)
        _logger.info("Device registry stopped")

    async def scan(self):
        _logger.info('Searching for AV devices')
        device_entries = await async_scan(self._factory)
        for entry in device_entries:
            _logger.info("Scan foundg device: %s", entry.location)
            await self._event_queue.put(entry)
            _logger.info('enqued')
            usn = entry.udn
            if usn not in self._av_devices:
                _logger.info("Scan found new device: %s", entry.location)
        if len(device_entries) > 0:
            await self._trigger_client_callback(DiscoveryEventType.NEW_DEVICE, usn)

    async def _consume_events(self):
        """
        Task that processes event queue entries.
        """
        while True:
            event = await self._event_queue.get()
            if event.event_type == DiscoveryEventType.NEW_DEVICE:
                if event.udn not in self._av_devices:
                    entry = await _create_device_entry(self._factory, event.location)
                    _logger.info("Found new device: %s", entry.device)
                    self._av_devices[event.udn] = entry
                    await self._trigger_client_callback(DiscoveryEventType.NEW_DEVICE, event.udn)
                else:
                    entry = self._av_devices[event.udn]
                    _logger.debug("Got a sign of life from: %s", entry.device)
                    # todo: update last_seen timestamp
            elif event.event_type == DiscoveryEventType.DEVICE_UPDATE:
                # TODO
                pass
            elif event.event_type == DiscoveryEventType.DEVICE_LOST:
                if event.udn in self._av_devices:
                    entry = self._av_devices.pop(event.udn)
                    _logger.info("ByeBye: %s", entry.device)
                    await self._trigger_client_callback(DiscoveryEventType.DEVICE_LOST, event.udn)
            self._event_queue.task_done()

    async def _trigger_client_callback(self, event, udn):
        """
        Invoke the client event callback, if set.
        """
        if self._event_callback:
            if inspect.iscoroutinefunction(self._event_callback):
                await self._event_callback(event, udn)
            else:
                self._event_callback(event, udn)
