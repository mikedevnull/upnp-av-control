from upnpavcontrol.core import AVControlPoint
from upnpavcontrol.core.discovery import DeviceRegistry
from upnpavcontrol.core.notification_backend import NotificationBackend
from ..testsupport import NullAdvertisementListener, UpnpTestRequester, NotificationTestEndpoint
import async_upnp_client
from .fake_upnp import format_ssdp_event, FakeAsyncUpnpDevice
from .async_utils import run_on_main_loop
import logging

_logger = logging.getLogger(__name__)


class FakeUpnpDeviceFactory():
    def __init__(self, context: 'TestContext'):
        self._context = context

    async def async_create_device(self, location: str) -> async_upnp_client.UpnpDevice:
        _logger.debug('Creating device for location %s', location)
        for device in self._context.devices_on_network.values():
            if device.location == location:
                return device
        raise KeyError('Device not found for location')


class TestContext(object):
    def __init__(self):
        self._available_devices = {}
        device_factory = FakeUpnpDeviceFactory(self)
        device_registry = DeviceRegistry(advertisement_listener=NullAdvertisementListener)
        self._advertisement_listener = device_registry._listener
        self._notification_endpoint = NotificationTestEndpoint()
        self._test_requester = UpnpTestRequester()
        notification_backend = NotificationBackend(endpoint=self._notification_endpoint, requester=self._test_requester)

        self.control_point = AVControlPoint(device_registry=device_registry,
                                            notifcation_backend=notification_backend,
                                            device_factory=device_factory)

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
            self.trigger_notification(device, 'alive')

    def remove_device_to_network(self, name, notify=False):
        _logger.debug('remove device %s', name)
        descriptor = self._available_devices.pop(name)
        if notify:
            self.trigger_notification(descriptor, 'byebye')

    def trigger_notification(self, device, event):
        ssdp = format_ssdp_event(device.descriptor, event)
        _logger.debug('trigger ssdp %s', ssdp)
        run_on_main_loop(self._advertisement_listener.simulate(ssdp))

    async def fake_async_search(self, *args, **kwargs):
        return
