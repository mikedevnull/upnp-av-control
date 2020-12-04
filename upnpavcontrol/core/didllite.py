# -*- coding: utf-8 -*-
import defusedxml.ElementTree as etree
from pydantic import BaseModel
import typing
import html


class DidlObject(BaseModel):
    id: str
    parentID: str
    upnpclass: str
    title: str


class DidlItem(DidlObject):
    pass


class DidlContainer(DidlObject):
    pass


class MusikAlbum(DidlContainer):
    albumArtURI: typing.Optional[str]
    artist: typing.Optional[str]
    genre: typing.Optional[str]
    producer: typing.Optional[str]
    toc: typing.Optional[str]


class MusikArtist(DidlContainer):
    genre: typing.Optional[str]
    artistDiscographyURI: typing.Optional[str]


class MusicTrack(DidlItem):
    artist: typing.Optional[str]
    album: typing.Optional[str]
    originalTrackNumber: typing.Optional[int]
    playlist: typing.Optional[str]
    storageMedium: typing.Optional[str]
    contributor: typing.Optional[str]
    date: typing.Optional[str]
    albumArtURI: typing.Optional[str]


# Not all fields are present in all models, but
# as their mappings don't overlap (for the subset we're currently supporting)
# it's ok to use a single mapping structure.
# Optional and required fields will be enfored by the model itself
_field_to_didl_mapping = {
    'id': '@id',
    'parentID': '@parentID',
    'upnpclass': 'upnp:class',
    'title': 'dc:title',
    'artist': 'upnp:artist',
    'album': 'upnp:album',
    'albumArtURI': 'upnp:albumArtURI',
    'artistDiscographyURI': 'upnp:artistDiscographyURI',
    'originalTrackNumber': 'upnp:originalTrackNumber',
    'playlist': 'upnp:playlist',
    'storageMedium': 'upnp:storageMedium',
    'contributor': 'dc:contributor',
    'date': 'dc:date'
}

_nsmap = {'upnp': 'urn:schemas-upnp-org:metadata-1-0/upnp/', 'dc': 'http://purl.org/dc/elements/1.1/'}


class DictAdapter():
    """
    Given a field mapping, this class provides a map like interface to
    an XML element.

    This provides a uniform an configurable way to transform XML elements
    into python/pydantic dataclasses.

    Adapted from pydantic.utils.GetterDict.
    """
    def __init__(self, obj: typing.Any, key_map: typing.Mapping[str, str], namespaces: typing.Mapping[str, str] = None):
        self._xml = obj
        self._key_map = key_map
        self._nsmap = namespaces

    def _get_from_xml(self, key, default=None):
        mapped_key = self._key_map[key]
        if mapped_key[0] == '@':
            return self._xml.attrib.get(mapped_key[1:], default)
        else:
            value = self._xml.findtext(mapped_key, namespaces=self._nsmap)
            if value is None:
                return default
            return html.unescape(value)

    def __getitem__(self, key: str) -> typing.Any:
        return self._get_from_xml(key)

    def get(self, key: typing.Any, default: typing.Any = None) -> typing.Any:
        return self._get_from_xml(key, default)

    def keys(self) -> typing.AbstractSet[str]:
        """
        Keys of the pseudo dictionary, uses a list not set so order information can be maintained like python
        dictionaries.
        """
        return self._key_map.keys()

    def values(self) -> typing.List[typing.Any]:
        return [self[k] for k in self]

    def items(self) -> typing.Iterator[typing.Tuple[str, typing.Any]]:
        for k in self:
            yield k, self.get(k)

    def __iter__(self) -> typing.Iterator[str]:
        for key in self._key_map:
            yield key

    def __len__(self) -> int:
        return len(self._key_map)

    def __contains__(self, item: typing.Any) -> bool:
        return item in self.keys()


def _create_xml_adapter(xmlElement, field_mapping=_field_to_didl_mapping):
    return DictAdapter(xmlElement, field_mapping, _nsmap)


def from_xml_string(xmldata):
    tree = etree.fromstring(xmldata)
    # TODO: validate root element
    for child in tree:
        yield _to_didl_element(child)


_class_to_element_mapping = {
    'object.item.audioItem.musicTrack': MusicTrack,
    'object.container.album.musicAlbum': MusikAlbum,
    'object.container.person.musicArtist': MusikArtist
}


def _to_didl_element(xmlElement):
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
    adapter = _create_xml_adapter(xmlElement)
    return cls.parse_obj(adapter)
