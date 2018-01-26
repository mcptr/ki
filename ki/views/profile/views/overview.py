import flask
from ki.webapp import MethodView
from ki.web.decorators import require_login
import ki.models.users as users_model

from . import mk_menu


class MainView(MethodView):
    decorators = [require_login]
    template = "views/profile/main.jinja2"

    def get(self, **kwargs):
        with self.api.pgsql.transaction() as tx:
            u = users_model.get_user_info(tx, flask.g.user.name)
        return self.mk_response(
            template=self.template,
            profile_menu=mk_menu(),
            # subnav=mk_subnav(),
            profile_user=u,
        )
