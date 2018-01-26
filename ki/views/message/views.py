import flask
from ki.webapp import MethodView


class MessageView(MethodView):
    template = "views/message/message.jinja2"

    def get(self):
        return self.mk_response(
            template=self.template,
        )
