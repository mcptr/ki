from ki.webapp import MethodView
from ki.webapp.utils import gettext
from ki.models.posts import posts as model


class PostDetails(MethodView):
    template = "views/post/details.jinja2"

    def get(self, post_id, slug=None):
        print(post_id, slug)

        post = None
        with self.api.pgsql.transaction() as tx:
            post = model.get_post_by_id(tx, int(post_id))

        return self.mk_response(
            template=self.template,
            post=post,
        )
