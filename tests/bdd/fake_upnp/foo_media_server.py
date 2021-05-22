from .fake_upnp_device import FakeDeviceDescriptor, FakeAsyncUpnpDevice
from .fake_upnp_service import UpnpServiceMock
from .connection_manager import FakeConnectionManagerService

didl_musictrack = """
<DIDL-Lite xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:upnp="urn:schemas-upnp-org:metadata-1-0/upnp/" xmlns:pv="http://www.pv.com/pvns/" xmlns="urn:schemas-upnp-org:metadata-1-0/DIDL-Lite/">
  <item id="/0/2/2" parentID="/0/2" restricted="1">
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
</DIDL-Lite>
""" # noqa: 501

_descriptor = FakeDeviceDescriptor(name="FooMedia",
                                   friendly_name="Foo MediaServer",
                                   location='http://192.168.99.2:9200/plugins/MediaServer.xml',
                                   udn='f5b1b596-c1d2-11e9-af8b-705681aa5dfd',
                                   device_type='MediaServer',
                                   service_types=['ContentDirectory:1', 'ConnectionManager:1'])


class FakeContentDirectoryService(UpnpServiceMock):
    def __init__(self, device):
        super().__init__(service_type="urn:schemas-upnp-org:service:ContentDirectory:1", device=device)
        self.add_async_action('Browse', self._browse)

    async def _browse(self, ObjectID, BrowseFlag, StartingIndex, RequestedCount, SortCriteria, Filter):
        return {'Result': didl_musictrack, 'NumberReturned': 1, 'TotalMatches': 1, 'UpdateID': 1}


def factory():
    device = FakeAsyncUpnpDevice(_descriptor)
    cm = FakeConnectionManagerService(device)
    cm.sink_protocols = ''
    device.mock_add_service(cm)
    device.mock_add_service(FakeContentDirectoryService(device))
    return device
