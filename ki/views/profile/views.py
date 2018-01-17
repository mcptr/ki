import flask
from flask_babel import gettext
import ki.std
import ki.logg
import ki.errors
import ki.models.users as users_model
import ki.models.sessions as session_model
import ki.models.actions as actions_model
from ki.webapp import MethodView
from ki.web.decorators import require_login


log = ki.logg.get(__name__)


def _mk_menu():
    menu = [
        dict(
            section="Account",
            elements=[
                # dict(
                #     href=flask.url_for("profile.dashboard"),
                #     caption="Profile overview",
                # ),
                # dict(
                #     href=flask.url_for("profile.edit_password"),
                #     caption="Change password",
                # ),
                # dict(
                #     href=flask.url_for("profile.edit_email"),
                #     caption="Manage email address",
                # ),
                # dict(
                #     href=flask.url_for("profile.remove"),
                #     caption="Account removal",
                # ),
            ]
        ),
        # dict(
        #     section="Content",
        #     elements=[
        #         dict(
        #             href="#",
        #             caption="Posts",
        #         ),
        #         dict(
        #             href="#",
        #             caption="Comments",
        #         ),
        #     ]
        # )
    ]
    return menu


def _mk_subnav():
    return [
        dict(
            href=flask.url_for("profile.logout"),
            caption=gettext("Logout"),
        ),
    ]


class MainView(MethodView):
    decorators = [require_login]
    template = "views/profile/main.jinja2"

    def get(self, **kwargs):
        return self.mk_response(
            template=self.template,
            profile_menu=_mk_menu(),
            subnav=_mk_subnav(),
        )


class LoginView(MethodView):
    template = "views/profile/login.jinja2"

    def get(self, **kwargs):
        if flask.g.user:
            print(flask.g.user.id)
            return self.redirect("profile.main")

        return self.mk_response(
            template=self.template,
        )

    def post(self, **kwargs):
        if flask.g.user:
            return self.redirect("profile.main")

        f = flask.request.form.to_dict()
        u = users_model.User(**f)
        u.password = f.get("password", None)

        ok = False
        action_id = None

        try:
            with self.api.pgsql.transaction() as tx:
                uid = users_model.authenticate(tx, u)
                msg = "Unable to login" if not ok else None
                action_id = actions_model.store(tx, "login", bool(uid), message=msg)

                if uid:
                    u = users_model.User(id=uid)
                    ua = flask.request.headers.get("User-agent", "")
                    sid = flask.session.get("id", None)
                    sess = session_model.create(tx, u, ua, id=sid)
                    session_model.touch(tx, sess)
                    # next_url = flask.g.session.get_field("next_url")
                    # if next_url:
                    #     next_url = ki.std.urlparse(next_url).path
                    print("Created SESSION", sess)

                tx.connection.commit()
                ok = uid
        except ki.errors.DatabaseError as e:
            log.exception(e)
            pass

        print("AUTH OK", ok)
        if ok:
            return self.redirect("profile.main")
        else:
            print("AUTH NOT OK", ok)
            return self.redirect("profile.login", action=action_id)


class SignUpView(MethodView):
    template = "views/profile/signup.jinja2"

    def get(self, **kwargs):
        return self.mk_response(
            template=self.template,
        )


class RecoveryView(MethodView):
    template = "views/profile/recovery.jinja2"

    def get(self, **kwargs):
        return self.mk_response(
            template=self.template,
        )


class LogoutView(MethodView):
    decorators = [require_login]

    def get(self, **kwargs):
        with self.api.pgsql.transaction() as tx:
            sess = session_model.destroy(tx, flask.g.session)
            tx.connection.commit()

        flask.session.clear()
        return self.redirect("home.main")
