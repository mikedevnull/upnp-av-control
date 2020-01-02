import logging
import colorlog
import argparse
from upnpavcontrol.core import AVControlPoint
from upnpavcontrol.web import app as web_app
import uvicorn

_logger = logging.getLogger(__name__)


def run_web_control_point():
    av_control_point = AVControlPoint()
    web_app.av_control_point = av_control_point
    config = uvicorn.Config(web_app, log_config=None, debug=True, reload=True, host='127.0.0.1', port=8000)
    server = uvicorn.Server(config)
    server.run()


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
    colorlog.basicConfig(level=args.loglevel, format='%(log_color)s%(levelname)s:%(name)s:%(message)s')
    logging.getLogger('async_upnp_client').setLevel(logging.INFO)
    run_web_control_point()
    logging.info('Successfully shutdown UPnP-AV WebControlPoint')


if __name__ == '__main__':
    main()
