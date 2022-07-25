from dataclasses import dataclass, field
import typing
from .. import typing_compat
from .. import didllite


@dataclass
class ContentFormat(object):
    mimetype: str
    meta: typing.Mapping[str, str] = field(default_factory=dict)

    @classmethod
    def fromstring(cls, data: str):
        parts = data.split(';')
        mimetype = parts[0]
        meta = {k: v for k, v in (part.split('=', 2) for part in parts[1:])}
        return cls(mimetype=mimetype, meta=meta)


@dataclass
class ProtocolInfoEntry(object):
    protocol: typing_compat.Literal['http-get', 'rtsp-rtp-udp']
    network: typing_compat.Literal['*']
    content_format: ContentFormat
    additional_info: str

    @classmethod
    def fromstring(cls, data: str):
        parts = data.split(':', 4)
        if parts[0] not in ('http-get', 'rtsp-rtp-udp'):
            return None
        if parts[1] != '*':
            return None
        content_format = ContentFormat.fromstring(parts[2])
        return cls(protocol=parts[0], network=parts[1], content_format=content_format, additional_info=parts[3])


def protocol_info_matches(lhs: ProtocolInfoEntry, rhs: ProtocolInfoEntry):
    return lhs is not None and rhs is not None and \
        lhs.protocol == rhs.protocol and lhs.content_format.mimetype == rhs.content_format.mimetype


def match_resources(object_resources: typing.Sequence[didllite.Resource],
                    renderer_protocols: typing.Sequence[ProtocolInfoEntry]) -> typing.Sequence[didllite.Resource]:
    matched_resources = []
    for object_resource in object_resources:
        for renderer_protocol in renderer_protocols:
            object_protoinfo = ProtocolInfoEntry.fromstring(object_resource.protocolInfo)
            if object_protoinfo is None:
                continue
            if protocol_info_matches(object_protoinfo, renderer_protocol):
                matched_resources.append(object_resource)
                break
    return matched_resources


def parse_protocol_infos(data):
    parser = (ProtocolInfoEntry.fromstring(entry) for entry in data.split(','))
    return [x for x in parser if x is not None]
