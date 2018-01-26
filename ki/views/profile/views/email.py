import flask
from flask_babel import gettext
import ki.logg
import ki.errors
import ki.emails
from ki.web.decorators import require_login
from ki.webapp import MethodView
from ki.models.auth import verifications
import ki.models.actions as actions_model
import ki.models.users as users_model

from . import (
    mk_menu,
    send_email_verification_link,
)


log = ki.logg.get(__name__)


def _create_verification(tx, user_id, email):
    v_id = verifications.create(
        tx,
        user_id,
        "email-verification",
        3600 * 24,
        verification_data=email,
        _allow_multiple=True,
    )
    return v_id

def _create_verification_link(v_id):
    link = flask.url_for("profile.verify_email", v_id=v_id, _external=True)
    return link


class EditEmailView(MethodView):
    decorators = [require_login]
    template = "views/profile/email/edit.jinja2"

    def get(self, **kwargs):
        return self.mk_response(
            template=self.template,
            profile_menu=mk_menu(),
        )


class EditEmailView(MethodView):
    decorators = [require_login]
    template = "views/profile/email/edit.jinja2"

    def get(self, **kwargs):
        return self.mk_response(
            template=self.template,
            profile_menu=mk_menu(),
        )

    def post(self, **kwargs):
        email = flask.request.form.get("email", None)

        action = actions_model.Action(
            session_id=flask.g.session.id
        )
        with self.api.pgsql.transaction() as tx:
            if not email:
                action.add_error(gettext("Missing email"))
            elif users_model.email_exists(tx, email):
                action.add_error(gettext("Email already exists"))
            else:
                users_model.set_email(tx, flask.g.user, email)
                v_id = _create_verification(tx, flask.g.user.id, email)
                link = _create_verification_link(v_id)
                send_email_verification_link(self.app, flask.g.user, link, email)
                action.add_message(gettext("Please verify your email"))

            tx.connection.commit()

        action.save(self.api)
        return self.redirect("profile.edit_email", action=action)


class ResendVerificationView(MethodView):
    decorators = [require_login]

    def get(self, **kwargs):
        action = actions_model.Action(
            session_id=flask.g.session.id
        )

        if not flask.g.user.email:
            action.add_error(
                gettext("You don't have any email address assigned")
            )
        elif flask.g.user.email_verified_on:
            action.add_error(
                gettext("Your email address is already verified")
            )
        else:
            with self.api.pgsql.transaction() as tx:
                v_id = _create_verification(
                    tx, flask.g.user.id, flask.g.user.email
                )
                link = _create_verification_link(v_id)
                send_email_verification_link(self.app, flask.g.user, link)
                action.add_message(gettext("Verification email sent"))
                tx.connection.commit()

        action.save(self.api)
        return self.redirect("profile.edit_email", action=action)


class VerifyEmailView(MethodView):
    decorators = [require_login]

    def get(self, v_id, **kwargs):
        message = None

        user = flask.g.user

        action = actions_model.Action(
            session_id=flask.g.session.id
        )

        if not v_id:
            action.add_error(gettext("Invalid verification"))
        elif not flask.g.user.email:
            action.add_error(gettext("No email address assigned"))
        elif flask.g.user.email_verified_on:
            action.add_error(gettext("Email address already verified"))
        else:
            with self.api.pgsql.transaction() as tx:
                v = verifications.use(tx, v_id, flask.g.user.id)
                tx.connection.commit()

                if v.verification_data != flask.g.user.email:
                    action.add_error(gettext("Invalid verification"))
                else:
                    users_model.set_email_verified(tx, flask.g.user)
                    action.add_message(gettext("Your email is now verified"))

                tx.connection.commit()

        action.save(self.api)
        return self.redirect("profile.edit_email", action=action)


class RemoveEmailView(MethodView):
    decorators = [require_login]
    template = "views/profile/email/remove.jinja2"

    def get(self, **kwargs):
        return self.mk_response(
            template=self.template,
            profile_menu=mk_menu(),
            user=flask.g.user,
        )

    def post(self, **kwargs):
        email = flask.request.form.get("email", None)
        if not email:
            flask.abort(403)

        ok = False
        with self.api.pgsql.transaction() as tx:
            ok = users_model.remove_email(tx, flask.g.user)
            tx.connection.commit()

        message = ("Email removed" if ok else "Failed to remove email")

        action = actions_model.Action(
            session_id=flask.g.session.id
        )

        if not ok:
            action.add_error(message)
        else:
            action.add_message(message)

        return self.redirect("profile.edit_email", action=action)
