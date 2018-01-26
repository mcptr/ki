import flask
from flask_babel import gettext
import ki.logg
import ki.errors
import ki.models.users as users_model
from ki.webapp import MethodView


log = ki.logg.get(__name__)


class LoginView(MethodView):
    template = "views/profile/login.jinja2"

    def get(self, **kwargs):
        if flask.g.user:
            return self.redirect("profile.main")

        next_url = flask.request.args.get("next_url")
        if next_url:
            with self.api.pgsql.transaction() as tx:
                updated = flask.g.session.update(tx, dict(
                    next_url=next_url
                ))
                tx.connection.commit()

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
        next_url = None

        try:
            with self.api.pgsql.transaction() as tx:
                uid = users_model.authenticate(tx, u)

                if uid:
                    u = users_model.User(id=uid)
                    ua = flask.request.headers.get("User-agent", "")
                    sid = flask.session.get("id", None)
                    flask.g.session.set_user(tx, u)
                    next_url = flask.g.session.get("next_url")
                    if next_url:
                        next_url = ki.std.urlparse(next_url).path

                tx.connection.commit()
                ok = uid
        except ki.errors.DatabaseError as e:
            log.exception(e)

        if ok:
            if next_url:
                return self.redirect_url(next_url)
            else:
                return self.redirect("profile.main")
        else:
            return self.redirect("profile.login")
