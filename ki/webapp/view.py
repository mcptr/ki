import flask
import flask.views
import ki.logg
import ki.web.nav


log = ki.logg.get(__name__)


class BaseView:
    route = None

    def __init__(self, api, *args, **kwargs):
        self.api = api

    def mk_response(self, **kwargs):
        template = kwargs.pop("template", None)
        nav = kwargs.pop("nav", ki.web.nav.get_posts_nav())
        footer = kwargs.pop("footer", ki.web.nav.get_footer_nav())

        kwargs.update(nav=nav)
        kwargs.update(footer=footer)
        kwargs.update(user=kwargs.pop("user", flask.g.user))
        kwargs.update(session=kwargs.pop("session", flask.g.session))
        kwargs.update(request=kwargs.pop("request", flask.request))
        return flask.render_template(template, view=kwargs)

    def redirect(self, view, **kwargs):
        return flask.redirect(
            flask.url_for(view, **kwargs)
        )


class View(BaseView, flask.views.View):
    def __init__(self, api, *args, **kwargs):
        BaseView.__init__(self, api, *args, **kwargs)
        flask.views.View.__init__(self)


class MethodView(BaseView, flask.views.MethodView):
    def __init__(self, api, *args, **kwargs):
        BaseView.__init__(self, api, *args, **kwargs)
        flask.views.MethodView.__init__(self)
