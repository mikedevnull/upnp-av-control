# -*- coding: utf-8 -*-
from attr import attrs, attrib
import lxml.etree

nsmap = {
    'upnp': 'urn:schemas-upnp-org:metadata-1-0/upnp/',
    'dc': 'http://purl.org/dc/elements/1.1/'
}


@attrs(frozen=True)
class BaseObject(object):
    id = attrib()
    parentID = attrib()
    upnpclass = attrib()
    title = attrib()


@attrs(frozen=True)
class MusicTrack(object):
    id = attrib()
    parentID = attrib()
    upnpclass = attrib()
    title = attrib()
    artist = attrib(default=None)
    album = attrib(default=None)
    originalTrackNumber = attrib(default=None)
    playlist = attrib(default=None)
    storageMedium = attrib(default=None)
    contributor = attrib(default=None)
    date = attrib(default=None)


def parse(xmldata):
    tree = lxml.etree.fromstring(xmldata)
    # TODO: validate root element
    for child in tree:
        yield _to_didl_element(child)


def _to_didl_element(xmlElement):
    upnpclass = xmlElement.findtext('upnp:class', namespaces=nsmap)
    if upnpclass.startswith('object.item.audioItem.musicTrack'):
        return _parse_musicitem(xmlElement)
    else:
        return _parse_base_object(xmlElement)


@attrs(frozen=True)
class _DidlEntry(object):
    name = attrib()
    key = attrib()
    required = attrib(type=bool, default=True)


def _parse_didl(xmlElement, attributes, elements):
    data = {}
    for attribute in attributes:
        value = xmlElement.attrib[attribute.name]
        if attribute.required and value is None:
            raise RuntimeError(
                'required attribute %s not present in DIDL-Lite data' %
                attribute.name)
        data[attribute.key] = value

    for element in elements:
        value = xmlElement.findtext(element.name, namespaces=nsmap)
        if element.required and value is None:
            raise RuntimeError(
                'required element %s not present in DIDL-Lite data' %
                element.name)
        data[element.key] = value

    return data


def _parse_musicitem(xmlElement):
    data = _parse_didl(
        xmlElement,
        attributes=(_DidlEntry(name='id', key='id'),
                    _DidlEntry(name='parentID', key='parentID')),
        elements=(_DidlEntry(name='upnp:class', key='upnpclass'),
                  _DidlEntry(name='dc:title', key='title'),
                  _DidlEntry(
                      name='upnp:artist', key='artist', required=False),
                  _DidlEntry(name='upnp:album', key='album', required=False),
                  _DidlEntry(
                      name='upnp:originalTrackNumber',
                      key='originalTrackNumber',
                      required=False),
                  _DidlEntry(
                      name='upnp:playlist', key='playlist', required=False),
                  _DidlEntry(
                      name='upnp:storageMedium',
                      key='storageMedium',
                      required=False),
                  _DidlEntry(
                      name='dc:contributor',
                      key='contributor',
                      required=False),
                  _DidlEntry(name='dc:date', key='date', required=False)))

    return MusicTrack(**data)


def _parse_base_object(xmlElement):
    id = xmlElement.attrib['id']
    parentID = xmlElement.attrib['parentID']
    upnpclass = xmlElement.findtext('upnp:class', namespaces=nsmap)
    title = xmlElement.findtext('dc:title', namespaces=nsmap)
    return BaseObject(
        id=id, parentID=parentID, upnpclass=upnpclass, title=title)
