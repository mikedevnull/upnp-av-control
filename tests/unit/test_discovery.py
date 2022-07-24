# -*- coding: utf-8 -*-
from upnpavcontrol.core.discovery.events import DiscoveryEvent as SSDPEvent, DiscoveryEventType
import pytest
from upnpavcontrol.core.discovery.advertisement import _DeviceAdvertisementHandler
import upnpavcontrol.core.discovery.scan
from upnpavcontrol.core import discovery
from ..testsupport import NullAdvertisementListener, AsyncMock
from . import advertisement_data

import asyncio

ssdp_to_event_mapping = [(advertisement_data.alive_renderer_ssdp, advertisement_data.alive_renderer_event),
                         (advertisement_data.alive_server_ssdp, advertisement_data.alive_server_event),
                         (advertisement_data.byebye_renderer_ssdp, advertisement_data.byebye_renderer_event),
                         (advertisement_data.alive_printer_ssdp, None), (advertisement_data.byebye_printer_ssdp, None),
                         (advertisement_data.update_renderer_ssdp, advertisement_data.update_renderer_event),
                         (advertisement_data.update_printer_ssdp, None)]


@pytest.mark.asyncio
@pytest.mark.parametrize("test_input,expected_event", ssdp_to_event_mapping)
async def test_handle_advertisement_alive(test_input, expected_event):
    queue = AsyncMock(asyncio.Queue)
    handler = _DeviceAdvertisementHandler(queue)
    if test_input['NTS'] == 'ssdp:alive':
        await handler.on_alive(test_input)
    elif test_input['NTS'] == 'ssdp:byebye':
        await handler.on_byebye(test_input)
    elif test_input['NTS'] == 'ssdp:update':
        await handler.on_update(test_input)

    if expected_event is None:
        queue.put.assert_not_called()
    else:
        queue.put.assert_called_once_with(expected_event)


@pytest.mark.asyncio
async def test_device_registry_event_processing():
    registry = discovery.DeviceRegistry(advertisement_listener=NullAdvertisementListener)
    discovery_callback = AsyncMock(name='registry_event_callback')
    registry.set_event_callback(discovery_callback)
    await registry.async_start()
    assert len(registry.devices) == 0

    await registry._event_queue.put(advertisement_data.alive_renderer_event)
    await registry._event_queue.join()

    assert len(registry.devices) == 1
    discovery_callback.assert_called_once_with(advertisement_data.alive_renderer_event.event_type,
                                               advertisement_data.renderer_entry)

    discovery_callback.reset_mock()
    await registry._event_queue.put(advertisement_data.alive_server_event)
    await registry._event_queue.join()

    assert len(registry.devices) == 2

    discovery_callback.assert_called_once_with(advertisement_data.alive_server_event.event_type,
                                               advertisement_data.server_entry)

    # same event for already known device: callback not called
    discovery_callback.reset_mock()
    await registry._event_queue.put(advertisement_data.alive_renderer_event)
    await registry._event_queue.join()

    discovery_callback.assert_not_called()
    assert len(registry.devices) == 2

    # removal of known device
    discovery_callback.reset_mock()
    await registry._event_queue.put(advertisement_data.byebye_renderer_event)
    await registry._event_queue.join()

    discovery_callback.assert_called_once_with(advertisement_data.byebye_renderer_event.event_type,
                                               advertisement_data.renderer_entry)
    assert len(registry.devices) == 1

    # removal of uknown device,
    discovery_callback.reset_mock()
    await registry._event_queue.put(advertisement_data.byebye_renderer_event)
    await registry._event_queue.join()

    discovery_callback.assert_not_called()
    assert len(registry.devices) == 1
    await registry.async_stop()


scan_server_ssdp = {
    'Host': '239.255.255.250:1900',
    'Cache-Control': 'max-age=1800',
    'Location': 'http://192.168.99.2:9200/plugins/MediaServer.xml',
    'ST': 'urn:schemas-upnp-org:device:MediaServer:1',
    'NTS': 'ssdp:alive',
    'Server': 'foonix/1.2 UPnP/1.0 FooServer/1.50',
    'USN': 'uuid:f5b1b596-c1d2-11e9-af8b-705681aa5dfd::urn:schemas-upnp-org:device:MediaServer:1'  # noqa: E501
}

scan_renderer_ssdp = {
    'Cache-Control': 'max-age=1800',
    'Ext': None,
    'Location': 'http://192.168.99.1:1234/dmr.xml',
    'ST': 'urn:schemas-upnp-org:device:MediaRenderer:1',
    'NTS': 'ssdp:alive',
    'Server': 'foonix/1.2 UPnP/1.0 FooRender/1.50',
    'USN': 'uuid:13bf6358-00b8-101b-8000-74dfbfed7306::urn:schemas-upnp-org:device:MediaRenderer:1'  # noqa: E501
}


async def mock_async_search(async_callback, timeout, service_type):
    from upnpavcontrol.core.discovery import utils
    if utils.is_media_renderer(service_type):
        await async_callback(scan_renderer_ssdp)
    elif utils.is_media_server(service_type):
        await async_callback(scan_server_ssdp)


@pytest.mark.asyncio
async def test_scan_av_devices(monkeypatch, ):
    monkeypatch.setattr(upnpavcontrol.core.discovery.scan, 'async_search', mock_async_search)
    queue = AsyncMock(asyncio.Queue)
    await upnpavcontrol.core.discovery.scan.scan_devices(queue, 'urn:schemas-upnp-org:device:MediaServer:1')
    queue.put.assert_called_once_with(
        SSDPEvent(DiscoveryEventType.NEW_DEVICE, 'urn:schemas-upnp-org:device:MediaServer:1',
                  'f5b1b596-c1d2-11e9-af8b-705681aa5dfd', 'http://192.168.99.2:9200/plugins/MediaServer.xml'))
