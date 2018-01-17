import flask
from . import views


def create_app(webapp, **kwargs):
    bp_name = "post"
    app = flask.Blueprint(
        bp_name,
        __name__,
        template_folder=kwargs.pop("template_folder", "templates")
    )

    app.add_url_rule(
        "/<int:post_id>",
        "details_without_slug",
        view_func=webapp.mk_view(views.PostDetails)
    )

    app.add_url_rule(
        "/<int:post_id>/<string:slug>",
        "details",
        view_func=webapp.mk_view(views.PostDetails)
    )

    webapp.register_blueprint(app, **kwargs)
    webapp.register_before_request_hooks(bp_name, [])
