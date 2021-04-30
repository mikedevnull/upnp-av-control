# -*- coding: utf-8 -*-
from upnpavcontrol.core import didllite

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

didl_musictrack2 = """
<DIDL-Lite xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:upnp="urn:schemas-upnp-org:metadata-1-0/upnp/" xmlns:pv="http://www.pv.com/pvns/" xmlns="urn:schemas-upnp-org:metadata-1-0/DIDL-Lite/">
  <item id="/a/176/l/179/t/2836" parentID="/a/176/l/179/t" restricted="1">
    <upnp:class>object.item.audioItem.musicTrack</upnp:class>
    <dc:title>Song Title 1</dc:title>
    <dc:creator>Artist 2</dc:creator>
    <upnp:album>Album 1</upnp:album>
    <upnp:artist role="artist">Song Title 1</upnp:artist>
    <dc:contributor>Artist 1</dc:contributor>
    <upnp:originalTrackNumber>5</upnp:originalTrackNumber>
    <upnp:genre>Keine Stilrichtung</upnp:genre>
    <upnp:albumArtURI xmlns:dlna="urn:schemas-dlna-org:metadata-1-0/" dlna:profileID="JPEG_TN">http://192.168.178.21:9002/music/091ab74a/cover_160x160_m.jpg</upnp:albumArtURI>
    <upnp:albumArtURI>http://192.168.178.21:9002/music/091ab74a/cover</upnp:albumArtURI>
    <pv:modificationTime>1257616464</pv:modificationTime>
    <pv:addedTime>1544479558</pv:addedTime>
    <pv:lastUpdated>1544479558</pv:lastUpdated>
    <res protocolInfo="http-get:*:audio/mpeg:DLNA.ORG_PN=MP3;DLNA.ORG_OP=11;DLNA.ORG_FLAGS=01700000000000000000000000000000" size="4265996" duration="0:04:26.520" bitrate="16000" sampleFrequency="44100">http://192.168.178.21:9002/music/2836/download.mp3?bitrate=320</res>
  </item>
    <item id="/x" parentID="/" restricted="1">
    <upnp:class>object.item.audioItem.musicTrack</upnp:class>
    <dc:title>Foo</dc:title>
    <dc:creator>Artist 2</dc:creator>
    <upnp:album>Album 1</upnp:album>
    <upnp:artist role="artist">Artist 2</upnp:artist>
    <dc:contributor>Artist 2</dc:contributor>
    <upnp:originalTrackNumber>6</upnp:originalTrackNumber>
    <upnp:genre>Keine Stilrichtung</upnp:genre>
    <upnp:albumArtURI xmlns:dlna="urn:schemas-dlna-org:metadata-1-0/" dlna:profileID="JPEG_TN">http://192.168.178.21:9002/music/091ab74a/cover_160x160_m.jpg</upnp:albumArtURI>
    <upnp:albumArtURI>http://192.168.178.21:9002/music/091ab74a/cover</upnp:albumArtURI>
    <pv:modificationTime>1257616464</pv:modificationTime>
    <pv:addedTime>1544479558</pv:addedTime>
    <pv:lastUpdated>1544479558</pv:lastUpdated>
    <res protocolInfo="http-get:*:audio/mpeg:DLNA.ORG_PN=MP3;DLNA.ORG_OP=11;DLNA.ORG_FLAGS=01700000000000000000000000000000" size="4265996" duration="0:04:26.520" bitrate="16000" sampleFrequency="44100">http://192.168.178.21:9002/music/2837/download.mp3?bitrate=320</res>
  </item>
</DIDL-Lite>
"""


def test_didl_container_parse():
    result = list(didllite.from_xml_string(didl1))
    assert len(result) == 3
    assert result[0].id == '29$40850$0'
    assert result[0].parentID == '29$40850'
    assert result[0].title == '= All Songs ='
    assert result[0].upnpclass == 'object.container.album.musicAlbum'
    assert result[1].id == '29$40850$40862'
    assert result[1].parentID == '29$40850'
    assert result[1].title == 'Album1'
    assert result[1].upnpclass == 'object.container.album.musicAlbum'
    assert result[2].id == '29$40850$40850'
    assert result[2].parentID == '29$40850'
    assert result[2].title == 'Album2'
    assert result[2].upnpclass == 'object.container.album.musicAlbum'


def test_didl_musictrack_parse():
    result = list(didllite.from_xml_string(didl_musictrack))
    assert len(result) == 1
    track = result[0]
    assert track.id == '26$40260$@40260'
    assert track.parentID == '26$40260'
    assert track.title == 'SomeTitle'
    assert track.album == 'SomeAlbumTitle'
    assert track.upnpclass == 'object.item.audioItem.musicTrack'


def test_didle_musictracks_parse():
    result = list(didllite.from_xml_string(didl_musictrack2))
    assert len(result) == 2
