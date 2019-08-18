# -*- coding: utf-8 -*-
from upnpavcontrol.core import discover
import pytest

alive_renderer_device_data = {
    'Host':
    '239.255.255.250:1900',
    'Cache-Control':
    'max-age=1800',
    'Location':
    'http://192.168.99.1:1234/dmr.xml',
    'NT':
    'urn:schemas-upnp-org:device:MediaRenderer:1',
    'NTS':
    'ssdp:alive',
    'Server':
    'foonix/1.2 UPnP/1.0 FooRender/1.50',
    'USN':
    'uuid:13bf6358-00b8-101b-8000-74dfbfed7306::urn:schemas-upnp-org:device:MediaRenderer:1'  # noqa: E501
}

alive_printer_device_data = {
    'Host':
    '239.255.255.250:1900',
    'Cache-Control':
    'max-age=1800',
    'Location':
    'http://192.168.99.3:1234/device.xml',
    'NT':
    'urn:schemas-upnp-org:device:printer:1',
    'Server':
    'foonix/1.2 UPnP/1.0 FooPrinter/1.50',
    'NTS':
    'ssdp:alive',
    'USN':
    'uuid:92b65aa0-c1dc-11e9-8a7b-705681aa5dfd::urn:schemas-upnp-org:device:printer:1'  # noqa: E501
}

alive_server_device_data = {
    'Host':
    '239.255.255.250:1900',
    'Cache-Control':
    'max-age=1800',
    'Location':
    'http://192.168.99.2:9200/plugins/MediaServer.xml',
    'NT':
    'urn:schemas-upnp-org:device:MediaServer:1',
    'NTS':
    'ssdp:alive',
    'Server':
    'foonix/1.2 UPnP/1.0 FooServer/1.50',
    'USN':
    'uuid:f5b1b596-c1d2-11e9-af8b-705681aa5dfd::urn:schemas-upnp-org:device:MediaServer:1'  # noqa: E501
}

byebye_renderer_device_data = {
    'Host':
    '239.255.255.250:1900',
    'Location':
    'http://192.168.99.1:1234/dmr.xml',
    'NT':
    'urn:schemas-upnp-org:device:MediaRenderer:1',
    'NTS':
    'ssdp:byebye',
    'USN':
    'uuid:13bf6358-00b8-101b-8000-74dfbfed7306::urn:schemas-upnp-org:device:MediaRenderer:1'  # noqa: E501
}


@pytest.mark.asyncio
async def test_discover_by_alive(mock_discovery_backend):
    registry = discover.DeviceRegistry()
    assert len(registry._av_devices) == 0

    await registry._listener.trigger_alive(alive_renderer_device_data)

    assert len(registry._av_devices) == 1
    assert len(registry.mediarenderers) == 1
    assert len(registry.mediaservers) == 0

    assert registry.mediarenderers[0].friendly_name == 'FooRenderer'

    await registry._listener.trigger_alive(alive_server_device_data)

    assert len(registry._av_devices) == 2
    assert len(registry.mediarenderers) == 1
    assert len(registry.mediaservers) == 1

    # alive message from an already known device should do nothing
    await registry._listener.trigger_alive(alive_server_device_data)

    assert len(registry._av_devices) == 2
    assert len(registry.mediarenderers) == 1
    assert len(registry.mediaservers) == 1


@pytest.mark.asyncio
async def test_ignore_non_av_devices(mock_discovery_backend):
    registry = discover.DeviceRegistry()
    assert len(registry._av_devices) == 0

    await registry._listener.trigger_alive(alive_printer_device_data)

    assert len(registry._av_devices) == 0
    assert len(registry.mediarenderers) == 0
    assert len(registry.mediaservers) == 0


@pytest.mark.asyncio
async def test_remove_by_byebye(mock_discovery_backend):
    registry = discover.DeviceRegistry()

    await registry._listener.trigger_alive(alive_renderer_device_data)
    await registry._listener.trigger_alive(alive_server_device_data)
    assert len(registry._av_devices) == 2

    await registry._listener.trigger_byebye(byebye_renderer_device_data)

    assert len(registry._av_devices) == 1
    assert len(registry.mediarenderers) == 0
    assert len(registry.mediaservers) == 1


@pytest.mark.asyncio
async def test_scan_av_devices(mock_discovery_backend, mock_scanned_devices):
    registry = discover.DeviceRegistry()
    await registry.scan()

    assert len(registry._av_devices) == 2
    assert len(registry.mediarenderers) == 1
    assert len(registry.mediaservers) == 1
