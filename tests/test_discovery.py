# -*- coding: utf-8 -*-
import pytest
from upnpavcontrol.core import discover

from unittest.mock import Mock


@pytest.mark.asyncio
async def test_discover_by_alive(mocked_device_registry):
    registry = mocked_device_registry

    discovery_callback = Mock(name='registry_event_callback')
    registry.set_event_callback(discovery_callback)

    assert len(registry._av_devices) == 0

    renderer_ssdp_data = await registry.trigger_renderer_alive()

    discovery_callback.assert_called_once_with(
        discover.DiscoveryEventType.NEW_DEVICE,
        discover.udn_from_usn(renderer_ssdp_data['USN'], renderer_ssdp_data['NT']))

    assert len(registry._av_devices) == 1
    assert len(registry.mediarenderers) == 1
    assert len(registry.mediaservers) == 0

    assert registry.mediarenderers[0].friendly_name == 'FooRenderer'

    server_ssdp_data = await registry.trigger_server_alive()

    assert len(registry._av_devices) == 2
    assert len(registry.mediarenderers) == 1
    assert len(registry.mediaservers) == 1

    assert discovery_callback.call_count == 2
    discovery_callback.assert_called_with(discover.DiscoveryEventType.NEW_DEVICE,
                                          discover.udn_from_usn(server_ssdp_data['USN'], server_ssdp_data['NT']))

    # alive message from an already known device should do nothing
    await registry.trigger_server_alive()

    assert len(registry._av_devices) == 2
    assert len(registry.mediarenderers) == 1
    assert len(registry.mediaservers) == 1

    # callback has not been called for already known device
    assert discovery_callback.call_count == 2


@pytest.mark.asyncio
async def test_ignore_non_av_devices(mocked_device_registry):
    registry = mocked_device_registry

    discovery_callback = Mock(name='registry_event_callback')
    registry.set_event_callback(discovery_callback)

    assert len(registry._av_devices) == 0

    await registry.trigger_printer_alive()

    assert len(registry._av_devices) == 0
    assert len(registry.mediarenderers) == 0
    assert len(registry.mediaservers) == 0
    discovery_callback.assert_not_called()


@pytest.mark.asyncio
async def test_remove_by_byebye(mocked_device_registry):
    registry = mocked_device_registry

    await registry.trigger_renderer_alive()
    await registry.trigger_server_alive()
    assert len(registry._av_devices) == 2

    discovery_callback = Mock(name='registry_event_callback')
    registry.set_event_callback(discovery_callback)

    renderer_ssdp_data = await registry.trigger_renderer_byebye()

    assert len(registry._av_devices) == 1
    assert len(registry.mediarenderers) == 0
    assert len(registry.mediaservers) == 1

    discovery_callback.assert_called_once_with(
        discover.DiscoveryEventType.DEVICE_LOST,
        discover.udn_from_usn(renderer_ssdp_data['USN'], renderer_ssdp_data['NT']))


@pytest.mark.asyncio
async def test_scan_av_devices(mocked_device_registry, mock_scanned_devices):
    registry = mocked_device_registry
    discovery_callback = Mock(name='registry_event_callback')
    registry.set_event_callback(discovery_callback)

    await registry.scan()

    assert len(registry._av_devices) == 2
    assert len(registry.mediarenderers) == 1
    assert len(registry.mediaservers) == 1

    discovery_callback.assert_called()
