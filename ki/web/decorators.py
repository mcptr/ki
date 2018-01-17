import flask
import ki.logg


log = ki.logg.get(__name__)


def require_login(view):
    def f(*args, **kwargs):
        u = flask.g.user
        if not (u and u.id and u.is_active and not u.is_closed):
            log.warning("require_login: Not authorized: %s", u.id if u else None)
            return flask.redirect(flask.url_for("profile.login"))
        return view(*args, **kwargs)
    return f
