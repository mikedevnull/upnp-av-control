from upnpavcontrol.core.notification_backend import NotificationEndpointBase


class NotificationTestEndpoint(NotificationEndpointBase):
    @property
    def callback_url(self):
        return 'http://localhost:12345'

    async def async_start(self, callback):
        pass

    async def async_stop(self):
        pass
