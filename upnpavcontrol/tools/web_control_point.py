import asyncio
import logging
import argparse
from upnpavcontrol.core import AVControlPoint
from upnpavcontrol.web import run_web_api
_logger = logging.getLogger(__name__)


async def run_web_control_point(loop):
    cp = AVControlPoint()
    upnp_task = loop.create_task(cp.run())
    web_task = loop.create_task(run_web_api(cp))
    await asyncio.wait([upnp_task, web_task])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-d',
        '--debug',
        help="Shot lots of debugging information",
        action="store_const",
        dest="loglevel",
        const=logging.DEBUG,
        default=logging.WARNING,
    )
    parser.add_argument(
        '-v',
        '--verbose',
        help="Verbose logging",
        action="store_const",
        dest="loglevel",
        const=logging.INFO,
    )
    args = parser.parse_args()
    logging.basicConfig(level=args.loglevel)
    logging.getLogger('async_upnp_client').setLevel(logging.INFO)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_web_control_point(loop))
    loop.close()


if __name__ == '__main__':
    main()
