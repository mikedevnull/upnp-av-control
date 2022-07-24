from .utils import udn_from_usn
from .events import DiscoveryEvent as SSDPEvent, DiscoveryEventType
from async_upnp_client.search import async_search
import asyncio
import logging

_logger = logging.getLogger(__name__)


async def scan_devices(event_queue: asyncio.Queue, device_type: str, timeout: int = 3):
    """
    Search for new UPnP (AV) devices of a given device type.

    Sends a search request to the network and waits until `timeout` for responses.
    Valid responses will be converted to DeviceDiscoverEvent events and pushed
    into the target event queue for another consumer.

    Parameters
    ---------
    event_queue : asyncio.Queue
        Target queue where events about found devices will be pushed.
    device_type : str
        UPnP device type descriptor that will be used as search target
    timeout : int
        Time in seconds that will be waited for av devices to respond
    """

    async def handle_discovery(description):
        description_url = description['Location']
        device_type = description['ST']
        device_udn = udn_from_usn(description['USN'], device_type)
        event = SSDPEvent(DiscoveryEventType.NEW_DEVICE, device_type, device_udn, description_url)

        _logger.debug('Got scan result %s at %s', device_type, description_url)
        await event_queue.put(event)
        _logger.debug('Sent scan result %s to queue', description_url)

    await async_search(handle_discovery, timeout=timeout, service_type=device_type)
