from async_upnp_client.event_handler import UpnpNotifyServer


class NotificationTestEndpoint(UpnpNotifyServer):

    def __init__(self):
        self._callback = None

    @property
    def callback_url(self):
        return 'http://localhost:12345'

    async def async_start_server(self, callback):
        self._callback = callback
        pass

    async def async_stop_server(self):
        pass

    async def trigger_notification(self, headers, body):
        if self._callback is not None:
            await self._callback(headers, body)
