import asyncio
from .utils import is_media_device, udn_from_usn
from .events import DeviceDiscoveryEvent, DiscoveryEventType
import typing
import async_upnp_client.advertisement

AdvertisementListenerCallback = typing.Callable[[typing.Mapping[str, str]], typing.Awaitable]
""" Type of the callbacks for `async_upnp_client.UpnpAdvertisementListener """

AdvertisementListenerFactory = typing.Callable[
    [AdvertisementListenerCallback, AdvertisementListenerCallback, AdvertisementListenerCallback],
    async_upnp_client.advertisement.UpnpAdvertisementListener]
""" Type of a factory to create an `async_upnp_client.UpnpAdvertisementListener` """


def create_upnp_advertisement_listener(
        on_alive: AdvertisementListenerCallback, on_byebye: AdvertisementListenerCallback,
        on_update: AdvertisementListenerCallback) -> async_upnp_client.advertisement.UpnpAdvertisementListener:
    """
    Default factory to create `UpnpAdvertisementListener` instances
    """
    return async_upnp_client.advertisement.UpnpAdvertisementListener(on_alive=on_alive,
                                                                     on_byebye=on_byebye,
                                                                     on_update=on_update)


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
