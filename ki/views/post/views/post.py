import time
import json
import ki.logg
from ki.webapp import MethodView
from ki.webapp.utils import gettext
from ki.models.posts import posts as posts_model
from ki.models.posts import comments as comments_model
from ki.models.cache import Cache

# TODO: require login


log = ki.logg.get(__name__)


# class PostEditorState:
#     def __init__(self, session_id):
#         self.session = session
#         self.key = "post-editor-state"
#         self.state = dict()

#     def load(self):
#         data = self.session.get(self.key, None)
#         if data:
#             self.state.update(data)
#         return self.state

#     def update(self, post=None):
#         post = (post or dict())
#         self.state.update(
#             post_id=post.get("id", None),
#             post=post,
#         )
#         st = dict()
#         st[self.key] = self.state
#         self.session.update(self.tx, st)

#     def match_post_id(self, post_id):
#         try:
#             state_post_id = self.state.get("post_id", None)
#             if not state_post_id:
#                 return True
#             return (state_post_id and int(post_id) == int(state_post_id))
#         except Exception as e:
#             log.exception(e)
#         return False

#     def clear(self):
#         log.info("Clearing post editor state")
#         self.session.remove(self.key)
#         self.update()


class EditorCache:
    def __init__(self, api, session_id, post_id):
        self.key = "%s-post-editor-cache-%s" % (session_id, post_id)
        self.cache = api.cache.get_connection()

    def load(self):
        d = self.cache.get(self.key)
        if d:
            return json.loads(d)
        return dict()

    def store(self, post):
        return self.cache.set(self.key, json.dumps(post))

    def drop(self):
        return self.cache.delete(self.key)


class Create(MethodView):
    def get(self):
        pe_state = PostEditorState(self.session)
        pe_state.clear()
        return self.redirect("post.edit")


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

    def get(self, post_id=None):
        if not post_id:
            self.abort(404)

        with self.api.pgsql.transaction() as tx:
            post = posts_model.get_post_by_id(tx, post_id)
            if not post:
                self.abort(404)

            cache = EditorCache(self.api, self.session.id, post_id)
            cached = cache.load()
            print("CACHED", cached)
            post.update(cached)
            # FIXME: AUTHORIZE
            # assert_authorized("post.edit", flask.g.user, orig_post)
            # original_post.update(cached)

            tx.connection.commit()

            return self.mk_response(
                template=self.template,
                post=post,
            )


class CancelEdit(MethodView):
    def get(self):
        post_id = self.get_argument("post_id", None, int)
        cache = EditorCache(self.api, self.session.id, post_id)
        cache.drop()
        return self.redirect_back()


class Save(MethodView):
    def post(self):
        with self.api.pgsql.transaction() as tx:
            form = self.get_form()
            posted = form.to_dict()

            post_id = posted.get("id", 0)
            print(posted)
            if not post_id:
                log.error("Missing post id")
                self.abort(404)

            post = posts_model.get_post_by_id(tx, int(post_id))
            if not post:
                log.error("Editing inexistent post")
                self.abort(404)

            tags = posted.get("tags", "")
            tags = list(set(
                filter(lambda t: t,
                       map(lambda w: w.strip(), tags.split(",")))
            ))
            print("TAGS", tags)
            posted["tags"] = tags
            post.update(posted)

            cache = EditorCache(self.api, self.session.id, post_id)
            if posted.get("preview", None):
                cache.store(post)
                print("PREVIEW", cache.load())
            print("UPDATED", post)
            tx.connection.commit()
            return self.redirect("post.details", post_id=post_id, slug=post.get("slug", ""))


class Preview(MethodView):
    template = "views/post/save.jinja2"

    def get(self):
        with self.api.pgsql.transaction() as tx:
            pe_state = PostEditorState(tx, self.session)
            if not post_id:  # preview
                tags_str = post.get("tags", "").replace(" ", ",")
                tags = sorted(set(
                    filter(lambda t: t.strip(), tags_str.split(","))
                ))
                post.update(
                    id=post_id,
                    tags=tags,
                    author=post.get("author", self.user.name),
                    ctime=post.get("ctime", int(time.time())),
                )

                template = "views/post/preview.jinja2"

                tx.connection.commit()
                return self.mk_response(
                    template=template,
                    post=post,
                    is_preview=True,
                )
