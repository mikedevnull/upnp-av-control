from upnpavcontrol.core.typing_compat import Protocol
from upnpavcontrol.core.mediarenderer import TransportState, PlaybackInfo
from upnpavcontrol.core.oberserver import Subscription, wait_for_value_if
from .queue import PlaybackQueue, PlaybackItem
import typing
import logging
import asyncio

_logger = logging.getLogger(__name__)


async def wait_for(oberserable, predicate: typing.Callable[[PlaybackInfo], bool], timeout: int = 5):
    future = asyncio.get_running_loop().create_future()

    async def f(v: PlaybackInfo):
        if predicate(v):
            future.set_result(True)

    subscription = await oberserable.subscribe(f)

    def unsub(*args):
        asyncio.create_task(subscription.unsubscribe())

    future.add_done_callback(unsub)
    return future


class PlaybackControllable(Protocol):
    async def play(self, item: PlaybackItem):
        ...

    async def stop(self):
        ...

    async def subscribe(self, callback: typing.Callable[[TransportState], typing.Awaitable[None]]) -> Subscription:
        ...


class QueueInterface(Protocol):
    def next_item(self) -> typing.Optional[PlaybackItem]:
        ...

    def clear(self) -> None:
        ...


class PlaybackController():
    def __init__(self, queue: QueueInterface = PlaybackQueue()):
        self._player = None
        self._queue = queue
        self._is_playing = False
        self._player_subscription: Subscription = None

    @property
    def is_playing(self):
        return self._is_playing

    @property
    def queue(self):
        return self._queue

    async def setup_player(self, player: PlaybackControllable):
        self._player = player

    async def play(self):
        if self._is_playing:
            _logger.debug("Already playing, doing nothing")
            return

        if self.queue.current_item is None:
            self.queue.next_item()
        if self.queue.current_item is None:
            _logger.debug("No item left to play, doing nothing")
            return

        if self._player_subscription is None:
            _logger.debug("Subscribing to transport state changes.")
            self._player_subscription = await self._player.subscribe(self._on_transport_state_changed)
        try:
            async with wait_for_value_if(self._player, lambda x: x.transport == TransportState.PLAYING):
                _logger.debug("Player should play item %s", self.queue.current_item)
                await self._player.play(self.queue.current_item)
                _logger.debug('waiting for playing feedback')
            _logger.debug('got for playing feedback')
        except Exception:
            _logger.exception("Error while trying to play next queue item")
            if self._player_subscription is not None:
                _logger.debug("Unsubscribing from transport state changes due to error.")
                await self._player_subscription.unsubscribe()
                self._player_subscription = None
                self._is_playing = False

    def clear(self):
        self._queue.clear()

    async def stop(self):
        if not self._is_playing:
            _logger.debug("Already stopped, doing nothing")
            return

        async with wait_for_value_if(self._player, lambda x: x.transport == TransportState.STOPPED):
            _logger.debug("Stopping player ...")
            await self._player.stop()
            self._is_playing = False
        _logger.debug('got stopped feedback')
        if self._player_subscription is not None:
            await self._player_subscription.unsubscribe()
            self._player_subscription = None

    async def _on_transport_state_changed(self, info: PlaybackInfo):
        try:
            player_is_playing = (info.transport == TransportState.PLAYING)
            if self._is_playing == player_is_playing:
                return
            _logger.debug("Switched playing state to %s", player_is_playing)
            self._is_playing = player_is_playing

            if not player_is_playing:  # switched from playing to stopped
                if self._queue.next_item() is not None:
                    _logger.debug("Trying to play next item in queue")
                    await self.play()
                elif self._player_subscription is not None:
                    await self._player_subscription.unsubscribe()
                    self._player_subscription = None
        except Exception as e:
            _logger.exception('transport state handler')
            raise e
