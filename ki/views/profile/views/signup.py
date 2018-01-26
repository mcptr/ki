import flask
from flask_babel import gettext

import ki.logg
import ki.emails
import ki.errors
from ki.webapp import MethodView
import ki.models.users as users_model
import ki.models.actions as actions_model
from . import send_email_verification_link


log = ki.logg.get(__name__)


class SignUpView(MethodView):
    template = "views/profile/signup.jinja2"

    def get(self, **kwargs):
        return self.mk_response(
            template=self.template,
        )

    def post(self, **kwargs):
        name = flask.request.form.get("name", "").lower()
        password = flask.request.form.get("password", None)
        email = (flask.request.form.get("email", None) or None)

        new_user = users_model.User(
            name=name,
            email=email
        )
        new_user.password = password

        ok = False
        message = None
        action_id = None

        action = actions_model.Action(
            session_id=flask.g.session.id
        )
        with self.api.pgsql.transaction() as tx:
            try:
                if not name:
                    message = gettext("Missing username")
                    action.add_error(message)
                elif users_model.user_exists(tx, new_user):
                    message = gettext("User already exists")
                    action.add_error(message)
                elif email and users_model.email_exists(tx, email):
                    message = gettext("Email already exists")
                    action.add_error(message)
                else:
                    user = users_model.create(tx, new_user)
                    if not user.id:
                        message = gettext("Signing up failed")
                        action.add_error(message)
                    else:
                        new_user.id = user.id
                        user = users_model.get(tx, new_user)
                        ok = True
                        message = gettext("Profile created")
                        action.add_message(message)

                        if user.email:
                            send_email_verification_link(self.app, user)
            except ki.errors.ValidationError as e:
                message = str(e)
                ok = False
                action.add_error(message)

        action.save(self.api)

        if ok:
            return self.redirect("profile.login", action=action)

        return self.redirect("profile.signup", action=action)
