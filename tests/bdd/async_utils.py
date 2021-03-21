from functools import wraps
import asyncio


def sync(func):
    @wraps(func)
    def synced_func(*args, **kwargs):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(func(*args, **kwargs))

    return synced_func


def run_on_main_loop(f):
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(f)
