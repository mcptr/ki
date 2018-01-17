import flask
from . import views


def create_app(webapp, **kwargs):
    print(kwargs)
    bp_name = "posts"
    app = flask.Blueprint(
        kwargs.pop("name", bp_name),
         __name__,
        template_folder=kwargs.pop("template_folder", "templates")
    )

    app.add_url_rule(
        "/",
        "main",
        view_func=webapp.mk_view(views.RecentPosts)
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

    app.add_url_rule(
        "/user/<string:username>",
        "by_user",
        view_func=webapp.mk_view(views.PostsByUser)
    )

    app.add_url_rule(
        "/user/<string:username>/page/<int:page>",
        "by_user_paged",
        view_func=webapp.mk_view(views.PostsByUser)
    )

    webapp.register_blueprint(app, **kwargs)
    webapp.register_before_request_hooks(bp_name, [])
