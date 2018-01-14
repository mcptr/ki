import flask
import flask_session

import ki.logg
import ki.models.sessions
import ki.models.users


log = ki.logg.get(__name__)


def load_user(app):
    log.info("Loading user")
    api = app.api
    flask.g.user = None
    current_user_agent = flask.request.headers.get("user-agent", ""),
    sess = ki.models.sessions.Session(
        id=flask.session.sid,
        user_agent=current_user_agent,
    )

    with api.pgsql.transaction() as tx:
        r = ki.models.sessions.load(tx, sess)
        flask.g.session = ki.models.sessions.Session(**r) if r else sess
        if flask.g.session.terminated:
            flask.abort(401)

        if flask.g.session:
            sua = flask.g.session.user_agent
            ki.models.sessions.touch(tx, flask.g.session)

        if sua and (current_user_agent != sua):
            log.error("Session user-agent mismatch. User id: %s ", user_id)
            flask.abort(401)
        else:
            user_data = dict()
            if flask.g.session.user_id:
                u = ki.models.users.User(flask.g.session.user_id)
                user_data = ki.models.users.load(u)
            flask.g.user = ki.models.users.User(**user_data) if user_data else None


def csrf_protect(*args, **kwargs):
    if flask.request.method in ["POST", "PUT"]:
        token = flask.session.pop("_csrf_token", None)
        if not token or token != flask.request.form.get("_csrf_token"):
            log.warning("Invalid csrf token")
            flask.abort(403)


def require_login(app):
    u = flask.g.user
    if not (u and u.id and u.is_active and not u.is_deleted):
        flask.abort(401)


def debug(app):
    # fix for jinja fuckups.
    app.flask_app.jinja_env.cache = {}
