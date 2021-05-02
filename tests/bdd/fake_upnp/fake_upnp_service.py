from unittest import mock
from ...testsupport import UpnpTestRequester, NotificationTestEndpoint
from email.utils import formatdate
import uuid
from xml.etree import ElementTree as ET
import defusedxml.ElementTree as DET
from urllib.parse import urlparse
import typing

ET.register_namespace('upnp', 'urn:schemas-upnp-org:metadata-1-0/upnp/')
ET.register_namespace('dc', 'http://purl.org/dc/elements/1.1/')
ET.register_namespace('avt-event', 'urn:schemas-upnp-org:metadata-1-0/AVT/')
ET.register_namespace('rcs', 'urn:schemas-upnp-org:metadata-1-0/RCS/')
ET.register_namespace('event', 'urn:schemas-upnp-org:event-1-0')

NS = {
    "soap_envelope": "http://schemas.xmlsoap.org/soap/envelope/",
    "device": "urn:schemas-upnp-org:device-1-0",
    "service": "urn:schemas-upnp-org:service-1-0",
    "event": "urn:schemas-upnp-org:event-1-0",
    "control": "urn:schemas-upnp-org:control-1-0",
}


def _format_last_change_notification(value: str):
    root = ET.Element('{urn:schemas-upnp-org:event-1-0}propertyset')
    prop = ET.SubElement(root, '{urn:schemas-upnp-org:event-1-0}property')
    lc = ET.SubElement(prop, 'LastChange')
    lc.text = value

    return ET.tostring(root).decode('utf-8')


def _format_last_change_payload(instance_xml_namespace: str, variables: typing.Mapping[str, typing.Any]):
    lcroot = ET.Element('{urn:schemas-upnp-org:metadata-1-0/upnp/}Event')
    instance = ET.SubElement(lcroot, instance_xml_namespace + 'InstanceID')
    instance.attrib['val'] = '0'
    for key, value in variables.items():
        var = ET.SubElement(instance, instance_xml_namespace + key)
        if key == 'Volume':
            var.attrib['channel'] = 'Master'
            var.attrib['val'] = str(value)
        else:
            var.attrib['val'] = value.value
    return ET.tostring(lcroot).decode('utf-8')


class FakeAsyncAction(object):
    def __init__(self, wrapped):
        self._wrapped = wrapped

    async def async_call(self, *args, **kwargs):
        return await self._wrapped(*args, **kwargs)


class FakeUpnpVariable(object):
    def __init__(self, name: str, value=None):
        self.value = value
        self.name = name


class UpnpServiceMock(object):
    def __init__(self, service_type: str, event_sub_url: str = None, device=None):
        self.device = device
        self.event_sub_url = event_sub_url
        self.service_type = service_type
        self._actions = {}
        self._event_endpoint = None
        self._event_subscritions = []
        self._variables = {}
        self._last_change = FakeUpnpVariable('LastChange', value='')
        self._seq = 0
        self.on_event = None

    def action(self, name: str):
        return self._actions[name]

    def has_action(self, name: str):
        return name in self._actions

    async def async_call_action(self, action: str, **kwargs):
        return await self._actions[action].async_call(**kwargs)

    def add_async_action(self, name: str, func, *args, **kwargs):
        self._actions[name] = FakeAsyncAction(func)

    def add_variable(self, variable: FakeUpnpVariable):
        self._variables[variable.name] = variable

    def configure_event_handling(self, requester: UpnpTestRequester, test_endpoint: NotificationTestEndpoint):
        self._event_endpoint = test_endpoint
        requester.register_uri_handler('SUBSCRIBE', self.event_sub_url, self.handle_event_subscription_request)
        requester.register_uri_handler('UNSUBSCRIBE', self.event_sub_url, self.handle_event_unsubscription_request)

    def handle_event_subscription_request(self, headers=None, body=None):
        sid = f'uuid:{uuid.uuid1()}'
        self._event_subscritions.append(sid)
        headers = {
            'DATE': formatdate(timeval=None, localtime=False, usegmt=True),
            'SERVER': 'foonix/1.2 UPnP/1.0 FooServer/1.50',
            'TIMEOUT': 'Second-1800',
            'sid': sid
        }
        return 200, headers, ''

    async def trigger_notification(self, instance_xml_namespace, variables):
        path = self._event_endpoint.callback_url
        host = urlparse(path).netloc
        last_change_value = _format_last_change_payload(instance_xml_namespace, variables)
        body = _format_last_change_notification(last_change_value)
        for sid in self._event_subscritions:
            headers = {
                'host': host,
                'content-type': 'text/xml',
                'content-length': str(len(body)),
                'NT': 'upnp:event',
                'NTS': 'upnp:propchange',
                'SID': sid,
                'seq': str(self._seq)
            }
            await self._event_endpoint.trigger_notification(headers, body)
        self._seq = self._seq + 1

    def notify_changed_state_variables(self, changed):
        if 'LastChange' in changed and self.on_event:
            var = FakeUpnpVariable('LastChange', value=changed['LastChange'])
            # pylint: disable=not-callable
            self.on_event(self, [var])

    def handle_event_unsubscription_request(self, headers, body=None):
        sid = headers['SID']
        self._event_subscritions.remove(sid)
        return 200, {}, ''
