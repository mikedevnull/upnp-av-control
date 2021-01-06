from unittest import mock


class AsyncMockStub(mock.MagicMock):
    async def __call__(self, *args, **kwargs):
        return super().__call__(*args, **kwargs)


try:
    from unittest.mock import AsyncMock
except ImportError:
    # Running on pre-3.8 Python; use local asyncmock wrapper
    AsyncMock = AsyncMockStub
