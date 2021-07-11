from pydantic import Field, BaseModel
import typing
from upnpavcontrol.core import typing_compat
from upnpavcontrol.core.mediarenderer import PlaybackInfo


class ApiInfo(BaseModel):
    version: typing_compat.Literal[1]


class PlayerDevice(BaseModel):
    friendly_name: str = Field(alias="name")
    udn: str = Field(alias="id")

    class Config:
        orm_mode = True
        allow_population_by_field_name = True


PlaybackState = PlaybackInfo


class PlaybackQueueItem(BaseModel):
    library_item_id: str


class LibraryCollection(BaseModel):
    id: str
    title: str

    class Config:
        orm_mode = True


class LibraryListItem(BaseModel):
    id: str
    title: str

    class Config:
        orm_mode = True


class LibraryItemMetadata(BaseModel):
    id: str
    parentID: str
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
