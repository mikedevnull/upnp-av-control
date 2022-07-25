import pytest
import pytest_asyncio
from unittest import mock
from async_upnp_client.ssdp_listener import SsdpListener, SsdpDevice, SsdpSource
from upnpavcontrol.core.discovery.events import DiscoveryEvent, DiscoveryEventType, create_discovery_event_observable
from upnpavcontrol.core.discovery.events import filter_lost_device_events, filter_new_device_events
from upnpavcontrol.core.discovery.events import filter_mediarenderer_events, filter_mediaserver_events
import reactivex as rx
import asyncio
import datetime
from typing import Callable, Awaitable
from dataclasses import dataclass
from ..testsupport.asyncmock_stub import AsyncMock


@pytest.mark.asyncio
async def test_subscribe_dispose_starts_and_stops_listener():
    mockListener = mock.create_autospec(SsdpListener, spec_set=True, instance=True)
    mockListener.async_start = AsyncMock()
    mockListener.async_stop = AsyncMock()
    listenerFactory = mock.Mock(return_value=mockListener)

    events = create_discovery_event_observable(listenerFactory=listenerFactory)

    observerMock = mock.Mock(spec=rx.abc.ObserverBase)
    subscription = events.subscribe(observerMock,
                                    scheduler=rx.scheduler.eventloop.AsyncIOScheduler(loop=asyncio.get_running_loop()))

    await asyncio.sleep(0)

    listenerFactory.assert_called_once()
    mockListener.async_start.assert_called_once()

    subscription.dispose()
    await asyncio.sleep(0)

    mockListener.async_stop.assert_called_once()


@dataclass(frozen=True)
class SubscribedObservableContext(object):
    events: rx.Observable
    event_trigger_cb: Callable[[SsdpDevice, str, SsdpSource], Awaitable]
    observer_mock: mock.Mock


@pytest_asyncio.fixture
async def subscribed_observable():
    mockListener = mock.create_autospec(SsdpListener, spec_set=True, instance=True)
    mockListener.async_start = AsyncMock()
    mockListener.async_stop = AsyncMock()
    listenerFactory = mock.Mock(return_value=mockListener)

    events = create_discovery_event_observable(listenerFactory=listenerFactory)

    observerMock = mock.Mock(spec=rx.abc.ObserverBase)
    subscription = events.subscribe(observerMock,
                                    scheduler=rx.scheduler.eventloop.AsyncIOScheduler(loop=asyncio.get_running_loop()))

    await asyncio.sleep(0)
    listenerFactory.assert_called_once()
    event_trigger_cb = listenerFactory.call_args[0][0]

    yield SubscribedObservableContext(events, event_trigger_cb, observerMock)

    subscription.dispose()


@pytest.mark.parametrize("source_event_type,mapped_event_type",
                         [(SsdpSource.ADVERTISEMENT_ALIVE, DiscoveryEventType.NEW_DEVICE),
                          (SsdpSource.ADVERTISEMENT_BYEBYE, DiscoveryEventType.DEVICE_LOST),
                          (SsdpSource.SEARCH_CHANGED, DiscoveryEventType.NEW_DEVICE)])
@pytest.mark.asyncio
async def test_maps_event_types(subscribed_observable: SubscribedObservableContext, source_event_type: SsdpSource,
                                mapped_event_type: DiscoveryEventType):
    fakedevice = SsdpDevice('fake-udn', datetime.datetime.now())
    fakedevice.add_location('some-fake-location', datetime.datetime.now())

    await subscribed_observable.event_trigger_cb(fakedevice, 'urn:schemas-upnp-org:device:MediaServer:1',
                                                 source_event_type)

    await asyncio.sleep(0)

    subscribed_observable.observer_mock.on_next.assert_called_once_with(
        DiscoveryEvent(mapped_event_type, 'urn:schemas-upnp-org:device:MediaServer:1', fakedevice.udn))


@pytest.mark.parametrize("source_event_type", [SsdpSource.ADVERTISEMENT_UPDATE, SsdpSource.SEARCH_ALIVE])
@pytest.mark.asyncio
async def test_ignores_unwanted_events(subscribed_observable: SubscribedObservableContext,
                                       source_event_type: SsdpSource):
    fakedevice = SsdpDevice('fake-udn', datetime.datetime.now())
    fakedevice.add_location('some-fake-location', datetime.datetime.now())

    await subscribed_observable.event_trigger_cb(fakedevice, 'urn:schemas-upnp-org:device:MediaServer:1',
                                                 source_event_type)

    await asyncio.sleep(0)

    subscribed_observable.observer_mock.on_next.assert_not_called()


