from .defaults import *

TESTING = True
DEBUG = True

SESSION_USE_SIGNER = True
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_PATH = "/"
PERMANENT_SESSION_LIFETIME = 3600

PGSQL_DSN = "postgresql://ki@localhost:5432/ki-devel"
REDIS_DSN = "redis://localhost:6379/1"

MAIL_SERVER = "localhost"
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USE_SSL = False
MAIL_DEBUG = False
MAIL_USERNAME = "noreply@localhost"
MAIL_PASSWORD = ""
MAIL_DEFAULT_SENDER = "KI <noreply@localhost>"
MAIL_SIGNATURE = ""

CELERY = dict(
    broker_url="redis://localhost:6379/2",
    result_backend="redis://localhost:6379/2",
    enable_utc=True,
)
