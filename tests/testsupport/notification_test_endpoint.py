from upnpavcontrol.core.notification_backend import NotificationEndpointBase


class NotificationTestEndpoint(NotificationEndpointBase):
    def __init__(self):
        self._callback = None

    @property
    def callback_url(self):
        return 'http://localhost:12345'

    async def async_start(self, callback):
        self._callback = callback
        pass

    async def async_stop(self):
        pass

    async def trigger_notification(self, headers, body):
        await self._callback(headers, body)
