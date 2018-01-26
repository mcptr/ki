import flask
from flask_babel import gettext
import hashlib
import uuid
import ki.emails
import ki.errors
from ki.models.auth import verifications


def mk_menu():
    menu = [
        dict(
            section=gettext("Profile"),
            elements=[
                dict(
                    href=flask.url_for("profile.logout"),
                    caption=gettext("Logout"),
                ),
                # dict(
                #     href="#",
                #     caption=gettext("Notifications"),
                # ),
                dict(
                    href=flask.url_for("profile.main"),
                    caption=gettext("Overview"),
                ),
                dict(
                    href=flask.url_for("profile.edit_password"),
                    caption=gettext("Change password"),
                ),
                dict(
                    href=flask.url_for("profile.edit_email"),
                    caption=gettext("Email address"),
                ),
                dict(
                    href=flask.url_for("profile.remove"),
                    caption=gettext("Account removal"),
                ),
            ]
        ),
        # dict(
        #     section="Content",
        #     elements=[
        #         dict(
        #             href="#",
        #             caption="Posts",
        #         ),
        #         dict(
        #             href="#",
        #             caption="Comments",
        #         ),
        #     ]
        # )
    ]
    return menu


def _mk_subnav():
    return [
    ]


def send_email_verification_link(app, user, link, email=None):
    email = (email or user.email)

    msg = ki.emails.VerificationEmail(
        [email], gettext("Verify your email address"),
    )

    msg.set_content(app, user, link)
    msg.send()


def send_notification_email(email, subject, content):
    email = ki.emails.Email(
        [email],
        subject,
        content=content,
    )
    email.send()


def send_recovery_link(app, user, link):
    msg = ki.emails.ProfileRecoveryEmail(
        [user.email],
        gettext("Profile recovery"),
    )

    msg.set_content(app, user, link)
    msg.send()
