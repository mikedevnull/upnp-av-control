from starlette.config import Config
from starlette.datastructures import Secret

config = Config(".env")

SECRET_KEY = config('SECRET_KEY', cast=Secret, default='super-secret-key-fixme')