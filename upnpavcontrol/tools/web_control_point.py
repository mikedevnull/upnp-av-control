import logging
import argparse
from upnpavcontrol.web import app as web_app
from upnpavcontrol.web import settings
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
        action="store_true",
    )
    parser.add_argument('-v', '--verbose', help="Verbose logging", action="store_true")
    parser.add_argument('--host', help="Host to bind", type=str, default="127.0.0.1")
    parser.add_argument('--port', help="Port to listen", type=int, default=8000)
    args = parser.parse_args()
    settings.QUIET = not args.verbose
    settings.DEBUG = args.debug
    run_web_control_point(host=args.host, port=args.port)
    logging.info('Successfully shutdown UPnP-AV WebControlPoint')


if __name__ == '__main__':
    main()
