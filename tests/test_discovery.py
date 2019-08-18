# -*- coding: utf-8 -*-
import pytest
from upnpavcontrol.core import discover
from .mock_utils import ssdp_alive_printer_device_data
from .mock_utils import ssdp_alive_server_device_data
from .mock_utils import ssdp_alive_renderer_device_data
from .mock_utils import ssdp_byebye_renderer_device_data


@pytest.mark.asyncio
async def test_discover_by_alive(mock_discovery_backend):
    registry = discover.DeviceRegistry()
    assert len(registry._av_devices) == 0

    await registry._listener.trigger_alive(ssdp_alive_renderer_device_data)

    assert len(registry._av_devices) == 1
    assert len(registry.mediarenderers) == 1
    assert len(registry.mediaservers) == 0

    assert registry.mediarenderers[0].friendly_name == 'FooRenderer'

    await registry._listener.trigger_alive(ssdp_alive_server_device_data)

    assert len(registry._av_devices) == 2
    assert len(registry.mediarenderers) == 1
    assert len(registry.mediaservers) == 1

    # alive message from an already known device should do nothing
    await registry._listener.trigger_alive(ssdp_alive_server_device_data)

    assert len(registry._av_devices) == 2
    assert len(registry.mediarenderers) == 1
    assert len(registry.mediaservers) == 1


@pytest.mark.asyncio
async def test_ignore_non_av_devices(mocked_device_registry):
    registry = mocked_device_registry
    assert len(registry._av_devices) == 0

    await registry._listener.trigger_alive(ssdp_alive_printer_device_data)

    assert len(registry._av_devices) == 0
    assert len(registry.mediarenderers) == 0
    assert len(registry.mediaservers) == 0


@pytest.mark.asyncio
async def test_remove_by_byebye(mocked_device_registry):
    registry = mocked_device_registry

    await registry._listener.trigger_alive(ssdp_alive_renderer_device_data)
    await registry._listener.trigger_alive(ssdp_alive_server_device_data)
    assert len(registry._av_devices) == 2

    await registry._listener.trigger_byebye(ssdp_byebye_renderer_device_data)

    assert len(registry._av_devices) == 1
    assert len(registry.mediarenderers) == 0
    assert len(registry.mediaservers) == 1


@pytest.mark.asyncio
async def test_scan_av_devices(mocked_device_registry, mock_scanned_devices):
    registry = mocked_device_registry
    await registry.scan()

    assert len(registry._av_devices) == 2
    assert len(registry.mediarenderers) == 1
    assert len(registry.mediaservers) == 1
