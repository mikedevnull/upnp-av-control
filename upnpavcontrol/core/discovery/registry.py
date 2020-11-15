import logging
from .utils import is_media_renderer, is_media_server
from .advertisement import AdvertisementListener, AdvertisementListenerInterface
from .scan import scan_devices
from dataclasses import dataclass
import asyncio
import typing
from .events import SSDPEvent, DiscoveryEventType
import datetime
from enum import Enum

_logger = logging.getLogger(__name__)


class MediaDeviceType(Enum):
    MEDIASERVER = 'MediaServer'
    MEDIARENDERER = 'MediaRenderer'


@dataclass
class DeviceEntry(object):
    location: str
    udn: str
    device_type: MediaDeviceType
    expires_at: typing.Optional[datetime.datetime] = None


RegistryEventCallback = typing.Callable[[DiscoveryEventType, DeviceEntry], typing.Awaitable]


def _device_entry_from_event(event: SSDPEvent) -> typing.Optional[DeviceEntry]:
    if event.location is None:
        return None
    if is_media_server(event.device_type):
        media_device_type = MediaDeviceType.MEDIASERVER
    elif is_media_renderer(event.device_type):
        media_device_type = MediaDeviceType.MEDIARENDERER
    else:
        return None
    return DeviceEntry(location=event.location, udn=event.udn, device_type=media_device_type)


# async def _create_device_entry(factory: async_upnp_client.UpnpFactory, location: str) -> typing.Optional[DeviceEntry]:
#     """
#     Creates a AV device instance by downloading and processing the device description.

#     Parameters
#     ----------
#     factory : async_upnp_client.UpnpFactory
#         Factory instance used to create the low-level async_upnp_client instance.
#     location : str
#         URL where the device description can be downloaded

#     Returns
#     -------
#     MediaServer, MediaRenderer
#         A renderer or server instance on success or None otherwise.
#     """
#     raw_device = await factory.async_create_device(location)
#     raw_device_type = raw_device._device_info.device_type
#     if is_media_server(raw_device_type):
#         return DeviceEntry(raw_device=raw_device, device_type=MediaDeviceType.MEDIASERVER)
#     elif is_media_renderer(raw_device_type):
#         return DeviceEntry(raw_device=raw_device, device_type=MediaDeviceType.MEDIARENDERER)


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
    def __init__(self, advertisement_listener: typing.Type[AdvertisementListenerInterface] = None):
        """
        Constructor

        Parameters
        ----------
        advertisement_listener : AdvertisementListenerBase
            Implementation of an advertisement listener.
            This is mostly useful for testing or similar purposes, as other implementations can be injected.
        upnp_requester : async_upnp_client.UpnpRequester
            Instance of an UpnpRequester that will be used to issue http requests.
            If `None`, a default `async_upnp_client.aiohttp.AiohttpRequester` will be created.
            This is mostly useful for testing or similar purposes, as other implementations can be injected.
        """
        self._event_queue = asyncio.Queue()
        if advertisement_listener is None:
            self._listener = AdvertisementListener(self._event_queue)
        else:
            self._listener = advertisement_listener(self._event_queue)
        self._av_devices: typing.Dict[str, DeviceEntry] = {}
        self._event_callback: typing.Optional[RegistryEventCallback] = None
        self._scan_task: typing.Optional[asyncio.Task] = None
        self._process_task: typing.Optional[asyncio.Task] = None

    def get_device_entry(self, udn: str) -> DeviceEntry:
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

    @property
    def devices(self):
        return self._av_devices

    def set_event_callback(self, callback: typing.Optional[RegistryEventCallback]):
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
        self._scan_task = loop.create_task(self._periodic_scan())
        self._process_task = loop.create_task(self._consume_events())
        await self._listener.async_start()

    async def async_stop(self):
        """
        Stop device registry operation and cancel all pending tasks
        """
        _logger.debug("Begin device registry shutdown")
        running_tasks = []
        if self._scan_task is not None:
            running_tasks.append(self._scan_task)
            self._scan_task.cancel()
        if self._process_task is not None:
            running_tasks.append(self._process_task)
            self._process_task.cancel()
        await self._listener.async_stop()
        await asyncio.gather(*running_tasks, return_exceptions=True)
        _logger.info("Device registry stopped")

    async def _periodic_scan(self):
        try:
            while True:
                await self._scan()
                await asyncio.sleep(5 * 60)  # repeat every 5 minutes
        except asyncio.CancelledError:
            logging.debug('Searching for AV devices cancelled')
            return
        except Exception:
            logging.exception('Searching for AV devices failed')
            raise

    async def _scan(self):
        server_scan: typing.Optional[asyncio.Task] = None
        renderer_scan: typing.Optional[asyncio.Task] = None
        try:
            _logger.debug('Searching for AV devices')
            server_scan = asyncio.create_task(
                scan_devices(self._event_queue, 'urn:schemas-upnp-org:device:MediaServer:1'))
            renderer_scan = asyncio.create_task(
                scan_devices(self._event_queue, 'urn:schemas-upnp-org:device:MediaRenderer:1'))
            await asyncio.gather(server_scan, renderer_scan)
        except Exception:
            running_tasks = []
            if server_scan is not None:
                running_tasks.append(server_scan)
                server_scan.cancel()
            if renderer_scan is not None:
                running_tasks.append(renderer_scan)
                renderer_scan.cancel()
            if server_scan is not None and renderer_scan is not None:
                await asyncio.gather(*running_tasks, return_exceptions=True)
            raise

    async def _consume_events(self):
        """
        Task that processes event queue entries.
        """
        running = True
        while running:
            event: typing.Optional[SSDPEvent] = None
            try:
                event = await self._event_queue.get()
                if event is None:
                    break
                if event.event_type == DiscoveryEventType.NEW_DEVICE:
                    if event.udn not in self._av_devices:
                        entry = _device_entry_from_event(event)
                        if entry is not None:
                            _logger.info("Found new device: %s", entry.udn)
                            self._av_devices[event.udn] = entry
                            await self._trigger_client_callback(DiscoveryEventType.NEW_DEVICE, entry)
                    else:
                        entry = self._av_devices[event.udn]
                        _logger.debug("Got a sign of life from: %s", entry.udn)
                        # todo: update last_seen timestamp
                elif event.event_type == DiscoveryEventType.DEVICE_UPDATE:
                    # TODO
                    pass
                elif event.event_type == DiscoveryEventType.DEVICE_LOST:
                    if event.udn in self._av_devices:
                        entry = self._av_devices.pop(event.udn)
                        _logger.info("ByeBye: %s", entry.udn)
                        await self._trigger_client_callback(DiscoveryEventType.DEVICE_LOST, entry)
                self._event_queue.task_done()
            except RuntimeError:
                logging.exception('Failed to process discovery event %s', event)
            except asyncio.CancelledError:
                logging.debug('Discovery event processing cancelled')
                running = False
            except Exception:
                logging.exception('Failed to process discovery events, shutting down')
                raise
        _logger.debug('Discovery event processing stopped')

    async def _trigger_client_callback(self, event_type: DiscoveryEventType, entry: DeviceEntry):
        """
        Invoke the client event callback, if set.
        """
        if self._event_callback is not None:
            await self._event_callback(event_type, entry)
