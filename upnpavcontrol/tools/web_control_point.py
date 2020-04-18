import logging
import colorlog
import argparse
from upnpavcontrol.web import app as web_app
import uvicorn

_logger = logging.getLogger(__name__)


def run_web_control_point(host, port):
    config = uvicorn.Config(web_app, log_config=None, debug=True, reload=True, host=host, port=port)
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
    parser.add_argument('--host', help="Host to bind", type=str, default="127.0.0.1")
    parser.add_argument('--port', help="Port to listen", type=int, default=8000)
    args = parser.parse_args()
    colorlog.basicConfig(level=args.loglevel, format='%(log_color)s%(levelname)s:%(name)s:%(message)s')
    logging.getLogger('async_upnp_client').setLevel(logging.INFO)
    run_web_control_point(host=args.host, port=args.port)
    logging.info('Successfully shutdown UPnP-AV WebControlPoint')


if __name__ == '__main__':
    main()
