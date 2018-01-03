import flask
import flask_session
from collections import namedtuple
from functools import partial
import ki.logg
import ki.cache
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
            __name__,
            template_folder=self.config.TEMPLATE_FOLDER,
            static_folder=self.config.STATIC_FOLDER,
        )
        self.flask_app.config.from_object(config)
        self.extensions = dict()
        self.init_extensions()
        self.register_before_request_hooks(None, [
            hooks.load_user
        ])

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

    def run(self):
        self.flask_app.run()

    def get_wsgi_app(self):
        return self.flask_app

    def register_before_request_hooks(self, bp, funcs):
        """Pass bp=None to make it for all blueprints"""
        current = []
        if not bp:
            current = self.flask_app.before_request_funcs.get(None, [])
        current.extend(funcs)
        current = map(lambda f: partial(f, self.api), current)
        self.flask_app.before_request_funcs[bp] = current

    def init_extensions(self):
        session_config = dict(
            SESSION_TYPE="redis",
            SESSION_REDIS=self.api.cache.get_connection()
        )
        self.flask_app.config.update(session_config)
        session = flask_session.Session(self.flask_app)

        self.extensions.update(
            session=session,
        )
