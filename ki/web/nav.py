import flask
from flask_babel import gettext


def get_posts_nav():
    menu = [
        dict(
            href=flask.url_for("posts.recent"),
            caption=gettext("Recent"),
        ),
        # dict(
        #     href=flask.url_for("comments.recent"),
        #     caption="Comments",
        # ),
        # dict(
        #     href=flask.url_for("posts.tags"),
        #     caption="Tags",
        # ),
        # dict(
        #     # href=flask.url_for("posts.search"),
        #     href="/",
        #     caption="Search",
        # ),
    ]

    # if flask.g.user.id:
    #     menu.append(
    #         dict(
    #             href=flask.url_for("post.create"),
    #             caption="Submit",
    #         )
    #     )
    return menu


def get_footer_nav():
    menu = [
        dict(
            href="#",
            caption=gettext("Help"),
        ),
        dict(
            href="#",
            caption=gettext("About"),
        ),
        dict(
            href="#",
            caption=gettext("Privacy"),
        ),
    ]
    return menu
