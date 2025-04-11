import dj_database_url
from .common import *

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='').split(' ')

DATABASES = {
    'default': dj_database_url.parse(config('DATABASE_URL'))
}

