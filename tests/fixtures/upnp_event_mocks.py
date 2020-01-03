from .discovery_mocks import UpnpTestRequester
from upnpavcontrol.core.notification_backend import NotificationEndpointBase, NotificationBackend


class NotificationTestEndpoint(NotificationEndpointBase):
    @property
    def callback_url(self):
        return 'http://localhost:12345'

    async def async_start(self, callback):
        pass

    async def async_stop(self):
        pass


_RESPONSES = {
    ('SUBSCRIBE', 'http://localhost:12342/rcs'): (200, {
        'SID': 'uuid:1381a57c-887f-1fbc-8000-f8b69e888b3d',
        'Timeout': 'Second-1800',
        'Content-Length': '0',
    }, ''),
}


def create_test_notification_backend():
    requester = UpnpTestRequester(_RESPONSES)
    endpoint = NotificationTestEndpoint()
    return NotificationBackend(endpoint=endpoint, requester=requester)
