# -*- coding: utf-8 -*-
from attr import attrs, attrib
import lxml.etree

nsmap = {'upnp': 'urn:schemas-upnp-org:metadata-1-0/upnp/',
         'dc': 'http://purl.org/dc/elements/1.1/'}


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


def _parse_musicitem(xmlElement):
    id = xmlElement.attrib['id']
    parentID = xmlElement.attrib['parentID']
    upnpclass = xmlElement.findtext('upnp:class', namespaces=nsmap)
    title = xmlElement.findtext('dc:title', namespaces=nsmap)
    artist = xmlElement.findtext('upnp:artist', namespaces=nsmap)
    album = xmlElement.findtext('upnp:album', namespaces=nsmap)
    originalTrackNumber = xmlElement.findtext(
        'upnp:originalTrackNumber', namespaces=nsmap)
    playlist = xmlElement.findtext('upnp:playlist', namespaces=nsmap)
    storageMedium = xmlElement.findtext('upnp:storageMedium', namespaces=nsmap)
    contributor = xmlElement.findtext('dc:contributor', namespaces=nsmap)
    date = xmlElement.findtext('dc:date', namespaces=nsmap)

    return MusicTrack(id=id,
                      parentID=parentID,
                      upnpclass=upnpclass,
                      title=title,
                      artist=artist,
                      album=album,
                      originalTrackNumber=originalTrackNumber,
                      playlist=playlist,
                      storageMedium=storageMedium,
                      contributor=contributor,
                      date=date)


def _parse_base_object(xmlElement):
    id = xmlElement.attrib['id']
    parentID = xmlElement.attrib['parentID']
    upnpclass = xmlElement.findtext('upnp:class', namespaces=nsmap)
    title = xmlElement.findtext('dc:title', namespaces=nsmap)
    return BaseObject(id=id,
                      parentID=parentID,
                      upnpclass=upnpclass,
                      title=title)
