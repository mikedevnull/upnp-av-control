from .fake_upnp_service import UpnpServiceMock
from upnpavcontrol.core import didllite
import enum


class PlaybackState(str, enum.Enum):
    STOPPED = 'STOPPED'
    PLAYING = 'PLAYING'
    PAUSED_PLAYBACK = 'PAUSED_PLAYBACK'


class FakeAVTransportService(UpnpServiceMock):

    def __init__(self, device):
        super().__init__(service_type="urn:schemas-upnp-org:service:AVTransport:1", device=device)
        self.add_async_action('SetAVTransportURI', self._set_transport)
        self.add_async_action('Play', self._play)
        self.state = PlaybackState.STOPPED
        self.current_uri = None
        self._current_uri_metadata = None
        self._active_resource = None

    async def _ext_set_transport_state(self, state: PlaybackState):
        self.state = state
        await self.trigger_notification(instance_xml_namespace='{urn:schemas-upnp-org:metadata-1-0/AVT/}',
                                        variables={'TransportState': self.state})

    async def _set_transport(self, InstanceID, CurrentURI, CurrentURIMetaData):
        meta = didllite.DidlLite(CurrentURIMetaData)
        item = meta.objects[0]
        active_resource = None
        for resource in item.res:
            if resource.uri == CurrentURI:
                active_resource = resource
                break
        assert active_resource is not None
        self._active_resource = active_resource
        self.current_uri = CurrentURI
        self._current_uri_metadata = CurrentURIMetaData
        self._playback_task = None

    async def _play(self, InstanceID, Speed):
        if self._active_resource is None:
            return
        if self.state != PlaybackState.PLAYING:
            self.state = PlaybackState.PLAYING
            await self.trigger_notification(instance_xml_namespace='{urn:schemas-upnp-org:metadata-1-0/AVT/}',
                                            variables={'TransportState': self.state.value})
