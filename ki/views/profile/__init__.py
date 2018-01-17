import flask
from . import views


def create_app(webapp, **kwargs):
    bp_name = "profile"
    app = flask.Blueprint(
        bp_name,
        __name__,
        template_folder=kwargs.pop("template_folder", "templates")
    )
    app.add_url_rule(
        "/",
        "main",
        view_func=webapp.mk_view(views.MainView)
    )

    app.add_url_rule(
        "/login",
        "login",
        view_func=webapp.mk_view(views.LoginView)
    )

    app.add_url_rule(
        "/signup",
        "signup",
        view_func=webapp.mk_view(views.SignUpView)
    )

    app.add_url_rule(
        "/recovery",
        "recovery",
        view_func=webapp.mk_view(views.RecoveryView)
    )

    app.add_url_rule(
        "/logout",
        "logout",
        view_func=webapp.mk_view(views.LogoutView)
    )

    webapp.register_blueprint(app, **kwargs)
    webapp.register_before_request_hooks(bp_name, [])
