import flask
from flask_babel import gettext
import ki.errors
from ki.web.decorators import require_login
from ki.webapp import MethodView
import ki.models.actions as actions_model
import ki.models.users as users_model
from . import (mk_menu, send_notification_email)


class EditPasswordView(MethodView):
    decorators = [require_login]
    template = "views/profile/password.jinja2"

    def get(self, **kwargs):
        return self.mk_response(
            template=self.template,
            profile_menu=mk_menu(),
        )

    def post(self, **kwargs):
        password = flask.request.form.get("password", None)
        repeated = flask.request.form.get("repeated", None)

        action = actions_model.Action(
            session_id=flask.g.session.id
        )

        if not (password and repeated) or (password != repeated):
            action.add_error(gettext("Passwords did not match"))
        else:
            with self.api.pgsql.transaction() as tx:
                try:
                    users_model.set_password(tx, flask.g.user, password)
                    action.add_message(gettext("Password changed successfully"))

                    if flask.g.user.email and flask.g.user.email_verified_on:
                        content = self.app.flask_app.render_l10n_template(
                            flask.g.user.locale,
                            "emails/notification.jinja2",
                            content=gettext("Your password has been changed."),
                            user=flask.g.user,
                        )
                        send_notification_email(
                            flask.g.user.email,
                            gettext("Password changed"),
                            content
                        )
                except ki.errors.ValidationError as e:
                    action.add_error(str(e))

        action.save(self.api)

        return self.redirect("profile.edit_password", action=action)
