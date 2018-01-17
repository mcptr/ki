import flask
from . import views


def create_app(webapp, **kwargs):
    bp_name = "help"
    app = flask.Blueprint(
        bp_name,
        __name__,
        template_folder=kwargs.pop("template_folder", "templates")
    )

    app.add_url_rule(
        "/formatting",
        "content_formatting",
        view_func=webapp.mk_view(views.ContentFormatting)
    )

    webapp.register_blueprint(app, **kwargs)
    webapp.register_before_request_hooks(bp_name, [])
