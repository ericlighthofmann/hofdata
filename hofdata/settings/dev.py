from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '7!sc##evq!k!1kbgk5mhnj-ou03z@c6$+=tqzro#@gozd=&w$y'

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = ['*']

#Email settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'ericlighthofmann@gmail.com'
#TODO: hide this in a environmental variable in production
EMAIL_HOST_PASSWORD = 'Griffey98632!'
EMAIL_PORT = 587

try:
    from .local import *
except ImportError:
    pass
