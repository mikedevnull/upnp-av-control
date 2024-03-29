import enum
import re
from . import didllite
import logging

_logger = logging.getLogger(__name__)


class BrowseFlags(enum.Enum):
    BrowseDirectChildren = 'BrowseDirectChildren'
    BrowseMetadata = 'BrowseMetadata'


class MediaServer(object):

    def __init__(self, device):
        self._device = device

    @property
    def friendly_name(self):
        return self._device.friendly_name

    @property
    def upnp_device(self):
        return self._device

    @property
    def udn(self):
        return self._device.udn.lstrip('uuid:')

    @property
    def av_transport(self):
        return self._device.service('urn:schemas-upnp-org:service:AVTransport:1')

    @property
    def connection_manager(self):
        return self._device.service('urn:schemas-upnp-org:service:ConnectionManager:1')

    @property
    def content_directory(self):
        return self._device.service('urn:schemas-upnp-org:service:ContentDirectory:1')

    async def browse(self,
                     objectID: str,
                     browse_flag: BrowseFlags = BrowseFlags.BrowseDirectChildren,
                     starting_index=0,
                     requested_count=0):
        payload = await self.content_directory.async_call_action('Browse',
                                                                 ObjectID=objectID,
                                                                 BrowseFlag=browse_flag.value,
                                                                 StartingIndex=starting_index,
                                                                 RequestedCount=requested_count,
                                                                 SortCriteria='',
                                                                 Filter='*')
        regex = re.compile(r"&(?!amp;|lt;|gt;)")
        didl = regex.sub("&amp;", payload['Result'])
        return didllite.DidlLite(didl)

    async def browse_metadata(self, object_id: str):
        didl = await self.browse(object_id, browse_flag=BrowseFlags.BrowseMetadata)
        return didl

    def __repr__(self):
        return '<MediaServer {}>'.format(self._device.friendly_name)
