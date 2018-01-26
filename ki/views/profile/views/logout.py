import flask
from ki.webapp import MethodView
from ki.web.decorators import require_login


class LogoutView(MethodView):
    decorators = [require_login]

    def get(self, **kwargs):
        with self.api.pgsql.transaction() as tx:
            flask.g.session.destroy(tx)
            tx.connection.commit()

        flask.session.clear()
        return self.redirect("home.main")
