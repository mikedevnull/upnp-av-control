from dataclasses import dataclass
import typing

# alive_server_ssdp = {
#     'Host': '239.255.255.250:1900',
#     'Cache-Control': 'max-age=1800',
#     'Location': server_entry.location,
#     'NT': 'urn:schemas-upnp-org:device:MediaServer:1',
#     'NTS': 'ssdp:alive',
#     'Server': 'foonix/1.2 UPnP/1.0 FooServer/1.50',
#     'USN': f'uuid:{server_entry.udn}::urn:schemas-upnp-org:device:MediaServer:1'  # noqa: E501
# }
# server_entry = DeviceEntry(location='http://192.168.99.2:9200/plugins/MediaServer.xml',
#                            udn='f5b1b596-c1d2-11e9-af8b-705681aa5dfd',
#                            device_type=MediaDeviceType.MEDIASERVER)
#


@dataclass
class FakeDeviceDescriptor(object):
    location: str
    device_type: str
    udn: str
    device_version: int = 1


_fake_devices = {
    'FooServer':
    FakeDeviceDescriptor(location='http://192.168.99.2:9200/plugins/MediaServer.xml',
                         udn='f5b1b596-c1d2-11e9-af8b-705681aa5dfd',
                         device_type='MediaServer')
}


def get_device(name: str):
    return _fake_devices[name]


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
    return descriptor
