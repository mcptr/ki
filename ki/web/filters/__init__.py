import jinja2
import flask
import ago
import markdown
import urllib.parse
import cgi
import time

import ki.logg
from ki.web.utils import mk_slug


log = ki.logg.get(__name__)


def slug(value, limit):
    return mk_slug(value, limit)


def quote_plus(value):
    return urllib.parse.quote_plus(value)


def to_ago_string(value):
    # a hack:
    r = ago.human(value, precision=1)
    if "microseconds" in r or "milliseconds" in r:
        return "just now"
    return r


def ts_to_datetime_str(value):
    return time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(value))


def ts_to_date_str(value):
    return time.strftime("%Y-%m-%d", time.gmtime(value))


def md_to_html(value):
    return markdown.markdown(value)


def escape(value):
    return cgi.escape(value)


def register(app):
    f = [
        slug,
        quote_plus,
        to_ago_string,
        ts_to_datetime_str,
        ts_to_date_str,
        md_to_html,
        escape
    ]
    for flt in f:
        log.debug("Registering jinja filter: %s", flt.__name__)
        app.jinja_env.filters[flt.__name__] = flt
