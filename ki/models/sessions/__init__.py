import uuid

import ki.pgsql
import ki.cache
import ki.logg
import ki.errors
from ki import validators


log = ki.logg.get(__name__)


class Session:
    def __init__(self, **kwargs):
        self.id = kwargs.pop("id", None)
        self.user_id = kwargs.pop("user_id", None)
        self.user_agent = kwargs.pop("user_agent", False)
        self.max_age_sec = kwargs.pop("max_age_sec", 0)
        self.ctime = kwargs.pop("ctime", None)
        self.mtime = kwargs.pop("mtime", None)


def create(tx, user, user_agent=None, max_age_sec=0, **kwargs):
    log.info("Creating session, user: %s", user.id)
    sql = (
        "INSERT INTO auth.sessions(id, user_id, max_age_sec, user_agent)"
        "  VALUES(%s, %s, %s, %s) RETURNING *"
    )
    if user_agent and len(user_agent) > 1024:
        raise ki.errors.Error("Invalid user agent")

    max_age_sec = int(max_age_sec or 0)

    session_id = kwargs.pop("id", str(uuid.uuid4()))
    tx.execute(sql, (session_id, user.id, max_age_sec, user_agent))
    r = tx.fetchone()
    if r.id:
        return Session(**r._asdict())
    return None


def touch(tx, session):
    sql = (
        "UPDATE auth.sessions AS s SET mtime = NOW()"
        "  FROM auth.users u"
        "  WHERE s.id = %s"
        "  AND u.id = %s AND u.is_active AND u.is_closed = false"
        "  AND CASE WHEN s.max_age_sec > 0 THEN"
        "        EXTRACT('EPOCH' FROM NOW() - s.mtime)::INTEGER < s.max_age_sec"
        "      ELSE TRUE"
        "      END"
        "  RETURNING s.id"
    )
    tx.execute(sql, (session.id, session.user_id))
    r = tx.fetchone()
    return r.id if r else None


def load(tx, session):
    sql = (
        "SELECT s.*"
        "  FROM auth.sessions s"
        "  WHERE s.id = %s"
        "  AND CASE WHEN s.max_age_sec > 0 THEN"
        "        EXTRACT('EPOCH' FROM NOW() - s.mtime)::INTEGER < s.max_age_sec"
        "      ELSE TRUE"
        "      END"
    )
    tx.execute(sql, (session.id,))
    r = tx.fetchone()
    return r


def destroy(tx, session):
    sql = (
        "DELETE FROM auth.sessions WHERE id = %s RETURNING id"
    )
    tx.execute(sql, (session.id,))
    r = tx.fetchone()
    return r.id if r else None


# TODO: make a periodic app for this
def remove_expired(api):
    sql = (
        "DELETE FROM auth.sessions WHERE max_age_sec > 0"
        "  AND EXTRACT('EPOCH' FROM NOW() - mtime)::INTEGER >= max_age_sec"
    )
    with api.pgsql.transaction() as tx:
        tx.execute(sql)
        tx.connection.commit()
