from .base import *

# DEBUG = False
ALLOWED_HOSTS = [
    ".ap-northeast-2.compute.amazonaws.com",
    "3.35.9.60",
]  # 인스턴스 IPv4 기반 퍼블릭 DNS 주소 or 퍼블릭 IP
WSGI_APPLICATION = "config.wsgi.deploy.application"

STATIC_ROOT = BASE_DIR / "static/"
STATICFILES_DIRS = []
