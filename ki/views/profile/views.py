from ki.webapp import MethodView


class MainView(MethodView):
    def get(self, **kwargs):
        return self.render_template(
            "profile/main.jinja2",
        )
