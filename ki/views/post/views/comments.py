import flask
from ki.webapp import MethodView
from ki.webapp.utils import gettext
from ki.models.posts import posts as posts_model
from ki.models.posts import comments as comments_model
from ki.web.decorators import require_login

# from voluptuous import Schema, Required, Optional, All, Length, Range


# schema_comment_save = Schema({
#     Required("post_id", msg="Missing post id"): All(int, Range(min=1)),
#     Required("content", msg="Missing comment content"): All(str, Length(min=1)),
#     Optional("parent_id", msg="Invalid parent comment"): All(int, Range(min=1)),
# })


class Save(MethodView):
    decorators = [require_login]

    def post(self, **kwargs):
        f = self.get_form()
        post_id = int(f.get("post_id", None) or 0)
        comment_id = int(f.get("comment_id", None) or 0)
        parent_id = (int(f.get("parent_id", 0)) or None)
        content = str(f.get("content", None) or "")

        if not post_id:
            self.abort(402)

        u = flask.g.user
        with self.api.pgsql.transaction() as tx:
            post_record = posts_model.get_post_by_id(tx, post_id)

            if not post_record:
                self.abort(404)

            saved_comment_id = None
            if comment_id:
                orig = comments_model.get(tx, comment_id)
                if not orig:
                    self.abort(404)

                is_same_user = (u.id == orig.user_id)
                is_admin = u.is_admin
                is_moderator = u.is_moderator

                if not (is_same_user or u.is_admin or u.is_moderator):
                    self.abort(403)

                saved_comment_id = comments_model.update(tx, comment_id, content)
            else:
                saved_comment_id = comments_model.create(
                    tx,
                    post_record["id"],
                    content,
                    user_id=flask.g.user.id,
                    parent_id=parent_id
                )

            tx.connection.commit()
            anchor = None
            if saved_comment_id:
                anchor = "comment-%d" % (
                    saved_comment_id if saved_comment_id else None
                )
            else:
                anchor = "comment-%d" % parent_id if parent_id else None

            print("#########", saved_comment_id)
            return self.redirect(
                "post.details",
                post_id=post_record["id"],
                slug=post_record["slug"],
                _anchor=anchor,
            )


class Delete(MethodView):
    decorators = [require_login]
    template = "views/post/edit.jinja2"

    def get(self, comment_id):
        post = None
        with self.api.pgsql.transaction() as tx:
            saved = comments_model.get(tx, comment_id)
            if not saved:
                self.abort(404)

            is_same_user = (flask.g.user.id == saved.user_id)
            is_admin = flask.g.user.is_admin
            is_moderator = flask.g.user.is_moderator

            if not (is_admin or is_moderator or is_same_user):
                self.abort(403)

            comments_model.delete(tx, comment_id)
            post = posts_model.get_post_by_id(tx, saved.post_id)
            tx.connection.commit()

        if post:
            return self.redirect(
                "post.details",
                post_id=post.get("id", 0),
                slug=post.get("slug", ""),
            )
        else:
            return self.redirect("posts.main")
