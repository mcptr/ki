import flask
import flask_session

import ki.logg
import ki.models.sessions
import ki.models.users


log = ki.logg.get(__name__)


def load_user(api):
    log.info("Loading user")
    flask.g.user = None

    sess = ki.models.sessions.Session(id=flask.session.sid)
    with api.pgsql.transaction() as tx:
        r = ki.models.sessions.load(tx, sess)
        flask.g.session = ki.models.sessions.Session(**r) if r else sess
        if flask.g.session.terminated:
            flask.abort(401)
        if flask.g.session.user_id:
            u = ki.models.users.User(flask.g.session.user_id)
            r = ki.models.users.load(u)
            flask.g.user = ki.models.users.User(**r) if r else None

        if flask.g.session:
            ki.models.sessions.touch(tx, flask.g.session)
    # sua = session.get("user_agent")[0]
    # ua = flask.request.headers.get("User-agent", "")
    # if sua and (ua != sua):
    #     log.error("Session user-agent mismatch. User id: %s ", user_id)
    #     flask.abort(401)
    # else:
    #     r = users_model.get(user_id, True)
    #     flask.g.user = User(**(r._asdict() if r else {}))


# @app.before_request
# def csrf_protect():
#     # if testing... this sucks
#     if app.config.get("TESTING", False):
#         return None
#     if flask.request.method in ["POST", "PUT"]:
#         token = flask.session.pop("_csrf_token", None)
#         if not token or token != flask.request.form.get("_csrf_token"):
#             log.warning("Invalid csrf token")
#             flask.abort(403)
