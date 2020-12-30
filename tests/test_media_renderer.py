import async_upnp_client
from upnpavcontrol.core.mediarenderer import PlaybackInfo, update_playback_info_from_event, create_media_renderer
import pytest
from typing import cast, Any

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


