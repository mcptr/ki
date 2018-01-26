import flask
from flask_babel import gettext
import ki.logg
import ki.errors
from ki.webapp import MethodView
from ki.web.decorators import require_login
import ki.models.actions as actions_model
import ki.models.users as users_model
from . import (mk_menu, send_notification_email)


log = ki.logg.get(__name__)


class AccountRemovalView(MethodView):
    decorators = [require_login]
    template = "views/profile/removal.jinja2"

    def get(self, **kwargs):
        return self.mk_response(
            template=self.template,
            profile_menu=mk_menu(),
        )

    def post(self, **kwargs):
        log.info("Account removal: user: %s", flask.g.user.name)

        keep_username = flask.request.form.get("keep-username", False)
        keep_comments = flask.request.form.get("keep-comments", False)

        action = actions_model.Action()

        redirect = None

        try:
            email = (
                flask.g.user.email
                if flask.g.user.email_verified_on else None
            )
            locale = flask.g.user.locale

            with self.api.pgsql.transaction() as tx:
                users_model.delete(
                    tx,
                    flask.g.user,
                    keep_username=keep_username,
                    keep_comments=keep_comments,
                )
                tx.connection.commit()

                action.add_message(gettext("Your profile was removed."))
                flask.g.session.destroy(tx)
                flask.session.clear()

                if email:
                    content = self.app.flask_app.render_l10n_template(
                        locale,
                        "emails/notification.jinja2",
                        content=gettext("Your profile was remoed."),
                    )
                    send_notification_email(
                        email,
                        gettext("Profile removed"),
                        content
                    )
        except ki.errors.Error as e:
            log.exception(e)
            action.add_error(gettext("Unable to remove your account."))

        action.save(self.api)
        return self.redirect("message.message", action=action)
