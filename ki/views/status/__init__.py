import flask
from ki.webapp import MethodView
from ki.webapp.utils import jsonify


def create_app(webapp, **kwargs):
    app = flask.Blueprint("status", __name__)
    app.add_url_rule("/", view_func=webapp.mk_view(StatusView))
    webapp.register_blueprint(app, **kwargs)


class StatusView(MethodView):
    def get(self, **kwargs):
        print(type(self.api))
        self.api.models.test.create_test_table()
        return jsonify(kwargs)
