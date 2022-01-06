from async_upnp_client import UpnpRequester
import os
import asyncio
import typing

TestResponseHandler = typing.Callable[[], typing.Tuple[int, typing.Mapping[str, str], str]]


def _make_datafile_response_handler(filepath):
    def f():
        with open(filepath, 'r') as handle:
            return 200, {}, handle.read()

    return f


def _make_static_reponse_handler(body: str, headers: dict = None):
    if headers is None:
        headers = {}

    def f():
        return 200, headers, body

    return f


class UpnpTestRequester(UpnpRequester):
    def __init__(self):
        self._response_map = {}

    def register_uri(self, method: str, url: str, body: str = None, headers: dict = None):
        self.register_uri_handler(method, url, _make_static_reponse_handler(body, headers))
        key = (method, url)
        self._response_map[key] = body

    def register_uri_from_datafile(self, method: str, url: str, filename: str, path='tests/data'):
        filepath = os.path.join(path, filename)
        self.register_uri_handler(method, url, _make_datafile_response_handler(filepath))

    def register_uri_handler(self, method: str, url: str, handler: TestResponseHandler):
        assert method in ('GET', 'POST', 'SUBSCRIBE', 'UNSUBSCRIBE')
        key = (method, url)
        self._response_map[key] = handler

    async def async_http_request(self, method, url, headers=None, body=None, body_type='text'):

        key = (method, url)
        if key not in self._response_map:
            raise asyncio.TimeoutError('Unkown resource for request: %s' % str(key))

        return self._response_map[key](headers, body)
