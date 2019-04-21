# -*- coding: utf-8 -*-
from upnpavcontrol.mediaserver import didllite

didl1 = """
<DIDL-Lite xmlns="urn:schemas-upnp-org:metadata-1-0/DIDL-Lite/" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:upnp="urn:schemas-upnp-org:metadata-1-0/upnp/" xmlns:sec="http://www.sec.co.kr/" xmlns:dlna="urn:schemas-dlna-org:metadata-1-0/">
<container id="29$40850$0"  parentID="29$40850"  restricted="1">
<dc:title>= All Songs =</dc:title>
<upnp:class>object.container.album.musicAlbum</upnp:class>
</container>
<container id="29$40850$40862"  parentID="29$40850"  restricted="1">
<dc:title>Album1</dc:title>
<upnp:class>object.container.album.musicAlbum</upnp:class>
<upnp:artist>Artist1</upnp:artist>
<upnp:album>Album1</upnp:album><upnp:albumArtURI dlna:profileID="JPEG_TN">http://192.168.2.250:50002/transcoder/jpegtnscaler.cgi/albumart/40862.jpg</upnp:albumArtURI>
</container>
<container id="29$40850$40850"  parentID="29$40850"  restricted="1">
<dc:title>Album2</dc:title>
<upnp:class>object.container.album.musicAlbum</upnp:class>
<upnp:artist>Artist1</upnp:artist>
<upnp:album>Album2</upnp:album><upnp:albumArtURI dlna:profileID="JPEG_TN">http://192.168.2.250:50002/transcoder/jpegtnscaler.cgi/albumart/40850.jpg</upnp:albumArtURI></container>
</DIDL-Lite>
"""  # noqa

didl_musictrack = """
<DIDL-Lite xmlns="urn:schemas-upnp-org:metadata-1-0/DIDL-Lite/" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:upnp="urn:schemas-upnp-org:metadata-1-0/upnp/" xmlns:sec="http://www.sec.co.kr/" xmlns:dlna="urn:schemas-dlna-org:metadata-1-0/"><item id="26$40260$@40260" parentID="26$40260" restricted="1">
<dc:title>SomeTitle</dc:title>
<upnp:class>object.item.audioItem.musicTrack</upnp:class>
<dc:date>2015-01-01</dc:date><upnp:album>SomeAlbumTitle</upnp:album><upnp:artist>SomeArtist</upnp:artist><dc:creator>SomeArtist</dc:creator><upnp:genre>Alternative</upnp:genre><upnp:author>SomeArtist</upnp:author><upnp:originalTrackNumber>1</upnp:originalTrackNumber><upnp:albumArtURI dlna:profileID="JPEG_TN">http://192.168.0.1:123456/ebdart/40260.jpg</upnp:albumArtURI><res  protocolInfo="http-get:*:audio/mp4:*" size="4161945" bitrate="16000" duration="0:04:08.000" nrAudioChannels="2" sampleFrequency="44100">http://192.168.0.1:123456/NDLNA/40260.m4a</res></item>
</DIDL-Lite>
"""  # noqa 501


def test_didl_container_parse():
    result = list(didllite.parse(didl1))
    assert len(result) == 3
    assert result[0] == didllite.BaseObject(
        id='29$40850$0',
        parentID='29$40850',
        title='= All Songs =',
        upnpclass='object.container.album.musicAlbum')
    assert result[1] == didllite.BaseObject(
        id='29$40850$40862',
        parentID='29$40850',
        title='Album1',
        upnpclass='object.container.album.musicAlbum')
    assert result[2] == didllite.BaseObject(
        id='29$40850$40850',
        parentID='29$40850',
        title='Album2',
        upnpclass='object.container.album.musicAlbum')


def test_didl_musictrack_parse():
    result = list(didllite.parse(didl_musictrack))
    assert len(result) == 1
    track = result[0]
    assert track.id == '26$40260$@40260'
    assert track.parentID == '26$40260'
    assert track.title == 'SomeTitle'
    assert track.album == 'SomeAlbumTitle'
    assert track.upnpclass == 'object.item.audioItem.musicTrack'
