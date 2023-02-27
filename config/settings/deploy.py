from .base import *

# DEBUG = False
ALLOWED_HOSTS = ["www.bistime.app", "bistime.app"]
WSGI_APPLICATION = "config.wsgi.deploy.application"
STATIC_ROOT = BASE_DIR / "static/"
STATICFILES_DIRS = []
