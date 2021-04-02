from dataclasses import dataclass, field
import csv
import io
import typing


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
    protocol: typing.Literal['http-get', 'rtsp-rtp-udp']
    network: typing.Literal['*']
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


def parse_protocol_infos(data):
    parser = (ProtocolInfoEntry.fromstring(entry) for entry in data.split(','))
    return [x for x in parser if x is not None]


def protocol_info_matches(lhs: ProtocolInfoEntry, rhs: ProtocolInfoEntry):
    return lhs is not None and rhs is not None and lhs.protocol == rhs.protocol and lhs.content_format.mimetype == rhs.content_format.mimetype
