from ki.webapp import MethodView


class StatusView(MethodView):
    def get(self, **kwargs):
        return self.render_template("index.jinja2")
