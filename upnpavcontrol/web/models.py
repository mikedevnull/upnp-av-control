from pydantic import BaseModel, Field
import typing


class DeviceModel(BaseModel):
    friendly_name: str = Field(alias="name")

    class Config:
        orm_mode = True
        allow_population_by_field_name = True


class LibraryListItem(BaseModel):
    title: str
    artist: typing.Optional[str]
    album: typing.Optional[str]

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
