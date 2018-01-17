import jinja2
import flask
import uuid


def _user_name(name):
    return name[:32] + ("~" if len(name) > 32 else "")


def _email(value):
    r = ""
    if value:
        try:
            (username, domain) = value.split("@")
            r = "@".join([
                username[:32] + ("..." if len(value) > 32 else ""),
                domain
            ])
        except Exception:
            r = value
    return r


def _generate_csrf_token():
    if "_csrf_token" not in flask.session:
        flask.session["_csrf_token"] = str(uuid.uuid4())
    return flask.session["_csrf_token"]


def register(app):
    app.jinja_env.globals.update(user_name=_user_name)
    app.jinja_env.globals.update(email=_email)
    app.jinja_env.globals.update(csrf_token=_generate_csrf_token)
