from upnpavcontrol.core import AVControlPoint
from upnpavcontrol.core.notification_backend import NotificationBackend
from upnpavcontrol.core.discovery.events import DiscoveryEvent, DiscoveryEventType
from ..testsupport import UpnpTestRequester, NotificationTestEndpoint
from async_upnp_client.client import UpnpDevice
from .fake_upnp import FakeAsyncUpnpDevice
from async_asgi_testclient import TestClient
import logging
import reactivex as rx
import typing

_logger = logging.getLogger(__name__)


class FakeUpnpDeviceFactory():

    def __init__(self, context: 'TestContext'):
        self._context = context

    async def async_create_device(self, location: str) -> UpnpDevice:
        _logger.debug('Creating device for location %s', location)
        for device in self._context.devices_on_network.values():
            if device.location == location:
                return device
        raise KeyError('Device not found for location')


class TestContext(object):

    def __init__(self):
        self._available_devices = {}
        device_factory = FakeUpnpDeviceFactory(self)
        self._notification_endpoint = NotificationTestEndpoint()
        self._discovery_events = rx.Subject()
        self._test_requester = UpnpTestRequester()
        notification_backend = NotificationBackend(endpoint=self._notification_endpoint, requester=self._test_requester)

        self.control_point = AVControlPoint(device_discovery_events=self._discovery_events,
                                            notifcation_backend=notification_backend,
                                            device_factory=device_factory)
        self.webclient: typing.Optional[TestClient] = None

    def get_device(self, name: str):
        return self._available_devices[name]

    @property
    def devices_on_network(self):
        return self._available_devices

    def add_device_to_network(self, name, device: FakeAsyncUpnpDevice, notify=False):
        _logger.debug('added new device %s', device.friendly_name)
        self._available_devices[name] = device
        for service in device.services.values():
            service.configure_event_handling(self._test_requester, self._notification_endpoint)
        if notify:
            self.trigger_notification(device, DiscoveryEventType.NEW_DEVICE)

    def remove_device_to_network(self, name, notify=False):
        _logger.debug('remove device %s', name)
        descriptor = self._available_devices.pop(name)
        if notify:
            self.trigger_notification(descriptor, DiscoveryEventType.DEVICE_LOST)

    def trigger_notification(self, device, event_type: DiscoveryEventType):
        descriptor = device.descriptor
        simulated_event = DiscoveryEvent(
            event_type=event_type,
            device_type=f'urn:schemas-upnp-org:device:{descriptor.device_type}:{descriptor.device_version}',
            udn=descriptor.udn,
            location=descriptor.location)
        _logger.debug('trigger event %s', simulated_event)

        self._discovery_events.on_next(simulated_event)
