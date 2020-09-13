from starlette.config import Config
from starlette.datastructures import Secret

config = Config(".env")

SECRET_KEY = config('UPNP_AV_CONTROL_SECRET_KEY', cast=Secret, default='super-secret-key-fixme')
EVENT_CALLBACK_PORT = config('UPNP_AV_CONTROL_EVENT_CALLBACK_PORT', cast=int, default=51234)
PUBLIC_IP = config('UPNP_AV_CONTROL_PUBLIC_IP', cast=str, default=None)
QUIET = config('UPNP_AV_CONTROL_QUIET', cast=bool, default=False)
DEBUG = config('UPNP_AV_CONTROL_DEBUG', cast=bool, default=False)
