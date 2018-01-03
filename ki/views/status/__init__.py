import flask
from . import views

def create_app(webapp, **kwargs):
    app = flask.Blueprint("status", __name__, template_folder="templates")
    app.add_url_rule(
        "/",
        view_func=webapp.mk_view(views.StatusView)
    )
    webapp.register_blueprint(app, **kwargs)
