from pydantic import BaseModel, Field
import typing
from . import json_api


class DeviceModel(BaseModel):
    friendly_name: str = Field(alias="name")

    class Config:
        orm_mode = True
        allow_population_by_field_name = True


DevicesResponse = json_api.create_list_response_model('mediadevice', id_field='udn', PayloadModel=DeviceModel)
DeviceResponse = json_api.create_response_model('mediadevice', DeviceModel)


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
