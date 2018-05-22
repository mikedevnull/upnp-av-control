from UpnpAVControl.mediaserver import didllite


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


def test_didl_container_parse():
    result = list(didllite.parse(didl1))
    assert len(result) == 3
    assert result[0] == didllite.BaseObject(
        id='29$40850$0', parentID='29$40850', title='= All Songs =',
        upnpclass='object.container.album.musicAlbum')
    assert result[1] == didllite.BaseObject(
        id='29$40850$40862', parentID='29$40850', title='Album1',
        upnpclass='object.container.album.musicAlbum')
    assert result[2] == didllite.BaseObject(
        id='29$40850$40850', parentID='29$40850', title='Album2',
        upnpclass='object.container.album.musicAlbum')
