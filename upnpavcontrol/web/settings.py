from starlette.config import Config
from starlette.datastructures import Secret

config = Config(".env")

SECRET_KEY = config('UPNP_AV_CONTROL_SECRET_KEY', cast=Secret, default='super-secret-key-fixme')
QUIET = config('UPNP_AV_CONTROL_QUIET', cast=bool, default=False)
DEBUG = config('UPNP_AV_CONTROL_DEBUG', cast=bool, default=False)
