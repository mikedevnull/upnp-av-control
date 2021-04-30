from upnpavcontrol import core
import pytest
from ..testsupport import AsyncMock
from unittest import mock


def test_parse_protocol_infos():
    test_data = """http-get:*:audio/mpeg:*,http-get:*:audio/L16;rate=8000;channels=1:*,http-get:*:audio/x-flac:*"""

    infos = core.parse_protocol_infos(test_data)
    assert len(infos) == 3

    assert infos[0].protocol == 'http-get'
    assert infos[0].network == '*'
    assert infos[0].content_format.mimetype == 'audio/mpeg'
    assert len(infos[0].content_format.meta) == 0
    assert infos[0].additional_info == '*'

    assert infos[1].protocol == 'http-get'
    assert infos[1].network == '*'
    assert infos[1].content_format.mimetype == 'audio/L16'
    assert len(infos[1].content_format.meta) == 2
    assert infos[1].content_format.meta['rate'] == '8000'
    assert infos[1].content_format.meta['channels'] == '1'
    assert infos[1].additional_info == '*'

    assert infos[2].protocol == 'http-get'
    assert infos[2].network == '*'
    assert infos[2].content_format.mimetype == 'audio/x-flac'
    assert len(infos[2].content_format.meta) == 0
    assert infos[2].additional_info == '*'


def test_parse_protocol_infos_discards_unsupported_and_illegal_entries():
    test_data = """http-put:*:audio/mpeg:*,http-get:foo:audio/L16;rate=8000;channels=1:*,http-get:*:audio/x-flac:*"""
    infos = core.parse_protocol_infos(test_data)
    assert len(infos) == 1

    assert infos[0].protocol == 'http-get'
    assert infos[0].network == '*'
    assert infos[0].content_format.mimetype == 'audio/x-flac'
    assert len(infos[0].content_format.meta) == 0
    assert infos[0].additional_info == '*'


@pytest.mark.parametrize("info1_str,info2_str,expected_result",
                         [('http-get:*:audio/mpeg:*', 'http-get:*:audio/mpeg:*', True),
                          ('http-get:*:audio/x-flac:*', 'http-get:*:audio/mpeg:*', False),
                          ('http-get:*:audio/x-flac:*', 'http-get:*:audio/x-flac:*', True),
                          ('foo:*:audio/x-flac:*', 'http-get:*:audio/x-flac:*', False),
                          ('foo:*:audio/x-flac:*', 'http-get:bar:audio/x-flac:*', False),
                          ('rtsp-rtp-udp:*:audio/x-flac:*', 'rtsp-rtp-udp:*:audio/x-flac:*', True),
                          ('rtsp-rtp-udp:*:audio/mpeg:*', 'http-get:*:audio/mpeg:*', False)])
def test_parse_protocol_info_match(info1_str, info2_str, expected_result):

    info1 = core.ProtocolInfoEntry.fromstring(info1_str)
    info2 = core.ProtocolInfoEntry.fromstring(info2_str)
    assert core.protocol_info_matches(info1, info2) == expected_result


class DmrMock(object):
    pass


class DmsMock(object):
    pass


class FakePlaybackItem(object):
    data = {'@protocolInfo': 'http-get:*:audio/mpeg:*', '#text': 'someURI'}
    res = [core.didllite.Resource.parse_obj(data)]


@pytest.mark.asyncio
async def test_play():
    object_id = '23456'
    dms = DmsMock()
    dms.connection_manager = mock.Mock()
    dms.connection_manager.has_action = mock.Mock(return_value=False)

    fake_didl = core.didllite.DidlLite('xmldata')
    fake_didl._objects = [FakePlaybackItem()]
    dms.browse_metadata = AsyncMock(return_value=fake_didl)

    dmr = DmrMock()
    dmr.get_protocol_info = AsyncMock(return_value=core.parse_protocol_infos('http-get:*:audio/mpeg:*'))
    dmr.connection_manager = mock.Mock()
    dmr.connection_manager.has_action = mock.Mock(return_value=False)

    dmr.av_transport = mock.Mock()
    dmr.av_transport.async_call_action = AsyncMock()

    await core.playback.play(dms, object_id, dmr)

    dms.browse_metadata.assert_called_once_with(object_id)
    call1 = mock.call('SetAVTransportURI', InstanceID=0, CurrentURI='someURI', CurrentURIMetaData='xmldata')
    call2 = mock.call('Play', InstanceID=0, Speed='1')
    dmr.av_transport.async_call_action.assert_has_calls([call1, call2])
