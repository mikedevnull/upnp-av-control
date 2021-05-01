from .fake_upnp_device import FakeDeviceDescriptor
from . import acme_renderer
from . import foo_media_server
from . import baz_printer
import typing

_fake_devices = {
    'FooMediaServer': foo_media_server.factory,
    'AcmeRenderer': acme_renderer.factory,
    'BazPrinter': baz_printer.factory
}


def get_device(name: str):
    return create_fake_device(_fake_devices[name])


def format_ssdp_event(descriptor: FakeDeviceDescriptor, event: str) -> typing.Mapping[str, str]:
    assert event in ('alive', 'byebye')
    if event == 'alive':
        return {
            'Host':
            '239.255.255.250:1900',
            'Cache-Control':
            'max-age=1800',
            'Location':
            descriptor.location,
            'NT':
            f'urn:schemas-upnp-org:device:{descriptor.device_type}:{descriptor.device_version}',
            'NTS':
            'ssdp:alive',
            'Server':
            'foonix/1.2 UPnP/1.0 FooServer/1.50',
            'USN':
            f'uuid:{descriptor.udn}::urn:schemas-upnp-org:device:{descriptor.device_type}:{descriptor.device_version}'  # noqa: E501
        }
    else:
        return {
            'Host':
            '239.255.255.250:1900',
            'Location':
            descriptor.location,
            'NT':
            f'urn:schemas-upnp-org:device:{descriptor.device_type}:{descriptor.device_version}',
            'NTS':
            'ssdp:byebye',
            'USN':
            f'uuid:{descriptor.udn}::urn:schemas-upnp-org:device:{descriptor.device_type}:{descriptor.device_version}'  # noqa: E501
        }


def create_fake_device(name: str):
    factory = _fake_devices[name]
    return factory()
