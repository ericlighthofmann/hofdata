from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '7!sc##evq!k!1kbgk5mhnj-ou03z@c6$+=tqzro#@gozd=&w$y'

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = ['hofdata.com', 'www.hofdata.com', '68.183.169.105']

try:
    from .local import *
except ImportError:
    pass
