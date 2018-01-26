import uuid
import json
from psycopg2.extras import Json

import ki.pgsql
import ki.cache
import ki.logg
import ki.errors
from ki import validators


log = ki.logg.get(__name__)


class Session:
    def __init__(self, **kwargs):
        self._from_dict(kwargs)

    def _from_dict(self, d):
        user_agent = d.get("user_agent", False)
        if user_agent and len(user_agent) > 1024:
            raise ki.errors.Error("Invalid user agent")
        self.user_agent = d.get("user_agent", False)

        self.id = d.get("id", None)
        self.user_id = d.get("user_id", None)
        self.max_age_sec = d.get("max_age_sec", 0)
        self.ctime = d.get("ctime", None)
        self.mtime = d.get("mtime", None)

        self.storage = (d.get("storage", {}) or {})

    def set_user(self, tx, user, max_age_sec=0, no_check=False):
        if not no_check and (self.user_id and self.user_id != user.id):
            raise ki.errors.Error("Session belongs to a different user")

        sql = (
            "UPDATE auth.sessions SET user_id = %s, max_age_sec = %s"
            "  WHERE id = %s RETURNING *"
        )
        max_age_sec = int(max_age_sec or 0)

        tx.execute(sql, (user.id, max_age_sec, self.id,))
        r = tx.fetchone()
        if r:
            self._from_dict(r._asdict())
            return True
        return None

    def touch(self, tx):
        sql = (
            "UPDATE auth.sessions AS s SET mtime = NOW()"
            "  FROM auth.users u"
            "  WHERE s.id = %s"
            "  AND u.id = %s AND u.is_active AND u.is_closed = false"
            "  AND CASE WHEN s.max_age_sec > 0 THEN"
            "    EXTRACT('EPOCH' FROM NOW() AT TIME ZONE 'UTC'"
            "        - s.mtime)::INTEGER < s.max_age_sec"
            "  ELSE TRUE"
            "  END"
            "  RETURNING s.id"
        )
        tx.execute(sql, (self.id, self.user_id))
        r = tx.fetchone()
        return r.id if r else None

    def load(self, tx):
        sql = (
            "SELECT s.*"
            " FROM auth.sessions s"
            " WHERE s.id = %s"
            " AND CASE WHEN s.max_age_sec > 0 THEN"
            "  EXTRACT('EPOCH' FROM NOW() AT TIME ZONE 'UTC'"
            "       - s.mtime)::INTEGER < s.max_age_sec"
            "  ELSE TRUE"
            " END"
        )
        tx.execute(sql, (self.id,))
        r = tx.fetchone()
        if r:
            self._from_dict(r._asdict())
            return True
        else:
            self._from_dict({})
        return False

    def create(self, tx):
        sql = (
            "INSERT INTO auth.sessions(user_id) VALUES(NULL) RETURNING *"
        )
        tx.execute(sql)
        r = tx.fetchone()
        if r:
            self._from_dict(r._asdict())
        else:
            self._from_dict({})

    def destroy(self, tx):
        sql = (
            "DELETE FROM auth.sessions WHERE id = %s RETURNING id"
        )
        tx.execute(sql, (self.id,))
        r = tx.fetchone()
        if r:
            self._from_dict({})
            return True
        return None

    def update(self, tx, d):
        self.storage.update(d)
        sql = (
            "UPDATE auth.sessions SET storage = %s WHERE id = %s RETURNING id"
        )
        tx.execute(sql, (Json(self.storage), self.id,))
        r = tx.fetchone()
        if r:
            return True
        return None

    def get(self, k, default=None):
        return self.storage.get(k, default)


# TODO: make a periodic app for this
def remove_expired(api):
    sql = (
        "DELETE FROM auth.sessions WHERE max_age_sec > 0"
        "  AND EXTRACT('EPOCH' FROM NOW() AT TIME ZONE 'UTC'"
        "      - mtime)::INTEGER >= max_age_sec"
    )
    with api.pgsql.transaction() as tx:
        tx.execute(sql)
        tx.connection.commit()
