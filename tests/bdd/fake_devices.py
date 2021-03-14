from dataclasses import dataclass
import typing
from ..testsupport.upnp_device_mocks import RenderingControlService as FakeRenderingControlService
from ..testsupport.upnp_device_mocks import ConnectionManagerService as FakeConnectionManagerService


@dataclass
class FakeDeviceDescriptor(object):
    location: str
    device_type: str
    udn: str
    name: str
    friendly_name: str
    service_types: typing.List[str]
    device_version: int = 1


class FakeAsyncUpnpDevice(object):
    def __init__(self, name, friendly_name, udn):
        self.name = name
        self.friendly_name = friendly_name
        self.udn = udn
        self._services = {}

    def has_service(self, service_type):
        return service_type in self._services

    def service(self, service_type):
        return self._services[service_type]

    def mock_add_service(self, service):
        self._services[service.service_type] = service


_fake_services = {
    'RenderingControl:1': FakeRenderingControlService,
    'ConnectionManager:1': FakeConnectionManagerService
}

_fake_devices = {
    'FooMediaServer':
    FakeDeviceDescriptor(name="FooMedia",
                         friendly_name="Foo MediaServer",
                         location='http://192.168.99.2:9200/plugins/MediaServer.xml',
                         udn='f5b1b596-c1d2-11e9-af8b-705681aa5dfd',
                         device_type='MediaServer',
                         service_types=[]),
    'AcmeRenderer':
    FakeDeviceDescriptor(name="AcmeRenderer",
                         friendly_name="Acme Super Blast Renderer",
                         location='http://192.168.99.1:5000',
                         udn='13bf6358-00b8-101b-8000-74dfbfed7306',
                         device_type='MediaRenderer',
                         service_types=['RenderingControl:1', 'ConnectionManager:1']),
    'BazPrinter':
    FakeDeviceDescriptor(name='BazPrinter',
                         friendly_name="Baz inc printer",
                         location='http://192.168.99.55',
                         udn='1234-5667-999-0',
                         device_type='Printer',
                         service_types=[])
}


def get_device(name: str):
    return _fake_devices[name]


def get_service(name: str):
    return _fake_services[name]()


def format_ssdp_event(descriptor: FakeDeviceDescriptor, event: str) -> typing.Mapping[str, str]:
    assert event in ('alive')
    return {
        'Host': '239.255.255.250:1900',
        'Cache-Control': 'max-age=1800',
        'Location': descriptor.location,
        'NT': f'urn:schemas-upnp-org:device:{descriptor.device_type}:{descriptor.device_version}',
        'NTS': f'ssdp:{event}',
        'Server': 'foonix/1.2 UPnP/1.0 FooServer/1.50',
        'USN':
        f'uuid:{descriptor.udn}::urn:schemas-upnp-org:device:{descriptor.device_type}:{descriptor.device_version}'  # noqa: E501
    }


def create_fake_device(descriptor: FakeDeviceDescriptor):
    device = FakeAsyncUpnpDevice(descriptor.name, descriptor.friendly_name, descriptor.udn)
    for st in descriptor.service_types:
        stub_service = get_service(st)
        device.mock_add_service(stub_service)
    return device
