from unittest import mock
import inspect


class AsyncMockStub(mock.MagicMock):

    def __init__(self, *args, side_effect=None, **kwargs):
        if side_effect is not None and inspect.iscoroutinefunction(side_effect):
            side_effect = _wrap_side_effect(side_effect)
        super().__init__(*args, side_effect=side_effect, **kwargs)

    async def __call__(self, *args, **kwargs):
        return super().__call__(*args, **kwargs)


try:
    from unittest.mock import AsyncMock
except ImportError:
    import asyncio
    import concurrent.futures

    pool = concurrent.futures.ThreadPoolExecutor()

    def _wrap_side_effect(side_effect):

        def blocking_side_effect(*args, **kwargs):
            return pool.submit(asyncio.run, side_effect(*args, **kwargs)).result()

        return blocking_side_effect

    AsyncMock = AsyncMockStub
