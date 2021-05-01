from dataclasses import dataclass
import typing
import urllib.parse


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
    def __init__(self, descriptor: FakeDeviceDescriptor):
        self.descriptor = descriptor
        self.services = {}

    @property
    def name(self):
        return self.descriptor.name

    @property
    def friendly_name(self):
        return self.descriptor.friendly_name

    @property
    def udn(self):
        return self.descriptor.udn

    @property
    def location(self):
        return self.descriptor.location

    def has_service(self, service_type):
        return service_type in self.services

    def service(self, service_type):
        return self.services[service_type]

    def mock_add_service(self, service):
        escaped_name = service.service_type.replace(":", "-")
        service.event_sub_url = urllib.parse.urljoin(self.location, escaped_name)
        self.services[service.service_type] = service
