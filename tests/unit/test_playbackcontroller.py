import pytest
from upnpavcontrol.core.playback.controller import PlaybackController, PlaybackItem, TransportState
from upnpavcontrol.core.oberserver import Observable
from upnpavcontrol.core.mediarenderer import PlaybackInfo
import unittest.mock as mock
import typing


class FakePlayerInterface():
    def __init__(self):
        self.play = mock.AsyncMock(side_effect=self._do_play)
        self.stop = mock.AsyncMock(side_effect=self._do_stop)
        self.subscribe = mock.AsyncMock(side_effect=self._do_subscribe)
        self._state = PlaybackInfo()
        self._state.transport = TransportState.STOPPED
        self._state_observable = Observable[PlaybackInfo]()
        self._state_subscription_count = 0

        self._state_observable.on_subscription_change = self._do_set_subscription_count

    @property
    def state_subscription_count(self):
        return self._state_subscription_count

    async def _do_subscribe(self, callback: typing.Callable[[PlaybackInfo], typing.Awaitable[None]]):
        return await self._state_observable.subscribe(callback)

    async def fake_stopped_event(self):
        await self._change_transport_state(TransportState.STOPPED)

    async def _do_play(self, item):
        await self._change_transport_state(TransportState.PLAYING)
        return True

    async def _do_stop(self):
        await self._change_transport_state(TransportState.STOPPED)

    async def _do_set_subscription_count(self, x):
        self._state_subscription_count = x

    async def _change_transport_state(self, state):
        if self._state.transport != state:
            self._state.transport = state
            await self._state_observable.notify(self._state)


class FakePlaybackQueue(list):
    def next_item(self) -> typing.Optional[PlaybackItem]:
        if len(self) == 0:
            return None
        return self.pop(0)


@pytest.fixture
def queueWithItems():
    queue = FakePlaybackQueue()
    item1 = PlaybackItem(dms='1234', object_id='9876', title='First song')
    item2 = PlaybackItem(dms='1234', object_id='9876', title='First song')
    queue.append(item1)
    queue.append(item2)
    return queue


@pytest.mark.asyncio
async def test_empty_queue_play_nothing_happens():
    player = FakePlayerInterface()
    queue = FakePlaybackQueue()
    controller = PlaybackController(queue)
    await controller.setup_player(player)
    assert not controller.is_playing
    assert len(controller.queue) == 0

    await controller.play()

    player.play.assert_not_called()
    player.stop.assert_not_called()
    player.subscribe.assert_not_called()
    assert not controller.is_playing


@pytest.mark.asyncio
async def test_stopped_device_play_device_starts_playing(queueWithItems):
    player = FakePlayerInterface()
    item1 = queueWithItems[0]
    controller = PlaybackController(queueWithItems)
    await controller.setup_player(player)

    await controller.play()

    player.subscribe.assert_called_once()
    player.play.assert_called_with(item1)
    assert controller.is_playing


@pytest.mark.asyncio
async def test_playing_device_play_nothing_happens(queueWithItems):
    player = FakePlayerInterface()
    controller = PlaybackController(queueWithItems)
    await controller.setup_player(player)

    await controller.play()
    assert controller.is_playing

    await controller.play()
    player.play.assert_called_once()  # only call on first play()
    player.subscribe.assert_called_once()  # only call on first play()
    player.stop.assert_not_called()
    assert controller.is_playing


@pytest.mark.asyncio
async def test_playing_song_finishes_next_item_is_player(queueWithItems):
    player = FakePlayerInterface()

    controller = PlaybackController(queueWithItems)
    await controller.setup_player(player)
    item1 = queueWithItems[0]
    item2 = queueWithItems[1]
    await controller.play()
    player.play.assert_called_with(item1)
    player.subscribe.assert_called_once()

    assert len(queueWithItems) == 1
    assert controller.is_playing
    player.play.reset_mock()

    await player.fake_stopped_event()
    player.play.assert_called_with(item2)
    assert len(queueWithItems) == 0
    assert controller.is_playing


@pytest.mark.asyncio
async def test_starting_first_playback_fails_player_never_starts(queueWithItems):
    player = FakePlayerInterface()

    controller = PlaybackController(queueWithItems)
    await controller.setup_player(player)
    item1 = queueWithItems[0]

    player.play.return_value = False
    player.play.side_effect = None
    await controller.play()
    player.play.assert_called_with(item1)
    player.subscribe.assert_called_once()
    assert len(queueWithItems) == 1
    assert not controller.is_playing
    player.play.assert_called_once()
    assert player.state_subscription_count == 0


@pytest.mark.asyncio
async def test_starting_playback_fails_playback_stops(queueWithItems):
    player = FakePlayerInterface()

    controller = PlaybackController(queueWithItems)
    await controller.setup_player(player)
    item1 = queueWithItems[0]
    item2 = queueWithItems[1]

    await controller.play()
    player.play.assert_called_with(item1)
    player.subscribe.assert_called_once()
    assert controller.is_playing
    player.play.reset_mock()

    player.play.return_value = False
    player.play.side_effect = None

    await player.fake_stopped_event()
    player.play.assert_called_with(item2)
    assert player.state_subscription_count == 0
    assert len(queueWithItems) == 0
    assert not controller.is_playing
