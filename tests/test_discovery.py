# -*- coding: utf-8 -*-
import pytest
from upnpavcontrol.core.discovery.advertisement import _DeviceAdvertisementHandler
from . import advertisement_data
from unittest.mock import AsyncMock, Mock
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
async def test_device_registry_event_processing(mocked_device_registry):
    registry = mocked_device_registry
    discovery_callback = Mock(name='registry_event_callback')
    registry.set_event_callback(discovery_callback)
    await registry.async_start()
    assert len(registry.mediaservers) == 0
    assert len(registry.mediarenderers) == 0

    await registry._event_queue.put(advertisement_data.alive_renderer_event)
    await registry._event_queue.join()

    assert len(registry.mediaservers) == 0
    assert len(registry.mediarenderers) == 1

    discovery_callback.assert_called_once_with(advertisement_data.alive_renderer_event.event_type,
                                               advertisement_data.alive_renderer_event.udn)

    discovery_callback.reset_mock()
    await registry._event_queue.put(advertisement_data.alive_server_event)
    await registry._event_queue.join()

    assert len(registry.mediaservers) == 1
    assert len(registry.mediarenderers) == 1

    discovery_callback.assert_called_once_with(advertisement_data.alive_server_event.event_type,
                                               advertisement_data.alive_server_event.udn)

    # same event for already known device: callback not called
    discovery_callback.reset_mock()
    await registry._event_queue.put(advertisement_data.alive_renderer_event)
    await registry._event_queue.join()

    discovery_callback.assert_not_called()
    assert len(registry.mediaservers) == 1
    assert len(registry.mediarenderers) == 1

    # removal of known device
    discovery_callback.reset_mock()
    await registry._event_queue.put(advertisement_data.byebye_renderer_event)
    await registry._event_queue.join()

    discovery_callback.assert_called_once_with(advertisement_data.byebye_renderer_event.event_type,
                                               advertisement_data.byebye_renderer_event.udn)
    assert len(registry.mediaservers) == 1
    assert len(registry.mediarenderers) == 0

    # removal of uknown device,
    discovery_callback.reset_mock()
    await registry._event_queue.put(advertisement_data.byebye_renderer_event)
    await registry._event_queue.join()

    discovery_callback.assert_not_called()
    assert len(registry.mediaservers) == 1
    assert len(registry.mediarenderers) == 0


@pytest.mark.asyncio
async def test_scan_av_devices(started_mocked_device_registry, mock_scanned_devices):
    registry = started_mocked_device_registry
    discovery_callback = Mock(name='registry_event_callback')
    registry.set_event_callback(discovery_callback)

    # ensure all outstanding (i.e. simulated) discovery events have been processed
    await registry._event_queue.join()

    assert len(registry._av_devices) == 2
    assert len(registry.mediarenderers) == 1
    assert len(registry.mediaservers) == 1

    discovery_callback.assert_called()
    await registry.async_stop()
