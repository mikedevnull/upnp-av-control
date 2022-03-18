from upnpavcontrol.core.mediarenderer import PlaybackInfo, update_playback_info_from_event


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


av_last_change_event = """
<Event xmlns="urn:schemas-upnp-org:metadata-1-0/AVT/">
    <InstanceID val="0">
        <AVTransportURI val="http://somehost:9002/music/3151/download.flc" />
        <AVTransportURIMetaData val="&lt;DIDL-Lite xmlns:dc=&quot;http://purl.org/dc/elements/1.1/&quot; xmlns:upnp=&quot;urn:schemas-upnp-org:metadata-1-0/upnp/&quot; xmlns:pv=&quot;http://www.pv.com/pvns/&quot; xmlns=&quot;urn:schemas-upnp-org:metadata-1-0/DIDL-Lite/&quot;&gt;&lt;item id=&quot;/a/199/l/202/t/3151&quot; parentID=&quot;/a/199/l/202/t&quot; restricted=&quot;1&quot;&gt;&lt;upnp:class&gt;object.item.audioItem.musicTrack&lt;/upnp:class&gt;&lt;dc:title&gt;SomeTitle&lt;/dc:title&gt;&lt;dc:creator&gt;SomeCreator&lt;/dc:creator&gt;&lt;upnp:album&gt;SomeAlbum&lt;/upnp:album&gt;&lt;upnp:artist role=&quot;artist&quot;&gt;SomeArtist&lt;/upnp:artist&gt;&lt;dc:contributor&gt;SomeCreator&lt;/dc:contributor&gt;&lt;upnp:originalTrackNumber&gt;7&lt;/upnp:originalTrackNumber&gt;&lt;dc:date&gt;1996-01-01&lt;/dc:date&gt;&lt;upnp:genre&gt;Country &amp;amp; Western&lt;/upnp:genre&gt;&lt;upnp:albumArtURI dlna:profileID=&quot;JPEG_TN&quot; xmlns:dlna=&quot;urn:schemas-dlna-org:metadata-1-0/&quot;&gt;http://somehost:9002/music/ec34a1b1/cover_160x160_m.jpg&lt;/upnp:albumArtURI&gt;&lt;upnp:albumArtURI&gt;http://somehost:9002/music/ec34a1b1/cover&lt;/upnp:albumArtURI&gt;&lt;pv:modificationTime&gt;1305365059&lt;/pv:modificationTime&gt;&lt;pv:addedTime&gt;1544479704&lt;/pv:addedTime&gt;&lt;pv:lastUpdated&gt;1544479704&lt;/pv:lastUpdated&gt;&lt;res protocolInfo=&quot;http-get:*:audio/x-flac:DLNA.ORG_OP=11;DLNA.ORG_FLAGS=01700000000000000000000000000000&quot; size=&quot;44040213&quot; duration=&quot;0:05:54.560&quot; bitrate=&quot;124125&quot; bitsPerSample=&quot;16&quot; sampleFrequency=&quot;44100&quot;&gt;http://somehost:9002/music/3151/download.flc&lt;/res&gt;&lt;res protocolInfo=&quot;http-get:*:audio/L16;rate=44100;channels=2:DLNA.ORG_PN=LPCM;DLNA.ORG_CI=1;DLNA.ORG_FLAGS=01700000000000000000000000000000&quot; duration=&quot;0:05:54.560&quot; bitsPerSample=&quot;16&quot; sampleFrequency=&quot;44100&quot;&gt;http://somehost:9002/music/3151/download.aif&lt;/res&gt;&lt;/item&gt;&lt;/DIDL-Lite&gt;" />
        <CurrentTrackDuration val="0:00:00.000" />
        <CurrentTrackMetaData val="&lt;DIDL-Lite xmlns:dc=&quot;http://purl.org/dc/elements/1.1/&quot; xmlns:upnp=&quot;urn:schemas-upnp-org:metadata-1-0/upnp/&quot; xmlns:pv=&quot;http://www.pv.com/pvns/&quot; xmlns=&quot;urn:schemas-upnp-org:metadata-1-0/DIDL-Lite/&quot;&gt;&lt;item id=&quot;/a/199/l/202/t/3151&quot; parentID=&quot;/a/199/l/202/t&quot; restricted=&quot;1&quot;&gt;&lt;upnp:class&gt;object.item.audioItem.musicTrack&lt;/upnp:class&gt;&lt;dc:title&gt;SomeTitle&lt;/dc:title&gt;&lt;dc:creator&gt;SomeCreator&lt;/dc:creator&gt;&lt;upnp:album&gt;SomeAlbum&lt;/upnp:album&gt;&lt;upnp:artist role=&quot;artist&quot;&gt;SomeArtist&lt;/upnp:artist&gt;&lt;dc:contributor&gt;SomeCreator&lt;/dc:contributor&gt;&lt;upnp:originalTrackNumber&gt;7&lt;/upnp:originalTrackNumber&gt;&lt;dc:date&gt;1996-01-01&lt;/dc:date&gt;&lt;upnp:genre&gt;Country &amp;amp; Western&lt;/upnp:genre&gt;&lt;upnp:albumArtURI dlna:profileID=&quot;JPEG_TN&quot; xmlns:dlna=&quot;urn:schemas-dlna-org:metadata-1-0/&quot;&gt;http://somehost:9002/music/ec34a1b1/cover_160x160_m.jpg&lt;/upnp:albumArtURI&gt;&lt;upnp:albumArtURI&gt;http://somehost:9002/music/ec34a1b1/cover&lt;/upnp:albumArtURI&gt;&lt;pv:modificationTime&gt;1305365059&lt;/pv:modificationTime&gt;&lt;pv:addedTime&gt;1544479704&lt;/pv:addedTime&gt;&lt;pv:lastUpdated&gt;1544479704&lt;/pv:lastUpdated&gt;&lt;res protocolInfo=&quot;http-get:*:audio/x-flac:DLNA.ORG_OP=11;DLNA.ORG_FLAGS=01700000000000000000000000000000&quot; size=&quot;44040213&quot; duration=&quot;0:05:54.560&quot; bitrate=&quot;124125&quot; bitsPerSample=&quot;16&quot; sampleFrequency=&quot;44100&quot;&gt;http://somehost:9002/music/3151/download.flc&lt;/res&gt;&lt;res protocolInfo=&quot;http-get:*:audio/L16;rate=44100;channels=2:DLNA.ORG_PN=LPCM;DLNA.ORG_CI=1;DLNA.ORG_FLAGS=01700000000000000000000000000000&quot; duration=&quot;0:05:54.560&quot; bitsPerSample=&quot;16&quot; sampleFrequency=&quot;44100&quot;&gt;http://somehost:9002/music/3151/download.aif&lt;/res&gt;&lt;/item&gt;&lt;/DIDL-Lite&gt;" />
        <CurrentTrackURI val="http://somehost:9002/music/3151/download.flc" />
    </InstanceID>
</Event>
"""  # noqa: E501


