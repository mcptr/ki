import flask
import flask.views
import ki.logg


log = ki.logg.get(__name__)


class BaseView:
    route = None
    nav = []

    def __init__(self, api, *args, **kwargs):
        self.api = api

    def mk_response(self, **kwargs):
        template = kwargs.pop("template", None)
        kwargs.update(nav=kwargs.pop("nav", self.nav))
        kwargs.update(user=kwargs.pop("user", flask.g.user))
        kwargs.update(session=kwargs.pop("session", flask.g.session))
        return flask.render_template(template, view=kwargs)


class View(BaseView, flask.views.View):
    def __init__(self, api, *args, **kwargs):
        BaseView.__init__(self, api, *args, **kwargs)
        flask.views.View.__init__(self)


class MethodView(BaseView, flask.views.MethodView):
    def __init__(self, api, *args, **kwargs):
        BaseView.__init__(self, api, *args, **kwargs)
        flask.views.View.__init__(self)
