import os

os.environ.setdefault("IS_HTTPS", "no")
os.environ.setdefault("SECRET_KEY", "dummy")
os.environ.setdefault("ENVIRONMENT", "CI")
os.environ.setdefault("SENDFILE_BACKEND", "django_sendfile.backends.simple")

from .base import *  # noqa isort:skip
