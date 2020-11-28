from upnpavcontrol.core.discovery.advertisement import AdvertisementListenerInterface


class NullAdvertisementListener(AdvertisementListenerInterface):
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
