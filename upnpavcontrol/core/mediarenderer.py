import logging
from .notification_backend import NotificationBackend
from .oberserver import Observable, Subscription
from . import didllite
from .playback.protocol_info import parse_protocol_infos
from async_upnp_client import UpnpStateVariable, UpnpDevice, UpnpService
import defusedxml.ElementTree as etree
from typing import Iterable, Optional, cast
import asyncio
from pydantic import BaseModel
import enum
import xml.dom.minidom
import typing

_logger = logging.getLogger(__name__)


class TransportState(str, enum.Enum):
    STOPPED = 'STOPPED'
    PLAYING = 'PLAYING'
    PAUSED_PLAYBACK = 'PAUSED'
    NO_MEDIA_PRESENT = 'IDLE'


class PlaybackInfo(BaseModel):
    volume_percent: int = 0
    transport: TransportState = TransportState.STOPPED
    title: typing.Optional[str]
    artist: typing.Optional[str]
    album: typing.Optional[str]


_nsmap = {
    'upnp': 'urn:schemas-upnp-org:metadata-1-0/upnp/',
    'dc': 'http://purl.org/dc/elements/1.1/',
    'avt-event': 'urn:schemas-upnp-org:metadata-1-0/AVT/',
    'rcs': 'urn:schemas-upnp-org:metadata-1-0/RCS/'
}


def prettify_xml(xml_frame):
    dom = xml.dom.minidom.parseString(xml_frame)
    return dom.toprettyxml()


def _set_current_track_metadata(xml: str, info: PlaybackInfo):
    didl = didllite.from_xml_string(xml)
    changed = False
    if len(didl) > 0:
        current = didl[0]
        if current.upnpclass.startswith('object.item.audioItem.musicTrack'):
            current = cast(didllite.MusicTrack, current)
            if current.artist != info.artist:
                info.artist = current.artist
                changed = True
            if current.album != info.album:
                info.album = current.album
                changed = True
            if current.title != info.title:
                info.title = current.title
                changed = True
    return changed


def update_playback_info_from_event(info: PlaybackInfo, event: str) -> bool:
    _logger.debug(event)
    tree = etree.fromstring(event)
    any_value_changed = False
    vol = tree.find("./rcs:InstanceID[@val='0']/rcs:Volume", namespaces=_nsmap)
    if vol is not None:
        value = int(vol.attrib['val'])
        if value != info.volume_percent:
            info.volume_percent = value
            any_value_changed = True
    state = tree.find("./avt-event:InstanceID[@val='0']/avt-event:TransportState", namespaces=_nsmap)
    if state is not None:
        value = TransportState[state.attrib['val']]
        if value != info.transport:
            info.transport = value
            any_value_changed = True
    transportMeta = tree.find("./avt-event:InstanceID[@val='0']/avt-event:CurrentTrackMetaData", namespaces=_nsmap)
    if transportMeta is not None:
        if _set_current_track_metadata(transportMeta.attrib['val'], info):
            any_value_changed = True
    return any_value_changed


async def create_media_renderer(device: UpnpDevice, notification_backend: Optional[NotificationBackend] = None):
    """
    Factory function to create a MediaRenderer.

    Use this function instead of calling `MediaRenderer.__init__()` to construct new MediaRenderers.

    The rationale behind this is that this factory function will use some async functions to update the renderers
    internal state, and `__init__` methods cannot be async.
    """
    renderer = MediaRenderer(device, notification_backend)
    await renderer.update_playback_info()
    await renderer._playback_observable.notify(renderer.playback_info)
    return renderer


class MediaRenderer(object):

    def __init__(self, device: UpnpDevice, notification_backend: Optional[NotificationBackend] = None):
        self._device = device
        self._notify_backend = notification_backend
        self._notifications_enabled = False
        self.rendering_control.on_event = self._on_event
        if self.av_transport is not None:
            self.av_transport.on_event = self._on_event
        self._playback_info = PlaybackInfo()
        self._playback_observable = Observable[PlaybackInfo](replay=True)
        self._playback_observable.on_subscription_change = self._handle_subscription_change

    def _on_event(self, service: UpnpService, variables: Iterable[UpnpStateVariable]):
        for variable in variables:
            logging.info('%s -> %s', variable.name, variable.value)
            if variable.name == 'LastChange':
                any_changes = update_playback_info_from_event(self._playback_info, cast(str, variable.value))
                if any_changes:
                    asyncio.create_task(self._playback_observable.notify(self._playback_info))

    def __repr__(self):
        return '<MediaRenderer {}>'.format(self.friendly_name)

    async def get_volume(self):
        response = await self.rendering_control.action('GetVolume').async_call(InstanceID=0, Channel='Master')
        return response['CurrentVolume']

    async def set_volume(self, value):
        return await self.rendering_control.action('SetVolume').async_call(InstanceID=0,
                                                                           Channel='Master',
                                                                           DesiredVolume=value)

    async def get_protocol_info(self):
        response = await self.connection_manager.async_call_action('GetProtocolInfo')
        data = response['Sink']
        return parse_protocol_infos(data)

    async def subscribe_notifcations(self, subscriber) -> Subscription:
        return await self._playback_observable.subscribe(subscriber)

    async def _handle_subscription_change(self, subscription_count):
        if subscription_count > 0:
            await self._enable_notifications()
        elif subscription_count == 0:
            await self._disable_notifications()

    @property
    def playback_info(self):
        return self._playback_info

    async def update_playback_info(self):
        self._playback_info.volume_percent = await self.get_volume()

    async def _enable_notifications(self):
        if self._notifications_enabled:
            return
        if self._notify_backend is not None:
            self._notifications_enabled = True
            if self.rendering_control:
                await self._notify_backend.subscribe(self.rendering_control)
            if self.av_transport:
                await self._notify_backend.subscribe(self.av_transport)
            if self.connection_manager:
                await self._notify_backend.subscribe(self.connection_manager)

    async def _disable_notifications(self):
        if self._notifications_enabled is False:
            return
        try:
            self._notifications_enabled = False
            if self._notify_backend is not None:
                if self.rendering_control:
                    await self._notify_backend.unsubscribe(self.rendering_control)
                if self.av_transport:
                    await self._notify_backend.unsubscribe(self.av_transport)
                if self.connection_manager:
                    await self._notify_backend.unsubscribe(self.connection_manager)
        except asyncio.TimeoutError:
            logging.warning('Failed to unsubscribe from notifications from %s', self.friendly_name)

    @property
    def udn(self):
        return self.upnp_device.udn.lstrip('uuid:')

    @property
    def rendering_control(self):
        return self._device.service('urn:schemas-upnp-org:service:RenderingControl:1')

    @property
    def av_transport(self):
        if self._device.has_service('urn:schemas-upnp-org:service:AVTransport:1'):
            return self._device.service('urn:schemas-upnp-org:service:AVTransport:1')
        else:
            return None

    @property
    def connection_manager(self):
        return self._device.service('urn:schemas-upnp-org:service:ConnectionManager:1')

    @property
    def friendly_name(self):
        return self._device.friendly_name

    @property
    def upnp_device(self):
        return self._device
