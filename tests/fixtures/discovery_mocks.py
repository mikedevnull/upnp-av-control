import os.path
import asyncio
from upnpavcontrol.core.discovery.advertisement import AdvertisementListenerInterface


class TestingAdvertisementListener(AdvertisementListenerInterface):
    """
    Does not actually listen to advertisement messages, instead provides
    methods to manually trigger discovery events for testing
    """
    def __init__(self, event_queue):
        pass

    async def async_start(self):
        pass

    async def async_stop(self):
        pass


# _RESPONSES = {
#     ('GET', 'http://192.168.99.1:1234/dmr.xml'): (200, {}, _read_data_file('dmr_99_1.xml')),
#     ('GET', 'http://192.168.99.1:1234/dmr_rcs.xml'): (200, {}, _read_data_file('dmr_rcs_99_1.xml')),
#     ('GET', 'http://192.168.99.1:1234/dmr_cms.xml'): (200, {}, _read_data_file('dmr_cms_99_1.xml')),
#     ('GET', 'http://192.168.99.1:1234/dmr_avts.xml'): (200, {}, _read_data_file('dmr_avts_99_1.xml')),
#     ('GET', 'http://192.168.99.2:9200/plugins/MediaServer.xml'): (200, {}, _read_data_file('dms_99_2.xml')),
#     ('GET', 'http://192.168.99.2:9200/plugins/UPnP/MediaServer/ContentDirectory.xml'):  # noqa: E501
#     (200, {}, _read_data_file('dms_cds_99_2.xml')),
#     ('GET', 'http://192.168.99.2:9200/plugins/UPnP/MediaServer/ConnectionManager.xml'):  # noqa: E501
#     (200, {}, _read_data_file('dms_cms_99_2.xml')),
#     ('GET', 'http://192.168.99.2:9200/plugins/UPnP/MediaServer/MediaReceiverRegistrar.xml'):  # noqa: E501
#     (200, {}, _read_data_file('dms_mrrs_99_2.xml'))
# }
