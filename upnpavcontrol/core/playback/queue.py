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

    @property
    def items(self):
        return self._items

    def insert(self, dms, object_id, title):
        self._items.append(PlaybackItem(dms=dms, object_id=object_id, title=title))

    def clear(self):
        self._items.clear()

    def next_item(self):
        if len(self._items) > 0:
            return self._items.pop(0)
        return None
