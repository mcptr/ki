import flask
from .views import post
from .views import comments


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
        view_func=webapp.mk_view(post.Details)
    )

    app.add_url_rule(
        "/<int:post_id>/<string:slug>",
        "details",
        view_func=webapp.mk_view(post.Details)
    )

    app.add_url_rule(
        "/edit/<int:post_id>",
        "edit",
        view_func=webapp.mk_view(post.Edit)
    )

    app.add_url_rule(
        "/save",
        "save",
        view_func=webapp.mk_view(post.Save)
    )

    app.add_url_rule(
        "/comments/save",
        "save_comment",
        view_func=webapp.mk_view(comments.Save)
    )

    app.add_url_rule(
        "/comments/delete/<int:comment_id>",
        "delete_comment",
        view_func=webapp.mk_view(comments.Delete)
    )

    webapp.register_blueprint(app, **kwargs)
    webapp.register_before_request_hooks(bp_name, [])
