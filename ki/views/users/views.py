from ki.webapp import MethodView
from ki.webapp.utils import gettext
from ki.models.posts import posts as model


class UserView(MethodView):
    template = "views/users/user.jinja2"

    def get(self, user):

        return self.mk_response(
            template=self.template,
        )
