import uuid
import flask
import flask_session

import ki.logg
import ki.models.sessions
import ki.models.users


log = ki.logg.get(__name__)


def remove_expired_sessions(app):
    ki.models.sessions.remove_expired(app.api)


def load_user(app):
    api = app.api
    flask.g.user = None
    flask.g.session = None

    session_id = flask.session.get("id", None)
    if not session_id:
        session_id = str(uuid.uuid4())
        flask.session["id"] = session_id

    current_user_agent = flask.request.headers.get("user-agent", "")

    sess = ki.models.sessions.Session(
        id=session_id,
        user_agent=current_user_agent,
    )
    with api.pgsql.transaction() as tx:
        r = ki.models.sessions.load(tx, sess)

        flask.g.session = ki.models.sessions.Session(**r._asdict()) if r else sess

        sua = flask.g.session.user_agent

        if sua and (current_user_agent != sua):
            log.error("Session user-agent mismatch. Session id: %s ", flask.g.session.id)
            flask.abort(401)

        ki.models.sessions.touch(tx, flask.g.session)
        user_data = dict()

        if flask.g.session.user_id:
            log.info("Loading user: %s", flask.g.session.user_id)
            u = ki.models.users.User(id=flask.g.session.user_id)
            user_data = ki.models.users.get(tx, u)
            print(u.as_dict(), user_data)
        flask.g.user = ki.models.users.User(**user_data._asdict()) if user_data else None
        tx.connection.commit()


def csrf_protect(*args, **kwargs):
    if flask.request.method in ["POST", "PUT"]:
        token = flask.session.pop("_csrf_token", None)
        if not token or token != flask.request.form.get("_csrf_token"):
            log.warning("Invalid csrf token")
            flask.abort(403)


def debug_mode_hooks(app):
    app.flask_app.config.update(TEMPLATES_AUTO_RELOAD=True)
    # fix for jinja fuckups.
    app.flask_app.jinja_env.cache = {}
