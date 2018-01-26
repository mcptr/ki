from flask_mail import Message


send = None


def initialize(celery_app, webapp):
    def _send(rcpt, subject, content):
        msg = Message(
            recipients=rcpt,
            subject=subject,
            body="\n\n".join([(content or ""), webapp.config.MAIL_SIGNATURE]),
        )
        webapp.extensions["mail"].send(msg)

    global send
    send = celery_app.task(_send)
