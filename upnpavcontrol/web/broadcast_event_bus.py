import asyncio


async def _create_async_notifier(callback):
    while True:
        message = yield
        await callback(message)


class BroadcastEventBus(object):
    def __init__(self):
        self._connections = []
        self.queue = _create_async_notifier(self._notify)

    async def accept(self, websocket):
        await websocket.accept()
        await websocket.send_json({'version': '0.0.1'})
        self._connections.append(websocket)

    def remove_connection(self, websocket):
        if websocket in self._connections:
            self._connections.remove(websocket)

    async def _notify(self, payload: str):
        tasks = []
        for websocket in self._connections:
            task = websocket.send_text(payload)
            tasks.append(task)
        return asyncio.gather(*tasks)

    async def broadcast_event(self, payload: str):
        await self.queue.asend(payload)
