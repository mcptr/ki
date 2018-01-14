import flask
from ki.webapp import MethodView
from ki.webapp.utils import gettext
import ki.web.pagination
from ki.models.posts import posts as model


class ListView(MethodView):
    template = "views/posts/listing.jinja2"

    def _load_posts(self, offset, limit, **kwargs):
        raise NotImplemented(gettext("Unable to load posts"))

    def _get_view_title(self, **kwargs):
        return None

    def _get_pagination_endpoint(self, **kwargs):
        return flask.request.endpoint

    def get(self, **kwargs):
        limit = 10
        page = int(kwargs.pop("page", 1))
        page = page if page > 0 else 1
        offset = (page * limit) - limit

        posts = self._load_posts(offset, limit, **kwargs)

        return self.mk_response(
            template=self.template,
            title=self._get_view_title(**kwargs),
            posts=posts,
            pagination = ki.web.pagination.mk_urls(
                self._get_pagination_endpoint(**kwargs),
                page,
                len(posts),
                limit
            )
        )


class RecentPosts(ListView):
    def _load_posts(self, offset, limit):
        with self.api.pgsql.transaction() as tx:
            return model.get_recent(tx, offset, limit)

    def _get_view_title(self, **kwargs):
        return gettext("Recent posts")

    def _get_pagination_endpoint(self, **kwargs):
        return "posts.recent_paged"


class PostsByTag(ListView):
    def _load_posts(self, offset, limit, **kwargs):
        tag = kwargs.get("tag", None)
        if not tag:
            return []
        with self.api.pgsql.transaction() as tx:
            return model.get_by_tag(tx, tag, offset, limit)

    def _get_view_title(self, **kwargs):
        return gettext("Tag: %s", kwargs.get("tag", None))

    def _get_pagination_endpoint(self, **kwargs):
        return "posts.by_tag_paged"

    # view = schzd.web.view.View(
    #     "posts/index.jinja2",
    #     view_menu=menus.get_posts_view_menu(),
    #     subtitle="Recent posts",
    # )

    # return view.render(
    #     posts=posts,
    #     page_id=page_id,
    #     pagination=schzd.web.pagination.mk_urls(
    #         "posts.recent",
    #         page_id,
    #         len(posts),
    #         PAGE_LIMIT
    #     ),
    # )
