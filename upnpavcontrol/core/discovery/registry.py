import logging
from ..mediaserver import MediaServer
from ..mediarenderer import MediaRenderer
from .utils import is_media_server, is_media_renderer
from .advertisement import AdvertisementListenerFactory, create_upnp_advertisement_listener, DeviceAdvertisementHandler
from .scan import scan_devices
import async_upnp_client
import async_upnp_client.advertisement
import async_upnp_client.aiohttp
from dataclasses import dataclass
import asyncio
import typing
from .events import DiscoveryEventType
import inspect
import datetime

_logger = logging.getLogger(__name__)

DiscoveryEventCallback = typing.Callable[[DiscoveryEventType, str], None]


@dataclass
class DeviceEntry(object):
    device: async_upnp_client.UpnpDevice
    device_type: str
    expires_at: typing.Optional[datetime.datetime] = None


async def _create_device_entry(factory: async_upnp_client.UpnpFactory,
                               location: str) -> typing.Union[MediaServer, MediaRenderer, None]:
    """
    Creates a AV device instance by downloading and processing the device description.

    Parameters
    ----------
    factory : async_upnp_client.UpnpFactory
        Factory instance used to create the low-level async_upnp_client instance.
    location : str
        URL where the device description can be downloaded

    Returns
    -------
    MediaServer, MediaRenderer
        A renderer or server instance on success or None otherwise.
    """
    device = await factory.async_create_device(location)
    device_type = device._device_info.device_type
    if is_media_server(device_type):
        server = MediaServer(device)
        return DeviceEntry(device=server, device_type=device_type)
    elif is_media_renderer(device_type):
        renderer = MediaRenderer(device)
        return DeviceEntry(device=renderer, device_type=device_type)


UpnpRequesterFactory = typing.Callable[[], async_upnp_client.UpnpRequester]
""" Factory function for implementations of `async_upnp_client.UpnpRequester` """


def create_aiohttp_requester() -> async_upnp_client.UpnpRequester:
    """ Default factory for `async_upnp_client.UpnpRequester` instances

    Returns
    -------
    async_upnp_client.AiohttpRequester
    """
    return async_upnp_client.aiohttp.AiohttpRequester()


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

    def set_event_callback(self, callback: typing.Union[DiscoveryEventCallback, None]):
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
        self._scan_task.cancel()
        self._process_task.cancel()
        await self._listener.async_stop()
        await asyncio.gather(self._scan_task, self._process_task, return_exceptions=True)
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
        try:
            _logger.debug('Searching for AV devices')
            server_scan = asyncio.create_task(
                scan_devices(self._event_queue, 'urn:schemas-upnp-org:device:MediaServer:1'))
            renderer_scan = asyncio.create_task(
                scan_devices(self._event_queue, 'urn:schemas-upnp-org:device:MediaRenderer:1'))
            await asyncio.gather(server_scan, renderer_scan)
        except Exception:
            server_scan.cancel()
            renderer_scan.cancel()
            await asyncio.gather(server_scan, renderer_scan, return_exceptions=True)
            raise

    async def _consume_events(self):
        """
        Task that processes event queue entries.
        """
        running = True
        while running:
            try:
                event = await self._event_queue.get()
                if event.event_type == DiscoveryEventType.NEW_DEVICE:
                    if event.udn not in self._av_devices:
                        entry = await _create_device_entry(self._factory, event.location)
                        if entry is not None:
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
            except RuntimeError:
                logging.exception('Failed to process discovery event %s', event)
            except asyncio.CancelledError:
                logging.debug('Discovery event processing cancelled')
                running = False
            except Exception:
                logging.exception('Failed to process discovery events, shutting down')
                raise
        _logger.debug('Discovery event processing stopped')

    async def _trigger_client_callback(self, event, udn):
        """
        Invoke the client event callback, if set.
        """
        if self._event_callback:
            if inspect.iscoroutinefunction(self._event_callback):
                await self._event_callback(event, udn)
            else:
                self._event_callback(event, udn)
