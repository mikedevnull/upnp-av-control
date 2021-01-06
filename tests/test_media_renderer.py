import async_upnp_client
from upnpavcontrol.core.mediarenderer import PlaybackInfo, update_playback_info_from_event, create_media_renderer
from .testsupport.upnp_device_mocks import UpnpMediaRendererDevice
from .testsupport import AsyncMock
import pytest
from unittest import mock
from typing import cast, Any
import asyncio


rc_last_change_event = """
<Event xmlns="urn:schemas-upnp-org:metadata-1-0/RCS/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="urn:schemas-upnp-org:metadata-1-0/RCS/ http://www.upnp.org/schemas/av/rcs-event-v1-20060531.xsd"><InstanceID val="0">
  <Brightness>
    <val></val>
  </Brightness>
  <Mute channel="Master" val="0" />
  <PresetNameList val="FactoryDefaults" />
  <Volume channel="Master" val="21" />
</InstanceID></Event>
"""  # noqa: E501


def test_parse_rendering_control_event():
    info = PlaybackInfo()
    assert info.volume_percent != 21
    some_value_changed = update_playback_info_from_event(info, rc_last_change_event)
    assert info.volume_percent == 21
    assert some_value_changed is True
    some_value_changed = update_playback_info_from_event(info, rc_last_change_event)
    assert info.volume_percent == 21
    assert some_value_changed is False


@pytest.mark.asyncio
async def test_renderer_creation():
    device = UpnpMediaRendererDevice()
    # setup some fake return values, different from the default mock values, to explicitly check if they are used
    device.rendering_control.action('GetVolume').mock.return_value = {'CurrentVolume': 42}
    renderer = await create_media_renderer(cast(async_upnp_client.UpnpDevice, device))
    info = renderer.playback_info

    assert info.volume_percent == 42


class MockedNotificationBackend(object):
    subscribe = AsyncMock(name='subscribe')
    unsubscribe = AsyncMock(name='unsubscribe')


@pytest.mark.asyncio
async def test_notification_subscrition():
    device = UpnpMediaRendererDevice()
    notification_backend = MockedNotificationBackend()
    renderer = await create_media_renderer(cast(async_upnp_client.UpnpDevice, device),
                                           notification_backend=cast(Any, notification_backend))

    callback1 = mock.Mock()
    callback2 = mock.Mock()
    subscription1 = await renderer.subscribe_notifcations(callback1)
    notification_backend.subscribe.assert_has_calls(
        [mock.call(device.rendering_control), mock.call(device.connection_manager)], any_order=True)
    notification_backend.unsubscribe.assert_not_called()

    notification_backend.subscribe.reset_mock()
    notification_backend.unsubscribe.reset_mock()

    subscription2 = await renderer.subscribe_notifcations(callback2)
    # already another subscription, do nothing
    notification_backend.subscribe.assert_not_called()
    notification_backend.unsubscribe.assert_not_called()

    await subscription1.unsubscribe()
    # still one subscription prending, do nothing
    notification_backend.subscribe.assert_not_called()
    notification_backend.unsubscribe.assert_not_called()

    await subscription2.unsubscribe()
    # last notification subscription cancels upnp backend subscription
    notification_backend.subscribe.assert_not_called()
    notification_backend.unsubscribe.assert_has_calls(
        [mock.call(device.rendering_control), mock.call(device.connection_manager)], any_order=True)


class FakeStateVariable(object):
    def __init__(self, name, value):
        self.name = name
        self.value = value


@pytest.mark.asyncio
async def test_renderer_handle_backend_events():
    device = UpnpMediaRendererDevice()
    renderer = await create_media_renderer(cast(async_upnp_client.UpnpDevice, device), )

    info_cb = AsyncMock()
    await renderer.subscribe_notifcations(info_cb)

    original_volume_result = await device.rendering_control.action('GetVolume').async_call()
    assert renderer.playback_info.volume_percent == original_volume_result['CurrentVolume']

    fake_event_data = [
        FakeStateVariable('foobar', 'shouldBeIgnored'),
        FakeStateVariable('LastChange', rc_last_change_event)
    ]
    renderer._on_event(device.rendering_control, cast(Any, fake_event_data))
    # _on_event cannot be a coroutine, but creates a task. Ensure this task has a chance to run
    await asyncio.sleep(0)
    await asyncio.sleep(0)
    info_cb.assert_called_once_with(PlaybackInfo(volume_percent=21))
