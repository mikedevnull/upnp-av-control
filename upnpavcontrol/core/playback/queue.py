from dataclasses import dataclass
import typing


@dataclass
class PlaybackItem():
    dms: str
    object_id: str
    title: str
    image: typing.Optional[str] = None


class PlaybackQueue():
    def __init__(self):
        self._items = []
        self._current_item_index: typing.Optional[PlaybackItem] = None

    @property
    def items(self):
        return self._items

    @property
    def current_item(self):
        if self._current_item_index is None:
            return None
        return self._items[self._current_item_index]

    @property
    def current_item_index(self):
        return self._current_item_index

    def append(self, dms, object_id, title):
        self._items.append(PlaybackItem(dms=dms, object_id=object_id, title=title))

    def clear(self):
        self._items.clear()
        self._current_item_index = None

    def next_item(self):
        if len(self._items) == 0:
            return None
        if self._current_item_index is None:
            self._current_item_index = 0
        else:
            self._current_item_index += 1

        if self._current_item_index >= len(self._items):
            self._current_item_index = None
            return None

        return self._items[self._current_item_index]
