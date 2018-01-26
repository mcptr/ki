import flask
from flask_babel import gettext
import hashlib
import uuid
from ki.webapp import MethodView
import ki.models.actions as actions_model
import ki.models.users as users_model
from ki.models.auth import verifications
from . import send_recovery_link


def _create_recovery_link(verification_id, v_hash):
    return flask.url_for(
        "profile.recovery_auth",
        v_id=verification_id,
        v_hash=v_hash,
        _external=True
    )


def _create_verification_hash(user_id, email, random_bits):
    s = "user:%s:%s:%s" % (user_id, email, random_bits)
    return hashlib.md5(s.encode("utf-8")).hexdigest()


class RecoveryView(MethodView):
    template = "views/profile/recovery/email_form.jinja2"

    def get(self, **kwargs):
        if flask.g.user and flask.g.user.id:
            return self.redirect("profile.main")

        return self.mk_response(
            template=self.template,
        )

    def post(self, **kwargs):
        if flask.g.user and flask.g.user.id:
            return self.redirect("profile.main")

        action = actions_model.Action(
            session_id=flask.g.session.id
        )

        email = flask.request.form.get("email", None)
        if not email:
            action.add_error(gettext("No email provided"))
        else:
            with self.api.pgsql.transaction() as tx:
                u = users_model.get_by_email(tx, email)
                if not u:
                    action.add_error(gettext("Invalid email"))
                elif not u.email_verified_on:
                    action.add_error(gettext("Your email is not verified."))
                    action.add_error(gettext("Please contact our support."))
                else:
                    v_hash = _create_verification_hash(
                        u.id, u.email, str(uuid.uuid4())
                    )

                    v_id = verifications.create(
                        tx,
                        u.id,
                        "profile-recovery",
                        1200,
                        verification_data=v_hash,
                    )

                    if v_id:
                        link = _create_recovery_link(v_id, v_hash)
                        send_recovery_link(self.app, u, link)
                        action.add_message(
                            gettext("Recovery link was sent to your email")
                        )
                tx.connection.commit()

        action.save(self.api)
        return self.redirect("profile.recovery", action=action)


class RecoveryAuthView(MethodView):
    def get(self, v_id, v_hash, **kwargs):
        action = actions_model.Action(
            session_id=flask.g.session.id
        )

        ok = False

        with self.api.pgsql.transaction() as tx:
            v = verifications.use_no_user(tx, v_id)
            tx.connection.commit()

            ok = (v and v.user_id and v.verification_data == v_hash)
            if ok:
                u = users_model.User(id=v.user_id)
                flask.g.session.set_user(tx, u, 300, True)
                action.add_message(gettext("Remember to set a new password."))
            else:
                action.add_error(gettext("Invalid verification"))
            tx.connection.commit()

        action.save(self.api)

        if not ok:
            return self.redirect("profile.recovery", action=action)
        else:
            return self.redirect("profile.edit_password", action=action)
