from ki.webapp import MethodView


class StatusView(MethodView):
    def get(self, **kwargs):
        # self.api.models.test.create_test_table()
        print(dir(self.api))
        return self.render_template("index.jinja2")
