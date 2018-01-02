import flask
from collections import namedtuple
import ki.logg


class FlaskApp(flask.Flask):
    pass


Api = namedtuple("Api", ["cache", "pgsql"])


class Webapp:
    def __init__(self, config, api=None, **kwargs):
        self.log = ki.logg.get(__name__)
        self.config = config
        self.api = api
        self.flask_app = FlaskApp(__name__)
        self.flask_app.config.from_object(config)

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
