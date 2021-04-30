# -*- coding: utf-8 -*-
import defusedxml.ElementTree as etree
from pydantic import BaseModel, Field
import typing
from datetime import time
import html

_nsmap = {
    'upnp': 'urn:schemas-upnp-org:metadata-1-0/upnp/',
    'dc': 'http://purl.org/dc/elements/1.1/',
    'dl': 'urn:schemas-upnp-org:metadata-1-0/DIDL-Lite/'
}


class DictAdapter():
    """
    Given a field mapping, this class provides a map like interface to
    an XML element.

    This provides a uniform an configurable way to transform XML elements
    into python/pydantic dataclasses.

    Adapted from pydantic.utils.GetterDict.
    """
    def __init__(self, obj: typing.Any, namespaces: typing.Mapping[str, str] = _nsmap):
        self._xml = obj
        self._nsmap = namespaces

    def _get_from_xml(self, key, default=None):
        if key[0] == '@':
            return self._xml.attrib.get(key[1:], default)
        elif key == '__raw_xml':
            return etree.tostring(self._xml).decode()
        elif key == '#text':
            return self._xml.text
        elif key[0] == '#':
            value = self._xml.findtext(key[1:], namespaces=self._nsmap)
            if value is None:
                return default
            return html.unescape(value)
        elif key[0] == '*':
            return self._xml.findall(key[1:], namespaces=self._nsmap)
        else:
            element = self._xml.find(key, namespaces=self._nsmap)
            return element

    def get(self, key: typing.Any, default: typing.Any = None) -> typing.Any:
        return self._get_from_xml(key, default)


class Resource(BaseModel):
    protocolInfo: str = Field(alias='@protocolInfo')
    uri: str = Field(alias='#text')
    size: typing.Optional[int] = Field(alias='@size')
    duration: typing.Optional[time] = Field(alias='@duration')
    bitrate: typing.Optional[int] = Field(alias='@bitrate')
    sampleFrequency: typing.Optional[int] = Field(alias='@sampleFrequency')

    class Config:
        getter_dict = DictAdapter
        orm_mode = True


class AlbumArtURI(BaseModel):
    uri: str = Field(alias='#text')
    dlnaProfile: typing.Optional[str] = Field(alias='@dlna:profileID')

    class Config:
        getter_dict = DictAdapter
        orm_mode = True


class DidlObject(BaseModel):
    id: str = Field(alias='@id')
    parentID: str = Field(alias='@parentID')
    upnpclass: str = Field(alias='#upnp:class')
    title: str = Field(alias='#dc:title')

    res: typing.List[Resource] = Field(alias='*dl:res', default_factory=list)

    class Config:
        getter_dict = DictAdapter
        orm_mode = True


class DidlItem(DidlObject):
    pass


class DidlContainer(DidlObject):
    pass


class MusikAlbum(DidlContainer):
    albumArtURI: typing.Optional[AlbumArtURI] = Field(alias='upnp:albumArtURI')
    artist: typing.Optional[str] = Field(alias='#upnp:artist')
    genre: typing.Optional[str] = Field(alias='#upnp:genre')
    producer: typing.Optional[str]
    toc: typing.Optional[str]


class MusikArtist(DidlContainer):
    genre: typing.Optional[str] = Field(alias='#upnp:genre')
    artistDiscographyURI: typing.Optional[str] = Field(alias='#upnp:artistDiscographyURI')


class MusicTrack(DidlItem):
    artist: typing.Optional[str] = Field(alias='#upnp:artist')
    album: typing.Optional[str] = Field(alias='#upnp:album')
    artistDiscographyURI: typing.Optional[str] = Field(alias='#upnp:artistDiscographyURI')
    originalTrackNumber: typing.Optional[int] = Field(alias='#upnp:originalTrackNumber')
    playlist: typing.Optional[str] = Field(alias='#upnp:playlist')
    storageMedium: typing.Optional[str] = Field(alias='#upnp:storageMedium')
    contributor: typing.Optional[str] = Field(alias='#dc:contributor')
    date: typing.Optional[str] = Field(alias='#dc:date')
    albumArtURI: typing.Optional[AlbumArtURI] = Field(alias='upnp:albumArtURI')


def from_xml_string(xmldata):
    root = etree.fromstring(xmldata)
    return [_to_didl_element(child) for child in root]


class DidlLite(object):
    def __init__(self, xml: str):
        self._raw = xml
        self._objects: typing.Optional[typing.List[DidlObject]] = None

    @property
    def objects(self):
        if self._objects is None:
            self._objects = from_xml_string(self._raw)
        return self._objects

    @property
    def xml(self):
        return self._raw


_class_to_element_mapping = {
    'object.item.audioItem.musicTrack': MusicTrack,
    'object.container.album.musicAlbum': MusikAlbum,
    'object.container.person.musicArtist': MusikArtist
}


def _to_didl_element(xmlElement: any):
    upnpclass = xmlElement.findtext('upnp:class', namespaces=_nsmap)
    # mapping logic should be improved/refactored when more types are supported
    if upnpclass in _class_to_element_mapping:
        cls = _class_to_element_mapping[upnpclass]
    elif upnpclass.startswith('object.item'):
        cls = DidlItem
    elif upnpclass.startswith('object.container'):
        cls = DidlContainer
    else:
        cls = DidlObject
    return cls.from_orm(xmlElement)
