import time
from urllib.parse import urlparse, quote_plus

import ki.logg
from ki.web.utils import mk_slug


log = ki.logg.get(__name__)


COL_DEF = (
    "AS ("
    "  id INTEGER,"
    "  title VARCHAR,"
    "  description TEXT,"
    "  content TEXT,"
    "  url VARCHAR,"
    "  thumbnail_id INTEGER,"
    "  ctime INTEGER,"
    "  mtime INTEGER,"
    "  author VARCHAR,"
    "  user_id UUID,"
    "  tags VARCHAR[],"
    "  total_comments INTEGER,"
    "  thumbnail_path VARCHAR"
    ")"
)

LIMITS = "  LIMIT %s OFFSET %s"

STMT_GET_BY_ID = "SELECT * FROM posts.get_by_id(%s) " + COL_DEF
STMT_GET_BY_TAG = "SELECT * FROM posts.get_by_tag(%s) " + COL_DEF + LIMITS
STMT_GET_BY_USER = "SELECT * FROM posts.get_by_user(%s) " + COL_DEF + LIMITS
STMT_GET_RECENT = "SELECT * FROM posts.get_recent() " + COL_DEF + LIMITS

STMT_CREATE = (
    "SELECT posts.create_post("
    "  %(title)s, %(user_id)s,"
    "  %(description)s, %(content)s,"
    "  %(url)s"
    ") AS id"
)

STMT_DELETE = "DELETE FROM posts.posts WHERE id = %s RETURNING id"

STMT_ADD_TAGS = "SELECT * FROM posts.add_tags(%s, %s)"
STMT_REMOVE_TAGS = "SELECT * FROM posts.remove_tags(%s, %s)"


DEFAULT_LIMIT = 5


def __prepare_post(p):
    if not p:
        return None
    p = p._asdict()
    if p.get("url", None):
        source_domain = urlparse(p["url"]).hostname
        p.update(source_domain=source_domain)

    full_date = time.strftime(
        "%Y-%m-%d %H:%M",
        time.localtime(p.get("ctime", 0))
    )

    p.update(full_date=full_date)
    short_title = mk_slug(p.get("title", "")[:72], 70)
    p.update(slug=quote_plus(short_title))

    return p


def get_recent(tx, offset=0, limit=DEFAULT_LIMIT):
    tx.execute(STMT_GET_RECENT, (limit, offset))
    r = tx.fetchall()
    return list(map(__prepare_post, r))


def get_posts_by_tag(tx, tag, offset=0, limit=DEFAULT_LIMIT):
    tx.execute(STMT_GET_BY_TAG, (tag, limit, offset))
    return list(map(__prepare_post, tx.fetchall()))


def get_posts_by_user(tx, username, offset=0, limit=DEFAULT_LIMIT):
    tx.execute(STMT_GET_BY_USER, (username, limit, offset))
    return list(map(__prepare_post, tx.fetchall()))


def get_post_by_id(tx, id):
    tx.execute(STMT_GET_BY_ID, (id,))
    post = tx.fetchone()
    return __prepare_post(post)


def create(tx, **kwargs):
    log.debug("Creating post: %s", kwargs["title"])

    data = dict(
        title=kwargs.pop("title", None),
        user_id=kwargs.pop("user_id", None),
        description=kwargs.pop("description", None),
        content=kwargs.pop("content", None),
        url=kwargs.pop("url", None),
    )

    tags = kwargs.pop("tags", None)

    tx.execute(STMT_CREATE, data)
    post_id = tx.fetchone()
    if post_id and tags:
        add_tags(post_id, tags)
    return post_id


def update(tx, **kwargs):
    log.debug("Updating post: %d, %s", kwargs["id"], kwargs["title"])

    sql = (
        "UPDATE posts.posts SET"
        "    title=%(title)s, description=%(description)s,"
        "    content=%(content)s, url=%(url)s,"
        "    mtime=NOW()"
        "  WHERE id=%(id)s"
        "  RETURNING id"
    )

    tags = kwargs.pop("tags", None)

    tx.execute(sql, kwargs)
    r = tx.fetchone()
    if r:
        replace_tags(r.id, tags)
    return r


def delete(tx, id):
    tx.execute(STMT_DELETE, (id,))
    return tx.fetchone()


def add_tags(tx, post_id, tags):
    tags = list(set(filter(lambda t: t, tags)))
    if not tags:
        return

    tx.execute(STMT_ADD_TAGS, (post_id, tags))
    return tx.fetchone()


def remove_tags(tx, post_id, tags):
    tags = list(set(filter(lambda t: t, tags)))
    if not tags:
        return
    tx.execute(STMT_REMOVE_TAGS, (post_id, tags))
    return tx.fetchone()


def replace_tags(tx, post_id, new_tags):
    tx.execute(
        "DELETE FROM posts.tags WHERE post_id = %s",
        (post_id, )
    )
    add_tags(post_id, new_tags)
