from upnpavcontrol.web import json_rpc
import asyncio
import pydantic


class JsonRPCTestConnection(object):

    def __init__(self, websocket):
        self._websocket = websocket
        self._nextId = 1
        self.api_version = None
        self.state = 'disconnected'
        self.timeout = 5

    async def __aenter__(self):
        initEvent = await self.wait_for_notification()
        if initEvent.method == 'initialize':
            self.api_version = initEvent.params['version']
            self.state = 'connected'
        return self

    async def __aexit__(self, *args, **kwargs):
        self.state = 'disconnected'

    async def send(self, method, params=None):
        request = json_rpc.JsonRPCRequest(id=self._nextId, method=method, params=params, jsonrpc='2.0')
        self._nextId = +1
        await self._websocket.send_text(request.json())
        while True:
            try:
                raw_reply = await asyncio.wait_for(self._websocket.receive_json(), timeout=self.timeout)
                reply = json_rpc.JsonRPCResponse(**raw_reply)
                if reply.id == request.id:
                    return reply.result
            except pydantic.ValidationError:
                pass

    async def wait_for_notification(self):
        raw_reply = await asyncio.wait_for(self._websocket.receive_json(), timeout=self.timeout)
        reply = json_rpc.JsonRPCNotification(**raw_reply)

        return reply

    async def clear_pending_notifications(self):
        try:
            while True:
                await asyncio.wait_for(self._websocket.receive_json(), 0.5)
        except asyncio.TimeoutError:
            pass
