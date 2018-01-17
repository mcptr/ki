import flask
import flask_babel
import jinja2
from collections import namedtuple
from functools import partial

import ki.logg
import ki.cache
import ki.web.filters
import ki.web.jinja_extensions
from . import hooks


class FlaskApp(flask.Flask):
    pass


Api = namedtuple("Api", ["cache", "pgsql"])


class Webapp:
    def __init__(self, config, api=None, **kwargs):
        self.log = ki.logg.get(__name__)
        self.config = config
        self.api = api
        self.flask_app = FlaskApp(
            kwargs.pop("name", __name__),
            template_folder=self.config.TEMPLATE_FOLDER,
            static_folder=self.config.STATIC_FOLDER,
        )
        self.flask_app.config.from_object(config)

        self.extensions = dict()
        self.init_extensions()
        before_request_hooks = [
            hooks.remove_expired_sessions,
            hooks.load_user,
            hooks.csrf_protect,
        ]
        if self.config.DEBUG:
            before_request_hooks.append(hooks.debug_mode_hooks)

        self.register_before_request_hooks(None, before_request_hooks)

        ki.web.filters.register(self.flask_app)
        ki.web.jinja_extensions.register(self.flask_app)

    def mk_view(self, cls, *args, **kwargs):
        vargs = tuple([self.api, *args])
        view_func = cls.as_view(cls.__name__, *vargs, **kwargs)
        return view_func

    def register_view(self, view, **kwargs):
        route = kwargs.pop("route", view.route)
        self.log.debug("Registering view: %s -> %s", view.__name__, route)
        self.flask_app.add_url_rule(route, view_func=self.mk_view(view))

    def register_app(self, pkg, **kwargs):
        self.log.debug("Registering app: %s -> %s", pkg.__name__, kwargs)
        pkg.create_app(self, **kwargs)

    def register_blueprint(self, bp, **kwargs):
        self.flask_app.register_blueprint(bp, **kwargs)

    def run(self, **kwargs):
        for tpl in sorted(self.flask_app.jinja_env.list_templates()):
            self.log.debug("Template: %s", tpl)
        self.flask_app.run(**kwargs)

    def get_wsgi_app(self):
        return self.flask_app

    def register_before_request_hooks(self, bp, funcs):
        """Pass bp=None to make it for all blueprints"""
        hooks = self.flask_app.before_request_funcs.get(bp, [])
        hooks.extend(funcs)
        hooks = list(map(lambda f: partial(f, self), hooks))
        self.flask_app.before_request_funcs[bp] = hooks

    def init_extensions(self):
        self.flask_app.jinja_env.autoescape = jinja2.select_autoescape(
            enabled_extensions=("jinja2", "html", "xml"),
            default_for_string=True,
        )

        babel = flask_babel.Babel(self.flask_app)
        babel.locale_selector_func = self.locale_selector

        self.extensions.update(
            babel=babel,
        )

    def locale_selector(self):
        flask.request.accept_languages.best_match(
            self.config.LANGUAGES.keys()
        )
        # TODO: user/session
        return "en_US"
