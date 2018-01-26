from ki.webapp import MethodView
from ki.webapp.utils import gettext
from ki.models.posts import posts as posts_model
from ki.models.posts import comments as comments_model


class Details(MethodView):
    template = "views/post/details.jinja2"

    def get(self, post_id, slug=None, **kwargs):
        post = None
        comments = []
        with self.api.pgsql.transaction() as tx:
            post = posts_model.get_post_by_id(tx, int(post_id))
            comments = comments_model.get_comments_tree(tx, post_id)

        return self.mk_response(
            template=self.template,
            post=post,
            comments=comments,
            reply_to_id=self.get_argument("reply_to_id", None, int),
            edit_comment_id=self.get_argument("edit_comment_id", None, int),
        )


class Edit(MethodView):
    template = "views/post/edit.jinja2"

    def get(self, post_id):
        print(post_id)
        return self.mk_response(
            template=self.template,
        )


class Save(MethodView):
    template = "views/post/edit.jinja2"

    def get(self, post_id):
        print(post_id, slug)
        return self.mk_response(
            template=self.template,
        )
