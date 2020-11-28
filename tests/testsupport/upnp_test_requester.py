from async_upnp_client import UpnpRequester
import os
import asyncio


def _read_data_file(filename):
    filepath = os.path.join('tests', 'data', filename)
    with open(filepath, 'r') as handle:
        return handle.read()


class UpnpTestRequester(UpnpRequester):
    def __init__(self):
        self._response_map = {}

    def register_uri(self, method: str, url: str, body: str = None):
        assert method in ('GET', 'POST')
        key = (method, url)
        self._response_map[key] = body

    def register_uri_from_datafile(self, method: str, url: str, filename: str, path='tests/data'):
        filepath = os.path.join(path, filename)
        with open(filepath, 'r') as handle:
            self.register_uri(method, url, body=handle.read())

    async def async_do_http_request(self, method, url, headers=None, body=None, body_type='text'):

        key = (method, url)
        if key not in self._response_map:
            raise asyncio.TimeoutError('Unkown resource for request: %s' % str(key))

        return self._response_map[key]
