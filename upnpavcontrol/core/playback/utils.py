from dataclasses import dataclass
import typing
from .queue import PlaybackItem
from .protocol_info import match_resources
from ..oberserver import Subscription

from async_upnp_client.exceptions import UpnpActionResponseError
import logging
if typing.TYPE_CHECKING:
    from .. import MediaRenderer, MediaServer
    from ..mediarenderer import PlaybackInfo

_logger = logging.getLogger(__name__)


@dataclass
class PreparedConnection(object):
    connection_id: int
    av_transport_id: int
    rcs_id: int


def prepare_for_connection(dmr: 'MediaRenderer', dms: 'MediaServer') -> PreparedConnection:  # noqa F812
    # this is a stub, needs a proper implementation for devices that support PrepareForConnection
    if dmr.connection_manager.has_action('PrepareForConnection'):
        raise NotImplementedError('prepare for connection handling not yet implemented')
    if dms.connection_manager.has_action('PrepareForConnection'):
        raise NotImplementedError('prepare for connection handling not yet implemented')
    return PreparedConnection(connection_id=0, av_transport_id=0, rcs_id=0)


async def play(dms: 'MediaServer', object_id: str, dmr: 'MediaRenderer'):  # noqa F812
    if dmr.av_transport is None:
        _logger.error('Renderer %s has no AV Transport service', dmr.friendly_name)
        raise RuntimeError("Failed to play without transport service")
    didl = await dms.browse_metadata(object_id)
    playbackitem = didl.objects[0]
    assert len(didl.objects) == 1
    playback_meta = didl.xml
    dmr_protocol_info = await dmr.get_protocol_info()
    resources = match_resources(playbackitem.res, dmr_protocol_info)
    assert len(resources) > 0
    play_resource = resources[0]
    connection = prepare_for_connection(dmr, dms)
    try:
        await dmr.av_transport.async_call_action(
            'SetAVTransportURI',  # type: ignore
            InstanceID=connection.av_transport_id,
            CurrentURI=play_resource.uri,
            CurrentURIMetaData=playback_meta)
        await dmr.av_transport.async_call_action(
            'Play',  # type: ignore
            InstanceID=connection.av_transport_id,
            Speed="1")
    except UpnpActionResponseError as e:
        _logger.exception(e)
        _logger.debug("%s (%s)", e.error_desc, e.error_code)
        raise e

    return connection


class PlaybackControllableWrapper(object):
    DmsLookupCallable = typing.Callable[[str], 'MediaServer']

    def __init__(self, renderer: 'MediaRenderer', dmsLookup: DmsLookupCallable):
        self._renderer = renderer
        self._lookupDms = dmsLookup
        self._connection = None

    async def play(self, item: PlaybackItem):
        dms = self._lookupDms(item.dms)
        self._connection = await play(dms, item.object_id, self._renderer)

    async def stop(self):
        if self._connection is not None and self._renderer.av_transport is not None:
            await self._renderer.av_transport.async_call_action(
                'Stop',  # type: ignore
                InstanceID=self._connection.av_transport_id)
            self._connection = None

    async def subscribe(self, callback: typing.Callable[['PlaybackInfo'], typing.Awaitable[None]]) -> Subscription:
        return await self._renderer.subscribe_notifcations(callback)
