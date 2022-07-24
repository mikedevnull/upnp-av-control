from upnpavcontrol.core.discovery.events import DiscoveryEvent as SSDPEvent
from upnpavcontrol.core.discovery import DiscoveryEventType, DeviceEntry, MediaDeviceType

renderer_entry = DeviceEntry(device_type=MediaDeviceType.MEDIARENDERER,
                             udn='13bf6358-00b8-101b-8000-74dfbfed7306',
                             location='http://192.168.99.1:1234/dmr.xml')

alive_renderer_ssdp = {
    'Host': '239.255.255.250:1900',
    'Cache-Control': 'max-age=1800',
    'Location': renderer_entry.location,
    'NT': 'urn:schemas-upnp-org:device:MediaRenderer:1',
    'NTS': 'ssdp:alive',
    'Server': 'foonix/1.2 UPnP/1.0 FooRender/1.50',
    'USN': f'uuid:{renderer_entry.udn}::urn:schemas-upnp-org:device:MediaRenderer:1'  # noqa: E501
}

alive_renderer_event = SSDPEvent(DiscoveryEventType.NEW_DEVICE, 'urn:schemas-upnp-org:device:MediaRenderer:1',
                                 renderer_entry.udn, renderer_entry.location)

alive_printer_ssdp = {
    'Host': '239.255.255.250:1900',
    'Cache-Control': 'max-age=1800',
    'Location': 'http://192.168.99.3:1234/device.xml',
    'NT': 'urn:schemas-upnp-org:device:printer:1',
    'Server': 'foonix/1.2 UPnP/1.0 FooPrinter/1.50',
    'NTS': 'ssdp:alive',
    'USN': 'uuid:92b65aa0-c1dc-11e9-8a7b-705681aa5dfd::urn:schemas-upnp-org:device:printer:1'  # noqa: E501
}

server_entry = DeviceEntry(location='http://192.168.99.2:9200/plugins/MediaServer.xml',
                           udn='f5b1b596-c1d2-11e9-af8b-705681aa5dfd',
                           device_type=MediaDeviceType.MEDIASERVER)
alive_server_ssdp = {
    'Host': '239.255.255.250:1900',
    'Cache-Control': 'max-age=1800',
    'Location': server_entry.location,
    'NT': 'urn:schemas-upnp-org:device:MediaServer:1',
    'NTS': 'ssdp:alive',
    'Server': 'foonix/1.2 UPnP/1.0 FooServer/1.50',
    'USN': f'uuid:{server_entry.udn}::urn:schemas-upnp-org:device:MediaServer:1'  # noqa: E501
}

alive_server_event = SSDPEvent(DiscoveryEventType.NEW_DEVICE, 'urn:schemas-upnp-org:device:MediaServer:1',
                               'f5b1b596-c1d2-11e9-af8b-705681aa5dfd',
                               'http://192.168.99.2:9200/plugins/MediaServer.xml')

byebye_renderer_ssdp = {
    'Host': '239.255.255.250:1900',
    'NT': 'urn:schemas-upnp-org:device:MediaRenderer:1',
    'NTS': 'ssdp:byebye',
    'USN': f'uuid:{renderer_entry.udn}::urn:schemas-upnp-org:device:MediaRenderer:1'  # noqa: E501
}

byebye_printer_ssdp = {
    'Host': '239.255.255.250:1900',
    'NT': 'urn:schemas-upnp-org:device:printer:1',
    'NTS': 'ssdp:byebye',
    'USN': 'uuid:92b65aa0-c1dc-11e9-8a7b-705681aa5dfd::urn:schemas-upnp-org:device:printer:1'  # noqa: E501
}

byebye_renderer_event = SSDPEvent(DiscoveryEventType.DEVICE_LOST, 'urn:schemas-upnp-org:device:MediaRenderer:1',
                                  '13bf6358-00b8-101b-8000-74dfbfed7306')

update_renderer_ssdp = {
    'Host': '239.255.255.250:1900',
    'Location': renderer_entry.location,
    'NT': 'urn:schemas-upnp-org:device:MediaRenderer:1',
    'NTS': 'ssdp:update',
    'USN': f'uuid:{renderer_entry.udn}::urn:schemas-upnp-org:device:MediaRenderer:1'  # noqa: E501
}

update_renderer_event = SSDPEvent(DiscoveryEventType.DEVICE_UPDATE, 'urn:schemas-upnp-org:device:MediaRenderer:1',
                                  '13bf6358-00b8-101b-8000-74dfbfed7306', 'http://192.168.99.1:1234/dmr.xml')

update_printer_ssdp = {
    'Host': '239.255.255.250:1900',
    'Location': 'http://192.168.99.3:1234/device.xml',
    'NT': 'urn:schemas-upnp-org:device:printer:1',
    'NTS': 'ssdp:update',
    'USN': 'uuid:92b65aa0-c1dc-11e9-8a7b-705681aa5dfd::urn:schemas-upnp-org:device:printer:1'  # noqa: E501
}
