import flask
from . import views


def create_app(webapp, **kwargs):
    bp_name = "posts"
    app = flask.Blueprint(
        bp_name,
        __name__,
        template_folder=kwargs.pop("template_folder", "templates")
    )

    app.add_url_rule(
        "/recent",
        "recent",
        view_func=webapp.mk_view(views.RecentPosts)
    )

    app.add_url_rule(
        "/recent/page/<int:page>",
        "recent_paged",
        view_func=webapp.mk_view(views.RecentPosts)
    )

    app.add_url_rule(
        "/tag/<string:tag>",
        "by_tag",
        view_func=webapp.mk_view(views.PostsByTag)
    )

    app.add_url_rule(
        "/tag/<string:tag>/page/<int:page>",
        "by_tag_paged",
        view_func=webapp.mk_view(views.PostsByTag)
    )

    webapp.register_blueprint(app, **kwargs)
    webapp.register_before_request_hooks(bp_name, [])
