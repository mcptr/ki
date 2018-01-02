import flask.views
import ki.logg


log = ki.logg.get(__name__)


class View(flask.views.View):
    route = None

    def __init__(self, api, *args, **kwargs):
        super().__init__()
        self.api = api


class MethodView(flask.views.MethodView):
    route = None

    def __init__(self, api, *args, **kwargs):
        super().__init__()
        self.api = api