@pytest.mark.parametrize("device_type, expect_event", [("urn:schemas-upnp-org:device:MediaServer:1", True),
                                                       ("urn:schemas-upnp-org:device:MediaServer:3", True),
                                                       ("urn:schemas-upnp-org:device:MediaRenderer:1", True),
                                                       ("urn:schemas-upnp-org:device:MediaRenderer:2", True),
                                                       ("upnp::rootdevice", False),
                                                       ("urn:schemas-upnp-org:service:AVTransport:1", False),
                                                       ("urn:schemas-upnp-org:service:RenderingControl:1", False)])
@pytest.mark.asyncio
async def test_filters_media_devices(subscribed_observable: SubscribedObservableContext, device_type: str,
                                     expect_event: bool()):
    fakedevice = SsdpDevice('fake-udn', datetime.datetime.now())
    fakedevice.add_location('some-fake-location', datetime.datetime.now())

    await subscribed_observable.event_trigger_cb(fakedevice, device_type, SsdpSource.ADVERTISEMENT_ALIVE)

    await asyncio.sleep(0)

    if expect_event:
        subscribed_observable.observer_mock.on_next.assert_called_once()
    else:
        subscribed_observable.observer_mock.on_next.assert_not_called()


@pytest.fixture
def events_to_be_filtered():
    return rx.of(
        DiscoveryEvent(event_type=DiscoveryEventType.NEW_DEVICE,
                       device_type='urn:schemas-upnp-org:device:MediaServer:1',
                       udn='1'),
        DiscoveryEvent(event_type=DiscoveryEventType.NEW_DEVICE,
                       device_type='urn:schemas-upnp-org:device:MediaRenderer:1',
                       udn='2'),
        DiscoveryEvent(event_type=DiscoveryEventType.DEVICE_LOST,
                       device_type='urn:schemas-upnp-org:device:MediaServer:1',
                       udn='3'),
        DiscoveryEvent(event_type=DiscoveryEventType.DEVICE_LOST,
                       device_type='urn:schemas-upnp-org:device:MediaRenderer:1',
                       udn='4'))


def test_event_filter_new_devices(events_to_be_filtered):
    obs = mock.Mock(spec=rx.abc.ObserverBase)
    events_to_be_filtered.pipe(filter_new_device_events()).subscribe(obs)
    assert obs.on_next.call_count == 2
    obs.on_next.assert_has_calls([
        mock.call(
            DiscoveryEvent(event_type=DiscoveryEventType.NEW_DEVICE,
                           device_type='urn:schemas-upnp-org:device:MediaServer:1',
                           udn='1')),
        mock.call(
            DiscoveryEvent(event_type=DiscoveryEventType.NEW_DEVICE,
                           device_type='urn:schemas-upnp-org:device:MediaRenderer:1',
                           udn='2'))
    ])


def test_event_filter_lost_devices(events_to_be_filtered):
    obs = mock.Mock(spec=rx.abc.ObserverBase)
    events_to_be_filtered.pipe(filter_lost_device_events()).subscribe(obs)
    assert obs.on_next.call_count == 2
    obs.on_next.assert_has_calls([
        mock.call(
            DiscoveryEvent(event_type=DiscoveryEventType.DEVICE_LOST,
                           device_type='urn:schemas-upnp-org:device:MediaServer:1',
                           udn='3')),
        mock.call(
            DiscoveryEvent(event_type=DiscoveryEventType.DEVICE_LOST,
                           device_type='urn:schemas-upnp-org:device:MediaRenderer:1',
                           udn='4'))
    ])


def test_event_filter_renderer_devices(events_to_be_filtered):
    obs = mock.Mock(spec=rx.abc.ObserverBase)
    events_to_be_filtered.pipe(filter_mediarenderer_events()).subscribe(obs)
    assert obs.on_next.call_count == 2
    obs.on_next.assert_has_calls([
        mock.call(
            DiscoveryEvent(event_type=DiscoveryEventType.NEW_DEVICE,
                           device_type='urn:schemas-upnp-org:device:MediaRenderer:1',
                           udn='2')),
        mock.call(
            DiscoveryEvent(event_type=DiscoveryEventType.DEVICE_LOST,
                           device_type='urn:schemas-upnp-org:device:MediaRenderer:1',
                           udn='4'))
    ])


def test_event_filter_server_devices(events_to_be_filtered):
    obs = mock.Mock(spec=rx.abc.ObserverBase)
    events_to_be_filtered.pipe(filter_mediaserver_events()).subscribe(obs)
    assert obs.on_next.call_count == 2
    obs.on_next.assert_has_calls([
        mock.call(
            DiscoveryEvent(event_type=DiscoveryEventType.NEW_DEVICE,
                           device_type='urn:schemas-upnp-org:device:MediaServer:1',
                           udn='1')),
        mock.call(
            DiscoveryEvent(event_type=DiscoveryEventType.DEVICE_LOST,
                           device_type='urn:schemas-upnp-org:device:MediaServer:1',
                           udn='3')),
    ])
