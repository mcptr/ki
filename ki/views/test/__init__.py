import flask
from . import views


def create_app(webapp, **kwargs):
    bp_name = "test"
    app = flask.Blueprint(
        bp_name,
        __name__,
        template_folder=kwargs.pop("template_folder", "templates")
    )

    app.add_url_rule(
        "/email",
        "email_test",
        view_func=webapp.mk_view(views.EmailTest)
    )

    webapp.register_blueprint(app, **kwargs)
    webapp.register_before_request_hooks(bp_name, [])
