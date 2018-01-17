from ki.webapp import MethodView
from ki.webapp.utils import gettext


class ContentFormatting(MethodView):
    template = "views/help/content_formatting.jinja2"

    def get(self, *args, **kwargs):
        with self.api.pgsql.transaction() as tx:
            pass

        return self.mk_response(
            template=self.template,
        )
