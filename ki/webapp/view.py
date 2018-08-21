import flask
import flask.views
import ki.logg
import ki.std
import ki.web.nav
from ki.web.form import Form, FormData
import ki.models.actions


log = ki.logg.get(__name__)


class BaseView:
    route = None

    def __init__(self, app, *args, **kwargs):
        self.app = app
        self.api = app.api
        self.session = flask.g.session
        self.user = flask.g.user
        self.request = flask.request
        self.previous_view = "/"
        if self.request.referrer:
            parsed = ki.std.urlparse(self.request.referrer)
            self.previous_view = parsed.path
            if parsed.query:
                self.previous_view += "?" + parsed.query
            if parsed.fragment:
                self.previous_view += "#" + parsed.fragment


    def mk_response(self, **kwargs):
        template = kwargs.pop("template", None)
        nav = kwargs.pop("nav", ki.web.nav.get_posts_nav())
        subnav = kwargs.pop("subnav", ki.web.nav.get_posts_subnav())
        footer = kwargs.pop("footer", ki.web.nav.get_footer_nav())
        user = kwargs.pop("user", flask.g.user)

        kwargs.update(nav=nav)
        kwargs.update(subnav=subnav)
        kwargs.update(footer=footer)
        kwargs.update(user=kwargs.pop("user", user.as_dict() if user else None))
        kwargs.update(session=kwargs.pop("session", self.session))
        kwargs.update(request=kwargs.pop("request", self.request))

        kwargs.update(previous_view=self.previous_view)

        if not "action" in kwargs:
            action_id = flask.request.args.get(
                ki.models.actions.Action.url_param, None
            )
            action = ki.models.actions.Action(
                action_id,
                session_id=flask.g.session.id
            )

            if action_id:
                action.load(self.api, action_id)

            kwargs.update(action=action.to_dict())

        return flask.render_template(template, view=kwargs)

    def redirect(self, view, **kwargs):
        action = kwargs.pop("action", None)
        if action:
            kwargs[action.url_param] = action.id

        return flask.redirect(
            flask.url_for(view, **kwargs)
        )

    def redirect_url(self, url, **kwargs):
        action = kwargs.pop("action", None)
        if action:
            kwargs[action.url_param] = action.id

        return flask.redirect(url, **kwargs)

    def redirect_back(self, **kwargs):
        p = ki.std.urlparse(self.request.args.get("location", "/"))
        url = p.path
        if p.query:
            url += "?" + p.query
        return flask.redirect(url)

    def get_form(self):
        return Form(
            flask.request.form.to_dict()
            if flask.request.form
            else dict()
        )

    def get_request_args(self):
        return flask.request.args

    def get_argument(self, k, default=None, dt=None):
        v = flask.request.args.get(k, default)
        if dt:
            try:
                return dt(v)
            except TypeError:
                return default
        return v

    def abort(self, *args, **kwargs):
        flask.abort(*args, **kwargs)


class View(BaseView, flask.views.View):
    def __init__(self, api, *args, **kwargs):
        BaseView.__init__(self, api, *args, **kwargs)
        flask.views.View.__init__(self)


class MethodView(BaseView, flask.views.MethodView):
    def __init__(self, api, *args, **kwargs):
        BaseView.__init__(self, api, *args, **kwargs)
        flask.views.MethodView.__init__(self)
