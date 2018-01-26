import flask
from .views import (
    email,
    login,
    logout,
    overview,
    password,
    recovery,
    removal,
    signup
)


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
        view_func=webapp.mk_view(overview.MainView)
    )

    app.add_url_rule(
        "/login",
        "login",
        view_func=webapp.mk_view(login.LoginView)
    )

    app.add_url_rule(
        "/logout",
        "logout",
        view_func=webapp.mk_view(logout.LogoutView)
    )

    app.add_url_rule(
        "/signup",
        "signup",
        view_func=webapp.mk_view(signup.SignUpView)
    )

    app.add_url_rule(
        "/recovery",
        "recovery",
        view_func=webapp.mk_view(recovery.RecoveryView)
    )

    app.add_url_rule(
        "/recovery/<string:v_id>/<string:v_hash>",
        "recovery_auth",
        view_func=webapp.mk_view(recovery.RecoveryAuthView)
    )

    # app.add_url_rule(
    #     "/recovery/password/<string:v_id>",
    #     "recovery_password_change",
    #     view_func=webapp.mk_view(recovery.RecoveryPasswordChangeView)
    # )

    app.add_url_rule(
        "/settings/password",
        "edit_password",
        view_func=webapp.mk_view(password.EditPasswordView)
    )

    app.add_url_rule(
        "/settings/email",
        "edit_email",
        view_func=webapp.mk_view(email.EditEmailView)
    )

    app.add_url_rule(
        "/settings/email/resend-verification",
        "resend_verification",
        view_func=webapp.mk_view(email.ResendVerificationView)
    )

    app.add_url_rule(
        "/settings/email/remove",
        "remove_email",
        view_func=webapp.mk_view(email.RemoveEmailView)
    )

    app.add_url_rule(
        "/settings/email/verify/<string:v_id>",
        "verify_email",
        view_func=webapp.mk_view(email.VerifyEmailView)
    )

    app.add_url_rule(
        "/remove",
        "remove",
        view_func=webapp.mk_view(removal.AccountRemovalView)
    )

    webapp.register_blueprint(app, **kwargs)
    webapp.register_before_request_hooks(bp_name, [])
