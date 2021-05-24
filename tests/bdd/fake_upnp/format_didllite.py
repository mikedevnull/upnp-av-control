from typing import Iterable
from xml.etree import ElementTree as ET
from upnpavcontrol.core import didllite

ET.register_namespace('upnp', 'urn:schemas-upnp-org:metadata-1-0/upnp/')
ET.register_namespace('dc', 'http://purl.org/dc/elements/1.1/')
ET.register_namespace('avt-event', 'urn:schemas-upnp-org:metadata-1-0/AVT/')
ET.register_namespace('rcs', 'urn:schemas-upnp-org:metadata-1-0/RCS/')
ET.register_namespace('event', 'urn:schemas-upnp-org:event-1-0')
ET.register_namespace('didl', 'urn:schemas-upnp-org:metadata-1-0/DIDL-Lite/')
ET.register_namespace('', 'urn:schemas-upnp-org:metadata-1-0/DIDL-Lite/')

NS = {
    "soap_envelope": "http://schemas.xmlsoap.org/soap/envelope/",
    "device": "urn:schemas-upnp-org:device-1-0",
    "service": "urn:schemas-upnp-org:service-1-0",
    "event": "urn:schemas-upnp-org:event-1-0",
    "control": "urn:schemas-upnp-org:control-1-0",
    'upnp': 'urn:schemas-upnp-org:metadata-1-0/upnp/',
    'dc': 'http://purl.org/dc/elements/1.1/'
}


def add_subelement_if(parent, tag, ns, text):
    if text is None:
        return
    nsuri = NS[ns]
    element = ET.SubElement(parent, f'{{{nsuri}}}{tag}')
    element.text = text
    return element


def format_didllite(elements: Iterable[didllite.MusicTrack]):
    root = ET.Element('{urn:schemas-upnp-org:metadata-1-0/DIDL-Lite/}DIDL-Lite')
    for element in elements:
        item = format_music_item(element)
        root.append(item)
    return ET.tostring(root).decode('utf-8')


def format_music_item(didlelement: didllite.MusicTrack):
    item = ET.Element('{urn:schemas-upnp-org:metadata-1-0/DIDL-Lite/}item')
    item.attrib['id'] = didlelement.id
    item.attrib['parentID'] = didlelement.parentID
    item.attrib['restricted'] = '1'
    add_subelement_if(item, 'class', 'upnp', didlelement.upnpclass)
    add_subelement_if(item, 'title', 'dc', didlelement.title)
    add_subelement_if(item, 'album', 'upnp', didlelement.album)
    add_subelement_if(item, 'artist', 'upnp', didlelement.artist)
    add_subelement_if(item, 'originalTrackNumber', 'upnp', didlelement.originalTrackNumber)

    return item
