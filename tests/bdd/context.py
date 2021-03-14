from upnpavcontrol.core import AVControlPoint
from upnpavcontrol.core.discovery import DeviceRegistry
from upnpavcontrol.core.notification_backend import NotificationBackend
from ..testsupport import NullAdvertisementListener, UpnpTestRequester, NotificationTestEndpoint
from upnpavcontrol.core.discovery.registry import MediaDeviceType, MediaDeviceDiscoveryEvent, DiscoveryEventType
import async_upnp_client
from . import fake_devices
import asyncio
import logging

_logger = logging.getLogger(__name__)


def _run_on_main_loop(f):
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(f)


class FakeUpnpDeviceFactory():
    def __init__(self, context: 'TestContext'):
        self._context = context

    async def async_create_device(self, location: str) -> async_upnp_client.UpnpDevice:
        _logger.debug('Creating device for location %s', location)
        for descriptor in self._context.devices_on_network.values():
            if descriptor.location == location:
                return fake_devices.create_fake_device(descriptor)
        raise KeyError('Device not found for location')


class TestContext(object):
    def __init__(self):
        self._available_devices = {}
        device_factory = FakeUpnpDeviceFactory(self)
        device_registry = DeviceRegistry(advertisement_listener=NullAdvertisementListener)
        self._advertisement_listener = device_registry._listener
        endpoint = NotificationTestEndpoint()
        notification_backend = NotificationBackend(endpoint=endpoint, requester=UpnpTestRequester())

        self.control_point = AVControlPoint(device_registry=device_registry,
                                            notifcation_backend=notification_backend,
                                            device_factory=device_factory)

    @property
    def devices_on_network(self):
        return self._available_devices

    def add_device_to_network(self, name, descriptor, notify=False):
        _logger.debug('added new device %s', descriptor)
        self._available_devices[name] = descriptor
        if notify:
            self.trigger_notification(descriptor, 'alive')

    def remove_device_to_network(self, name, notify=False):
        _logger.debug('remove device %s', name)
        descriptor = self._available_devices.pop(name)
        if notify:
            self.trigger_notification(descriptor, 'byebye')

    def trigger_notification(self, descriptor, event):
        ssdp = fake_devices.format_ssdp_event(descriptor, event)
        _logger.debug('trigger ssdp %s', ssdp)
        _run_on_main_loop(self._advertisement_listener.simulate(ssdp))

    async def fake_async_search(self, *args, **kwargs):
        return
