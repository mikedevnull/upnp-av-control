from enum import Enum
from pydantic import Field, BaseModel
import typing
from upnpavcontrol.core import typing_compat
from upnpavcontrol.core.mediarenderer import TransportState


class ApiInfo(BaseModel):
    api_version: typing_compat.Literal[1]
    backend_version: str


class PlayerDevice(BaseModel):
    friendly_name: str = Field(alias="name")
    udn: str = Field(alias="id")

    class Config:
        orm_mode = True
        allow_population_by_field_name = True


class PlaybackState(BaseModel):
    volume_percent: int = 0
    transport: TransportState = TransportState.STOPPED
    title: typing.Optional[str]
    artist: typing.Optional[str]
    album: typing.Optional[str]

    class Config:
        use_enum_values = True


class PlaybackStateIn(BaseModel):
    volume_percent: typing.Optional[int]
    transport: typing.Optional[TransportState]


class PlaybackQueueItem(BaseModel):
    id: str
    title: typing.Optional[str]
    artist: typing.Optional[str]
    album: typing.Optional[str]
    image: typing.Optional[str]


class PlaybackQueue(BaseModel):
    items: typing.List[PlaybackQueueItem]
    current_item_index: typing.Optional[int]


class PlaybackQueueIn(BaseModel):
    items: typing.Optional[typing.List[PlaybackQueueItem]]
    current_item_index: typing.Optional[int]


class LibraryItemType(Enum):
    CONTAINER = 'container'
    ITEM = 'item'


class LibraryListItem(BaseModel):
    id: str
    parentID: typing.Optional[str]
    title: str
    upnpclass: LibraryItemType
    image: typing.Optional[str]

    class Config:
        orm_mode = True


class LibraryItemMetadata(BaseModel):
    id: str
    parentID: typing.Optional[str]
    upnpclass: str
    title: str
    artist: typing.Optional[str]
    genre: typing.Optional[str]
    album: typing.Optional[str]
    originalTrackNumber: typing.Optional[int]
    artistDiscographyURI: typing.Optional[str]
    albumArtURI: typing.Optional[str]

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
