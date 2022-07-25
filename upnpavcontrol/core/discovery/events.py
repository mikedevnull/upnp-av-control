from enum import Enum
from dataclasses import dataclass
import typing
from .utils import is_media_device, is_media_renderer, is_media_server
from async_upnp_client.ssdp_listener import SsdpListener, SsdpDevice
from async_upnp_client.const import SsdpSource
import reactivex as rx
import reactivex.operators as rxops
import reactivex.disposable as rxdisposable
from reactivex.typing import Action
import asyncio
import logging

_logger = logging.getLogger(__name__)


class DiscoveryEventType(Enum):
    """
    Different type of upnp events that might occur
    """
    NEW_DEVICE = 'NEW_DEVICE'
    DEVICE_UPDATE = 'DEVICE_UPDATE'
    DEVICE_LOST = 'DEVICE_LOST'


@dataclass(frozen=True)
class DiscoveryEvent:
    """
    Provides all required information to handle discovery
    events in a uniform way.
    This includes advertisements via SSDP (alive, update, bybye) and
    but also responses to search requests.

    Attributes
    ----------
    event_type : DiscoveryEventType
        The type of discovery represented by this event
    device_type : str
        A UPnP device type descriptor of the form 'urn:schemas-upnp-org:device:{deviceType}:{ver}'
    udn : str
        UUID of the device
    location: str or None
        URL to the UPnP description of the device. Only available for `NEW_DEVICE` or `DEVICE_UPDATE`
        event types.
    """
    event_type: DiscoveryEventType
    device_type: str
    udn: str
    location: typing.Optional[str] = None


def filter_mediarenderer_events():
    f: typing.Callable[[DiscoveryEvent], bool] = lambda e: is_media_renderer(e.device_type)
    return rxops.filter(f)


def filter_mediaserver_events():
    f: typing.Callable[[DiscoveryEvent], bool] = lambda e: is_media_server(e.device_type)
    return rxops.filter(f)


def filter_new_device_events():
    f: typing.Callable[[DiscoveryEvent], bool] = lambda e: e.event_type == DiscoveryEventType.NEW_DEVICE
    return rxops.filter(f)


def filter_lost_device_events():
    f: typing.Callable[[DiscoveryEvent], bool] = lambda e: e.event_type == DiscoveryEventType.DEVICE_LOST
    return rxops.filter(f)


@dataclass(frozen=True)
class _SsdpRawEvent(object):
    device: SsdpDevice
    device_or_service_type: str
    source: SsdpSource


def to_discovery_event(raw_event: _SsdpRawEvent) -> DiscoveryEvent:
    _type_mapping = {
        SsdpSource.SEARCH_CHANGED: DiscoveryEventType.NEW_DEVICE,
        SsdpSource.ADVERTISEMENT_ALIVE: DiscoveryEventType.NEW_DEVICE,
        SsdpSource.ADVERTISEMENT_BYEBYE: DiscoveryEventType.DEVICE_LOST,
    }
    return DiscoveryEvent(event_type=_type_mapping[raw_event.source],
                          device_type=raw_event.device_or_service_type,
                          udn=raw_event.device.udn.lstrip('uuid:'),
                          location=raw_event.device.location)


def create_discovery_event_observable(loop: typing.Optional[asyncio.AbstractEventLoop] = None,
                                      listenerFactory=None) -> rx.Observable[DiscoveryEvent]:

    def _on_subscribe(observer: rx.abc.ObserverBase[_SsdpRawEvent], scheduler: typing.Optional[rx.abc.SchedulerBase]):

        async def on_listener_callback(device: SsdpDevice, dtype, source: SsdpSource):
            observer.on_next(_SsdpRawEvent(device, dtype, source))

        activeloop = loop or asyncio.get_running_loop()

        create_listener = listenerFactory or SsdpListener
        listener = create_listener(on_listener_callback, loop=activeloop)

        async def startup():
            await listener.async_start()
            await listener.async_search()

        async def shutdown():
            await listener.async_stop()

        task = activeloop.create_task(startup())
        task_cancel = rxdisposable.Disposable(typing.cast(Action, task.cancel))
        listener_stop = rxdisposable.Disposable(typing.cast(Action, lambda: activeloop.create_task(shutdown())))
        return rxdisposable.CompositeDisposable(task_cancel, listener_stop)

    return rx.create(_on_subscribe).pipe(
        rxops.do_action(lambda x: _logger.debug(x)),
        rxops.filter(lambda e: e.source in
                     (SsdpSource.ADVERTISEMENT_ALIVE, SsdpSource.ADVERTISEMENT_BYEBYE, SsdpSource.SEARCH_CHANGED)),
        rxops.filter(
            lambda e: is_media_device(e.device_or_service_type) or e.source == SsdpSource.ADVERTISEMENT_BYEBYE),
        rxops.map(to_discovery_event))
