from upnpavcontrol.core.typing_compat import Protocol
from upnpavcontrol.core.mediarenderer import TransportState, PlaybackInfo
from upnpavcontrol.core.oberserver import Subscription
import typing
from .queue import PlaybackQueue, PlaybackItem


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


class PlaybackController():
    def __init__(self, queue: QueueInterface = PlaybackQueue()):
        self._player = None
        self._current_item = None
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
            return

        self._prepare_current_item()
        if self._current_item is not None:
            if self._player_subscription is None:
                self._player_subscription = await self._player.subscribe(self._on_transport_state_changed)
            if not await self._player.play(self._current_item):
                await self._player_subscription.unsubscribe()

    async def stop(self):
        if not self._is_playing:
            return
        await self._player.stop()
        self._is_playing = False
        if self._player_subscription is not None:
            await self._player_subscription.unsubscribe()

    def _prepare_current_item(self):
        if self._current_item is not None:
            return
        self._current_item = self.queue.next_item()

    async def _on_transport_state_changed(self, info: PlaybackInfo):
        player_is_playing = (info.transport == TransportState.PLAYING)
        if self._is_playing == player_is_playing:
            return
        self._is_playing = player_is_playing

        if not player_is_playing:  # switched from playing to stopped
            self._current_item = None
            await self.play()
