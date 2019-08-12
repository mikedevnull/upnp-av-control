import asyncio
import logging
from upnpavcontrol.core import AVControlPoint
from upnpavcontrol.web import run_web_api
_logger = logging.getLogger(__name__)


async def main(loop):
    cp = AVControlPoint()
    upnp_task = loop.create_task(cp.run())
    web_task = loop.create_task(run_web_api(cp))
    await asyncio.wait([upnp_task, web_task])


if __name__ == '__main__':

    logging.basicConfig(level=logging.INFO)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
    loop.close()
