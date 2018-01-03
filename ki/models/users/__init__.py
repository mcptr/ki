import time
import uuid

import ki.pgsql
import ki.logg
import ki.errors
from ki import validators
# from schzd.models.user_session import Session


log = ki.logg.get(__name__)


class User:
    def __init__(self, **kwargs):
        self.id = kwargs.pop("id", None)
        self.password = None  # must be explicitely set
        self.name = kwargs.pop("name", "Anonymous")
        self.email = kwargs.pop("email", None)
        self.is_admin = kwargs.pop("is_admin", False)
        self.is_moderator = kwargs.pop("is_moderator", False)
        self.is_active = kwargs.pop("is_moderator", False)
        self.is_closed = kwargs.pop("is_moderator", False)
        self.email_verified_on = kwargs.pop("email_verified_on", None)
        self.is_active = kwargs.pop("is_active", False)

    def as_dict(self):
        return self.__dict__


def create(tx, user):
    log.info("Creating user: %s", user.name)
    validators.validate_username(user.name)
    validators.validate_password(user.password)
    if user.email:
        validators.validate_email(user.email)

    sql = (
        "INSERT INTO auth.users(name, password, email)"
        "  VALUES(%(name)s, %(password)s, %(email)s)"
        "  RETURNING id"
    )

    tx.execute(sql, user.as_dict())
    r = tx.fetchone()
    return r


def delete(tx, user, **kwargs):
    log.info("Deleting user id: %s", user.id)
    validators.validate_user_id(user.id)
    # comments have a "on delete set null" fkey, they go first
    if not kwargs.get("keep_comments", 1):
        sql = (
            "UPDATE posts.comments SET content=NULL,"
            "  deleted=true WHERE user_id=%s"
        )
        tx.execute(sql, (user.id, ))

    if kwargs.get("keep_username", 1):
        sql = (
            "UPDATE auth.users SET is_closed=true, is_active=false,"
            "  email=NULL, "
            "  password=gen_random_uuid()::text || gen_random_uuid()"
            " WHERE id=%s "
        )
        tx.execute(sql, (user.id, ))
    else:
        sql = "DELETE FROM auth.users WHERE id=%s"
        tx.execute(sql, (user.id, ))

    return True


def get(tx, user, active_only=True, **kwargs):
    if not user.id:
        return None

    validators.validate_user_id(user.id)

    sql = (
        "SELECT id, name, email, is_active, is_admin, is_moderator,"
        "    email_verified_on,"
        "    ctime, mtime"
        "  FROM auth.users"
        "  WHERE id=%s"
    )

    if active_only:
        sql += " AND is_active"

    tx.execute(sql, (user.id,))
    return tx.fetchone()


def get_by_email(tx, user, active_only=True, **kwargs):
    sql = (
        "SELECT id, name, email, is_active, is_admin, is_moderator,"
        "    email_verified_on,"
        "    ctime, mtime"
        "  FROM auth.users"
        "  WHERE email=%s"
    )

    if active_only:
        sql += " AND is_active"

    tx.execute(sql, (user.email,))
    return tx.fetchone()


def get_user_info(tx, user):
    sql = (
        "SELECT * FROM auth.get_user_info(%s)"
        "    AS (name VARCHAR,"
        "       is_admin BOOLEAN,"
        "       is_moderator BOOLEAN,"
        "       is_active BOOLEAN,"
        "       is_closed BOOLEAN,"
        "       email_verified_on INTEGER,"
        "       ctime INTEGER,"
        "       mtime INTEGER,"
        "       total_posts BIGINT,"
        "       total_comments BIGINT)"
    )
    tx.execute(sql, (user.name, ))
    r = tx.fetchone()
    return r if r.name else None


def user_exists(tx, user):
    name = user.name.strip()

    sql = (
        "SELECT COUNT(id) > 0 AS user_exists"
        "  FROM auth.users WHERE name = %s"
    )

    tx.execute(sql, (name, ))
    r = tx.fetchone()
    return r.user_exists


def email_exists(tx, user):
    email = user.email.strip()

    sql = (
        "SELECT COUNT(id) > 0 AS email_exists"
        "  FROM auth.users WHERE email = %s"
    )

    tx.execute(sql, (email, ))
    r = tx.fetchone()
    return r.email_exists


def authenticate(tx, user, **kwargs):
    log.info("Authenticating: %s", user.name)
    sql = (
        "SELECT * FROM auth.authenticate_user(%s, %s)"
        "  AS(id UUID, name VARCHAR, ctime INTEGER, mtime INTEGER)"
    )

    tx.execute(sql, (user.name, user.password))
    r = tx.fetchone()

    if r.id:
        sid = kwargs.pop("session_id", None)
        if sid:
            sess = Session(sid)
            sess.update(
                user_id=str(r.id),
                ctime=time.time(),
            )
            sess.touch()
        return r
    return None


def set_password(tx, user):
    log.info("Setting password: %s", user.id)
    validators.validate_password(user.password)

    sql = "UPDATE auth.users SET password = %s WHERE id=%s RETURNING id"

    tx.execute(sql, (user.password, user.id))
    r = tx.fetchone()
    return r.id


def set_email_verified(tx, user):
    log.info("Setting email verified for user: %s", user.id)

    sql = (
        "UPDATE auth.users SET email_verified_on = NOW()"
        "  WHERE id=%s RETURNING id"
    )

    tx.execute(sql, (user.id,))
    r = tx.fetchone()
    return r.id is not None


def set_email(tx, user):
    log.info("Setting email for user: %s", user.id)
    validators.validate_email(user.email)

    sql = (
        "UPDATE auth.users SET email = %s, email_verified_on = NULL"
        "  WHERE id=%s RETURNING id"
    )

    tx.execute(sql, (user.email, user.id,))
    r = tx.fetchone()
    return r.id is not None


def remove_email(tx, user):
    log.info("Removing email for user: %s", user.id)

    sql = (
        "UPDATE auth.users SET email = NULL"
        "  WHERE id=%s RETURNING id"
    )

    tx.execute(sql, (user.id, ))
    r = tx.fetchone()
    return r.id is not None
