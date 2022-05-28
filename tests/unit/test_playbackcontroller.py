import pytest
from upnpavcontrol.core.playback.controller import PlaybackController, TransportState
from upnpavcontrol.core.playback.queue import PlaybackQueue
from upnpavcontrol.core.oberserver import Observable
from upnpavcontrol.core.mediarenderer import PlaybackInfo
from ..testsupport import AsyncMock
import typing


class FakePlayerInterface():

    def __init__(self):
        self.play = AsyncMock(side_effect=self._do_play)
        self.stop = AsyncMock(side_effect=self._do_stop)
        self.subscribe = AsyncMock(side_effect=self._do_subscribe)
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

    async def _do_stop(self):
        await self._change_transport_state(TransportState.STOPPED)

    async def _do_set_subscription_count(self, x):
        self._state_subscription_count = x

    async def _change_transport_state(self, state):
        if self._state.transport != state:
            self._state.transport = state
            await self._state_observable.notify(self._state)


@pytest.fixture
def queue_with_items():
    queue = PlaybackQueue()
    queue.append(dms='1234', object_id='9876', title='First song')
    queue.append(dms='1234', object_id='9876', title='First song')
    return queue


@pytest.mark.asyncio
async def test_empty_queue_play_nothing_happens():
    player = FakePlayerInterface()
    queue = PlaybackQueue()
    controller = PlaybackController(queue)
    await controller.setup_player(player)
    assert not controller.is_playing
    assert len(controller.queue.items) == 0

    await controller.play()

    player.play.assert_not_called()
    player.stop.assert_not_called()
    player.subscribe.assert_not_called()
    assert not controller.is_playing
    assert player.state_subscription_count == 0


@pytest.mark.asyncio
async def test_stopped_device_play_device_starts_playing(queue_with_items):
    player = FakePlayerInterface()
    item1 = queue_with_items.items[0]
    controller = PlaybackController(queue_with_items)
    await controller.setup_player(player)

    await controller.play()

    player.subscribe.assert_called()
    player.play.assert_called_with(item1)
    assert controller.is_playing
    assert player.state_subscription_count == 1


@pytest.mark.asyncio
async def test_playing_device_play_nothing_happens(queue_with_items):
    player = FakePlayerInterface()
    controller = PlaybackController(queue_with_items)
    await controller.setup_player(player)

    await controller.play()
    assert controller.is_playing

    await controller.play()
    player.play.assert_called_once()  # only call on first play()
    player.subscribe.assert_called()
    player.stop.assert_not_called()
    assert controller.is_playing
    assert player.state_subscription_count == 1


@pytest.mark.asyncio
async def test_playing_device_stop_playback_stops(queue_with_items):
    player = FakePlayerInterface()
    controller = PlaybackController(queue_with_items)
    await controller.setup_player(player)

    await controller.play()
    assert controller.is_playing

    await controller.stop()
    player.stop.assert_called_once()
    assert not controller.is_playing
    assert player.state_subscription_count == 0


@pytest.mark.asyncio
async def test_stopped_device_stop_nothing_happens(queue_with_items):
    player = FakePlayerInterface()
    controller = PlaybackController(queue_with_items)
    await controller.setup_player(player)

    await controller.stop()

    player.stop.assert_not_called()
    player.play.assert_not_called()
    assert not controller.is_playing
    assert player.state_subscription_count == 0


@pytest.mark.asyncio
async def test_playing_song_finishes_next_item_is_player(queue_with_items):
    player = FakePlayerInterface()

    controller = PlaybackController(queue_with_items)
    await controller.setup_player(player)
    item1 = queue_with_items.items[0]
    item2 = queue_with_items.items[1]
    await controller.play()
    player.play.assert_called_with(item1)
    player.subscribe.assert_called()
    assert player.state_subscription_count == 1

    assert controller.is_playing
    player.play.reset_mock()

    await player.fake_stopped_event()
    player.play.assert_called_with(item2)
    assert controller.is_playing
    assert player.state_subscription_count == 1


@pytest.mark.asyncio
async def test_starting_first_playback_fails_player_never_starts(queue_with_items):
    player = FakePlayerInterface()

    controller = PlaybackController(queue_with_items)
    await controller.setup_player(player)
    item1 = queue_with_items.items[0]

    player.play.side_effect = RuntimeError('Playback failed for some reason')
    await controller.play()
    player.play.assert_called_with(item1)
    player.subscribe.assert_called()
    assert queue_with_items.current_item_index == 0
    assert not controller.is_playing
    player.play.assert_called_once()
    assert player.state_subscription_count == 0


@pytest.mark.asyncio
async def test_starting_playback_fails_playback_stops(queue_with_items):
    player = FakePlayerInterface()

    controller = PlaybackController(queue_with_items)
    await controller.setup_player(player)
    item1 = queue_with_items.items[0]
    item2 = queue_with_items.items[1]

    await controller.play()
    player.play.assert_called_with(item1)
    player.subscribe.assert_called()
    assert controller.is_playing
    player.play.reset_mock()

    player.play.side_effect = RuntimeError('Playback failed for some reason')

    await player.fake_stopped_event()
    player.play.assert_called_with(item2)
    assert player.state_subscription_count == 0
    assert not controller.is_playing


@pytest.mark.asyncio
async def test_playing_device_stops_after_last_item(queue_with_items):
    queue_with_items._current_item_index = 1
    player = FakePlayerInterface()
    controller = PlaybackController(queue_with_items)
    await controller.setup_player(player)

    await controller.play()
    assert controller.is_playing
    player.play.assert_called_once()  # only call on first play()

    await player.fake_stopped_event()

    assert not controller.is_playing
    assert player.state_subscription_count == 0


@pytest.mark.asyncio
async def test_playing_device_set_item_index_plays_new_item(queue_with_items):
    queue_with_items._current_item_index = 0
    player = FakePlayerInterface()
    controller = PlaybackController(queue_with_items)
    await controller.setup_player(player)

    await controller.play()
    assert controller.is_playing

    await controller.set_current_item(1)

    player.stop.assert_called_once()
    player.play.assert_called_with(queue_with_items.items[1])

    assert controller.is_playing
    assert player.state_subscription_count == 1


@pytest.mark.asyncio
async def test_playing_device_set_already_selected_itemindex_does_nothing(queue_with_items):
    queue_with_items._current_item_index = 0
    player = FakePlayerInterface()
    controller = PlaybackController(queue_with_items)
    await controller.setup_player(player)

    await controller.play()
    assert controller.is_playing
    player.play.reset_mock()

    await controller.set_current_item(0)

    player.stop.assert_not_called()
    player.play.assert_not_called()

    assert controller.is_playing
    assert player.state_subscription_count == 1


@pytest.mark.asyncio
async def test_playing_device_set_out_of_bound_itemindex_raises_exception(queue_with_items):
    queue_with_items._current_item_index = 0
    player = FakePlayerInterface()
    controller = PlaybackController(queue_with_items)
    await controller.setup_player(player)

    await controller.play()
    assert controller.is_playing

    with pytest.raises(ValueError):
        await controller.set_current_item(2)


@pytest.mark.asyncio
async def test_stopped_device_set_item_index_new_item_selected_without_playing(queue_with_items):
    queue_with_items._current_item_index = 0
    player = FakePlayerInterface()
    controller = PlaybackController(queue_with_items)
    await controller.setup_player(player)
    await controller.set_current_item(1)

    player.stop.assert_not_called()
    player.play.assert_not_called()

    assert not controller.is_playing
    assert player.state_subscription_count == 0
