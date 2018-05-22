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


def parse(xmldata):
    tree = lxml.etree.fromstring(xmldata)
    # TODO: validate root element
    for child in tree:
        yield _to_didl_element(child)


def _to_didl_element(xmlElement):
    id = xmlElement.attrib['id']
    parentID = xmlElement.attrib['parentID']
    upnpclass = xmlElement.findtext('upnp:class', namespaces=nsmap)
    title = xmlElement.findtext('dc:title', namespaces=nsmap)
    return BaseObject(id=id,
                      parentID=parentID,
                      upnpclass=upnpclass,
                      title=title)
