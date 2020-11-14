import asyncio
from .utils import is_media_device, udn_from_usn
from .events import DeviceDiscoveryEvent, DiscoveryEventType
from abc import ABC, abstractmethod
import typing
from async_upnp_client.advertisement import UpnpAdvertisementListener


class AdvertisementListenerInterface(ABC):
    """
    Abstract base class for implementations that listen for UPnP advertisements.

    Implementations must receive and parse SSDP notifications for Mediarenderers and
    Mediaservers, convert them to discoverey events and push them to the given event queue.
    """
    @abstractmethod
    def __init__(self, event_queue: asyncio.Queue):
        """
        Parameters
        ----------
        event_queue: asyncio.Queue
            Target event queue. Received discovery events should be put there.
        """

    async def async_start(self):
        """
        Start async receiving/reacting to SSDP notifications for media devices.
        """
        pass

    async def async_stop(self):
        """
        Stop receiving SSDP notifications for media devices.
        """
        pass


class AdvertisementListener(AdvertisementListenerInterface):
    def __init__(self, event_queue: asyncio.Queue):
        self._handler = _DeviceAdvertisementHandler(event_queue)
        self._listener = UpnpAdvertisementListener(on_alive=self._handler.on_alive,
                                                   on_byebye=self._handler.on_byebye,
                                                   on_update=self._handler.on_update)

    async def async_start(self):
        await self._listener.async_start()

    async def async_stop(self):
        await self._listener.async_stop()


class _DeviceAdvertisementHandler(object):
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