def test_parse_av_trasnport_event():
    info = PlaybackInfo()
    assert info.album != "SomeAlbum"
    assert info.artist != "SomeArtist"
    assert info.title != "SomeTitle"

    some_value_changed = update_playback_info_from_event(info, av_last_change_event)
    assert info.album == "SomeAlbum"
    assert info.artist == "SomeArtist"
    assert info.title == "SomeTitle"
    assert some_value_changed is True


# @pytest.mark.asyncio
# async def test_renderer_creation():
#     device = UpnpMediaRendererDevice()
#     # setup some fake return values, different from the default mock values, to explicitly check if they are used
#     device.rendering_control.action('GetVolume').mock.return_value = {'CurrentVolume': 42}
#     renderer = await create_media_renderer(cast(async_upnp_client.UpnpDevice, device))
#     info = renderer.playback_info
#
#     assert info.volume_percent == 42
#
#
# class MockedNotificationBackend(object):
#     subscribe = AsyncMock(name='subscribe')
#     unsubscribe = AsyncMock(name='unsubscribe')
#
#
# @pytest.mark.asyncio
# async def test_notification_subscrition():
#     device = UpnpMediaRendererDevice()
#     notification_backend = MockedNotificationBackend()
#     renderer = await create_media_renderer(cast(async_upnp_client.UpnpDevice, device),
#                                            notification_backend=cast(Any, notification_backend))
#
#     callback1 = mock.Mock()
#     callback2 = mock.Mock()
#     subscription1 = await renderer.subscribe_notifcations(callback1)
#     notification_backend.subscribe.assert_has_calls(
#         [mock.call(device.rendering_control), mock.call(device.connection_manager)], any_order=True)
#     notification_backend.unsubscribe.assert_not_called()
#
#     notification_backend.subscribe.reset_mock()
#     notification_backend.unsubscribe.reset_mock()
#
#     subscription2 = await renderer.subscribe_notifcations(callback2)
#     # already another subscription, do nothing
#     notification_backend.subscribe.assert_not_called()
#     notification_backend.unsubscribe.assert_not_called()
#
#     await subscription1.unsubscribe()
#     # still one subscription prending, do nothing
#     notification_backend.subscribe.assert_not_called()
#     notification_backend.unsubscribe.assert_not_called()
#
#     await subscription2.unsubscribe()
#     # last notification subscription cancels upnp backend subscription
#     notification_backend.subscribe.assert_not_called()
#     notification_backend.unsubscribe.assert_has_calls(
#         [mock.call(device.rendering_control), mock.call(device.connection_manager)], any_order=True)
#
#
# class FakeStateVariable(object):
#     def __init__(self, name, value):
#         self.name = name
#         self.value = value
#
#
# @pytest.mark.asyncio
# async def test_renderer_handle_backend_events():
#     device = UpnpMediaRendererDevice()
#     renderer = await create_media_renderer(cast(async_upnp_client.UpnpDevice, device), )
#
#     info_cb = AsyncMock()
#     await renderer.subscribe_notifcations(info_cb)
#
#     original_volume_result = await device.rendering_control.action('GetVolume').async_call()
#     assert renderer.playback_info.volume_percent == original_volume_result['CurrentVolume']
#
#     fake_event_data = [
#         FakeStateVariable('foobar', 'shouldBeIgnored'),
#         FakeStateVariable('LastChange', rc_last_change_event)
#     ]
#     renderer._on_event(device.rendering_control, cast(Any, fake_event_data))
#     # _on_event cannot be a coroutine, but creates a task. Ensure this task has a chance to run
#     await asyncio.sleep(0)
#     await asyncio.sleep(0)
#     info_cb.assert_called_once_with(PlaybackInfo(volume_percent=21))
