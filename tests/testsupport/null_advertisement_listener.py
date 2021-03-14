from upnpavcontrol.core.discovery.advertisement import AdvertisementListenerInterface
from upnpavcontrol.core.discovery.registry import MediaDeviceDiscoveryEvent
from upnpavcontrol.core.discovery.advertisement import _DeviceAdvertisementHandler


class NullAdvertisementListener(AdvertisementListenerInterface):
    """
    Does not actually listen to advertisement messages, instead provides
    methods to manually trigger discovery events for testing
    """
    def __init__(self, event_queue):
        self._handler = _DeviceAdvertisementHandler(event_queue)

    async def simulate(self, data):
        assert data['NTS'] in ('ssdp:alive', 'ssdp:update', 'ssdp:byebye')
        if data['NTS'] == 'ssdp:alive':
            await self._handler.on_alive(data)
        elif data['NTS'] == 'ssdp:update':
            await self._handler.on_update(data)
        elif data['NTS'] == 'ssdp:byebye':
            await self._handler.on_byebye(data)

    async def trigger_alive(self, data):
        await self._handler.on_alive(data)

    async def async_start(self):
        pass

    async def async_stop(self):
        pass
