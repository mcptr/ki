import os


def get_base_dir(f):
    return os.path.join(
        os.path.dirname(os.path.abspath(f)),
        ".."
    )


TESTING = False
DEBUG = False

SESSION_USE_SIGNER = True
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_PATH = "/"
PERMANENT_SESSION_LIFETIME = 3600

PGSQL_DSN = ""
REDIS_DSN = ""

MAIL_SERVER = "localhost"
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USE_SSL = False
MAIL_DEBUG = False
MAIL_USERNAME = "noreply@localhost"
MAIL_PASSWORD = ""
MAIL_DEFAULT_SENDER = "KI <noreply@localhost>"
MAIL_SIGNATURE = ""


TEMPLATE_FOLDER = os.path.join(get_base_dir(__file__), "templates")

CELERY = dict(
    broker_url="redis://localhost:6379/2",
    result_backend="redis://localhost:6379/2",
    enable_utc=True,
)
