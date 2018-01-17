from ki.webapp import MethodView
from ki.webapp.utils import gettext
from ki.models.posts import posts as posts_model
from ki.models.posts import comments as comments_model


class PostDetails(MethodView):
    template = "views/post/details.jinja2"

    def get(self, post_id, slug=None):
        print(post_id, slug)

        post = None
        comments = []
        with self.api.pgsql.transaction() as tx:
            post = posts_model.get_post_by_id(tx, int(post_id))
            comments = comments_model.get_comments_tree(tx, post_id)

        return self.mk_response(
            template=self.template,
            post=post,
            comments=comments,
        )
