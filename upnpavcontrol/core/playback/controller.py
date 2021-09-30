from dataclasses import dataclass
from upnpavcontrol.core.typing_compat import Protocol
from upnpavcontrol.core.mediarenderer import TransportState
from upnpavcontrol.core.oberserver import Subscription
import typing


@dataclass
class PlaybackItem():
    dms: str
    object_id: str
    title: str
    image: typing.Optional[str] = None


class PlayInterface(Protocol):
    async def play(self, item: PlaybackItem):
        ...

    async def stop(self):
        ...

    async def subscribe(self, callback: typing.Callable[[TransportState], typing.Awaitable[None]]) -> Subscription:
        ...


class QueueInterface(Protocol):
    def nextItem(self) -> typing.Optional[PlaybackItem]:
        ...


class PlaybackController():
    def __init__(self, queue: QueueInterface):
        self._player = None
        self._current_item = None
        self._queue = queue
        self._state: TransportState = TransportState.STOPPED

    @property
    def queue(self):
        return self._queue

    async def setup_player(self, player: PlayInterface):
        self._player = player
        await self._player.subscribe(self._on_transport_state_changed)

    async def play(self):
        if self._state == TransportState.PLAYING:
            return
        self._prepare_current_item()
        if self._current_item is not None:
            if await self._player.play(self._current_item):
                self._state = TransportState.PLAYING
            else:
                self._state = TransportState.STOPPED

    async def stop(self):
        await self._player.stop()
        self._state = TransportState.PLAYING

    @property
    def playback_state(self):
        return self._state

    def _prepare_current_item(self):
        if self._current_item is not None:
            return
        self._current_item = self.queue.nextItem()

    async def _on_transport_state_changed(self, state: TransportState):
        if self._state == state:
            return
        self._state = state

        if self._state == TransportState.STOPPED:
            self._current_item = None
            await self.play()
