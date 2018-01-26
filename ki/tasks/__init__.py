import celery
from . import emails


class Tasks:
    def __init__(self, config):
        self.celery = celery.Celery()
        self.celery.conf.update(config)

    def initialize(self, webapp):
        emails.initialize(self.celery, webapp)

    def patch_context_task(self, webapp):
        class ContextTask(celery.Task):
            abstract = True

            def __call__(self, *args, **kwargs):
                with webapp.flask_app.app_context():
                    return super().__call__(*args, **kwargs)

        self.celery.Task = ContextTask
