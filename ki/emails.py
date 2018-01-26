import ki.tasks.emails


class Email:
    def __init__(self, rcpt, subject, **kwargs):
        self.rcpt = rcpt
        self.subject = subject
        self.content = kwargs.pop("content", None)

    def set_content(self, value):
        self.content = value

    def send(self):
        ki.tasks.emails.send.delay(self.rcpt, self.subject, self.content)


class VerificationEmail(Email):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def set_content(self, app, user, link):
        locale = (user.locale or "en_US")

        content = app.flask_app.render_l10n_template(
            locale,
            "emails/verification.jinja2",
            link=link,
            user=user,
        )

        super().set_content(content)


class ProfileRecoveryEmail(Email):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def set_content(self, app, user, link):
        locale = (user.locale or "en_US")

        content = app.flask_app.render_l10n_template(
            locale,
            "emails/profile_recovery.jinja2",
            link=link,
            user=user,
        )

        super().set_content(content)

