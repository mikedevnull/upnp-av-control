import pytest
from upnpavcontrol.core.playback.controller import PlaybackController, PlaybackItem, TransportState
from upnpavcontrol.core.oberserver import Observable
import unittest.mock as mock
import typing


class FakePlayerInterface():
    def __init__(self):
        self.play = mock.AsyncMock()
        self.stop = mock.AsyncMock()
        self._state_observable = Observable[TransportState]()

    async def subscribe(self, callback: typing.Callable[[TransportState], typing.Awaitable[None]]):
        return await self._state_observable.subscribe(callback)

    async def fake_stopped_event(self):
        await self._state_observable.notify(TransportState.STOPPED)


class FakePlaybackQueue(list):
    def nextItem(self) -> typing.Optional[PlaybackItem]:
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
    assert controller.playback_state == TransportState.STOPPED
    assert len(controller.queue) == 0

    await controller.play()

    player.play.assert_not_called()
    player.stop.assert_not_called()
    assert controller.playback_state == TransportState.STOPPED


@pytest.mark.asyncio
async def test_stopped_device_play_device_starts_playing(queueWithItems):
    player = FakePlayerInterface()
    item1 = queueWithItems[0]
    controller = PlaybackController(queueWithItems)
    await controller.setup_player(player)

    await controller.play()

    player.play.assert_called_with(item1)
    assert controller.playback_state == TransportState.PLAYING


@pytest.mark.asyncio
async def test_playing_device_play_nothing_happens(queueWithItems):
    player = FakePlayerInterface()
    controller = PlaybackController(queueWithItems)
    await controller.setup_player(player)

    await controller.play()
    assert controller.playback_state == TransportState.PLAYING

    await controller.play()
    player.play.assert_called_once()  # only call on first play()
    player.stop.assert_not_called()
    assert controller.playback_state == TransportState.PLAYING


@pytest.mark.asyncio
async def test_playing_song_finishes_next_item_is_player(queueWithItems):
    player = FakePlayerInterface()

    controller = PlaybackController(queueWithItems)
    await controller.setup_player(player)
    item1 = queueWithItems[0]
    item2 = queueWithItems[1]
    await controller.play()
    player.play.assert_called_with(item1)
    assert len(queueWithItems) == 1
    assert controller.playback_state == TransportState.PLAYING
    player.play.reset_mock()

    await player.fake_stopped_event()
    player.play.assert_called_with(item2)
    assert len(queueWithItems) == 0
    assert controller.playback_state == TransportState.PLAYING


@pytest.mark.asyncio
async def test_starting_first_playback_fails_player_never_starts(queueWithItems):
    player = FakePlayerInterface()

    controller = PlaybackController(queueWithItems)
    await controller.setup_player(player)
    item1 = queueWithItems[0]

    player.play.return_value = False
    await controller.play()
    player.play.assert_called_with(item1)
    assert len(queueWithItems) == 1
    assert controller.playback_state == TransportState.STOPPED
    player.play.assert_called_once()


@pytest.mark.asyncio
async def test_starting_playback_fails_playback_stops(queueWithItems):
    player = FakePlayerInterface()

    controller = PlaybackController(queueWithItems)
    await controller.setup_player(player)
    item1 = queueWithItems[0]
    item2 = queueWithItems[1]

    await controller.play()
    player.play.assert_called_with(item1)
    assert controller.playback_state == TransportState.PLAYING
    player.play.reset_mock()

    player.play.return_value = False

    await player.fake_stopped_event()
    player.play.assert_called_with(item2)
    assert len(queueWithItems) == 0
    assert controller.playback_state == TransportState.STOPPED
