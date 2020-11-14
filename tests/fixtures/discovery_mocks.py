import os.path
from async_upnp_client import UpnpRequester
import asyncio
from upnpavcontrol.core.discovery import events
from upnpavcontrol.core.discovery.advertisement import AdvertisementListenerInterface


class TestingAdvertisementListener(AdvertisementListenerInterface):
    """
    Does not actually listen to advertisement messages, instead provides
    methods to manually trigger discovery events for testing
    """
    def __init__(self, event_queue):
        self._queue = event_queue

    async def async_start(self):
        pass

    async def async_stop(self):
        pass

    async def trigger_event_and_wait(self, event):
        await self._queue.put(event)
        # ensure the event has been processed
        await self._queue.join()
        return event

    async def trigger_renderer_alive(self):
        event = events.DeviceDiscoveryEvent(events.DiscoveryEventType.NEW_DEVICE,
                                            'urn:schemas-upnp-org:device:MediaRenderer:1',
                                            '13bf6358-00b8-101b-8000-74dfbfed7306', 'http://192.168.99.1:1234/dmr.xml')
        return await self.trigger_event_and_wait(event)

    async def trigger_renderer_byebye(self):
        event = events.DeviceDiscoveryEvent(events.DiscoveryEventType.DEVICE_LOST,
                                            'urn:schemas-upnp-org:device:MediaRenderer:1',
                                            '13bf6358-00b8-101b-8000-74dfbfed7306', 'http://192.168.99.1:1234/dmr.xml')
        return await self.trigger_event_and_wait(event)

    async def trigger_server_alive(self):
        event = events.DeviceDiscoveryEvent(events.DiscoveryEventType.NEW_DEVICE,
                                            'urn:schemas-upnp-org:device:MediaServer:1',
                                            'f5b1b596-c1d2-11e9-af8b-705681aa5dfd',
                                            'http://192.168.99.2:9200/plugins/MediaServer.xml')
        return await self.trigger_event_and_wait(event)

    async def trigger_server_byebye(self):
        event = events.DeviceDiscoveryEvent(events.DiscoveryEventType.DEVICE_LOST,
                                            'urn:schemas-upnp-org:device:MediaServer:1',
                                            'f5b1b596-c1d2-11e9-af8b-705681aa5dfd',
                                            'http://192.168.99.2:9200/plugins/MediaServer.xml')
        return await self.trigger_event_and_wait(event)

    async def trigger_printer_alive(self):
        event = events.DeviceDiscoveryEvent(events.DiscoveryEventType.NEW_DEVICE,
                                            'urn:schemas-upnp-org:device:printer:1',
                                            '92b65aa0-c1dc-11e9-8a7b-705681aa5dfd',
                                            'http://192.168.99.3:1234/device.xml')
        return await self.trigger_event_and_wait(event)

    async def trigger_printer_byebye(self):
        event = events.DeviceDiscoveryEvent(events.DiscoveryEventType.DEVICE_LOST,
                                            'urn:schemas-upnp-org:device:printer:1',
                                            '92b65aa0-c1dc-11e9-8a7b-705681aa5dfd',
                                            'http://192.168.99.3:1234/device.xml')
        return await self.trigger_event_and_wait(event)


def _read_data_file(filename):
    filepath = os.path.join('tests', 'data', filename)
    with open(filepath, 'r') as handle:
        return handle.read()


class UpnpTestRequester(UpnpRequester):
    def __init__(self, response_map):
        self._response_map = response_map

    async def async_do_http_request(self, method, url, headers=None, body=None, body_type='text'):

        key = (method, url)
        if key not in self._response_map:
            raise asyncio.TimeoutError('Unkown resource for request: %s' % str(key))

        return self._response_map[key]


_RESPONSES = {
    ('GET', 'http://192.168.99.1:1234/dmr.xml'): (200, {}, _read_data_file('dmr_99_1.xml')),
    ('GET', 'http://192.168.99.1:1234/dmr_rcs.xml'): (200, {}, _read_data_file('dmr_rcs_99_1.xml')),
    ('GET', 'http://192.168.99.1:1234/dmr_cms.xml'): (200, {}, _read_data_file('dmr_cms_99_1.xml')),
    ('GET', 'http://192.168.99.1:1234/dmr_avts.xml'): (200, {}, _read_data_file('dmr_avts_99_1.xml')),
    ('GET', 'http://192.168.99.2:9200/plugins/MediaServer.xml'): (200, {}, _read_data_file('dms_99_2.xml')),
    ('GET', 'http://192.168.99.2:9200/plugins/UPnP/MediaServer/ContentDirectory.xml'):  # noqa: E501
    (200, {}, _read_data_file('dms_cds_99_2.xml')),
    ('GET', 'http://192.168.99.2:9200/plugins/UPnP/MediaServer/ConnectionManager.xml'):  # noqa: E501
    (200, {}, _read_data_file('dms_cms_99_2.xml')),
    ('GET', 'http://192.168.99.2:9200/plugins/UPnP/MediaServer/MediaReceiverRegistrar.xml'):  # noqa: E501
    (200, {}, _read_data_file('dms_mrrs_99_2.xml'))
}


def create_test_requester():
    return UpnpTestRequester(_RESPONSES)
