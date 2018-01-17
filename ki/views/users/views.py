from ki.webapp import MethodView
from ki.webapp.utils import gettext
from ki.models import users as user_model
from ki.models.posts import posts as posts_model
import ki.web.pagination


class UserInfoView(MethodView):
    template = "views/users/user.jinja2"

    def get(self, name):
        user = None
        posts = []
        with self.api.pgsql.transaction() as tx:
            user = user_model.get_user_info(tx, name)
            posts = posts_model.get_posts_by_user(tx, name, 0, 3)

        return self.mk_response(
            template=self.template,
            user_info=user,
            posts=posts,
        )
