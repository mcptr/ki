import flask
import flask.views
import ki.logg
import ki.web.nav
from ki.web.form import Form, FormData
import ki.models.actions


log = ki.logg.get(__name__)


class BaseView:
    route = None

    def __init__(self, app, *args, **kwargs):
        self.app = app
        self.api = app.api

    def mk_response(self, **kwargs):
        template = kwargs.pop("template", None)
        nav = kwargs.pop("nav", ki.web.nav.get_posts_nav())
        footer = kwargs.pop("footer", ki.web.nav.get_footer_nav())

        kwargs.update(nav=nav)
        kwargs.update(footer=footer)
        kwargs.update(user=kwargs.pop("user", flask.g.user.as_dict()))
        kwargs.update(session=kwargs.pop("session", flask.g.session))
        kwargs.update(request=kwargs.pop("request", flask.request))

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
