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
        self.terminated = kwargs.pop("terminated", False)
        self.ctime = kwargs.pop("ctime", None)
        self.mtime = kwargs.pop("mtime", None)


# class CachedSession:
#     def __init__(self, id, ttl=(3600 * 24)):
#         self.id = id
#         self.ttl = ttl
#         self.redis = schzd.core.cache.get_connection()
#         self.cache_key = "user:session:%s" % self.id

#     def update(self, **mapping):
#         return self.redis.hmset(self.cache_key, mapping)

#     def set(self, k, v):
#         return self.redis.hset(self.cache_key, k, v)

#     def remove(self, k):
#         return self.redis.hdel(self.cache_key, k)

#     def get(self, *args):
#         return list(
#             map(
#                 lambda v:
#                 v.decode("utf-8") if v else None,
#                 self.redis.hmget(self.cache_key, *args)
#             )
#         )

#     def get_all(self):
#         return self.redis.hgetall(self.cache_key)

#     def get_field(self, name):
#         v = self.redis.hget(self.cache_key, name)
#         return v.decode("utf-8") if v else None

#     def touch(self):
#         self.redis.hmset(self.cache_key, dict(
#             last_seen=time.time()
#         ))
#         self.redis.expire(self.cache_key, self.ttl)

#     def destroy(self):
#         return self.redis.delete(self.cache_key)



def create(tx, user, user_agent=None, max_age_sec=0):
    log.info("Creating session, user: %s", user.name)
    sql = (
        "INSERT INTO auth.sessions(user_id, max_age_sec, user_agent)"
        "  VALUES(%s, %s, %s) RETURNING *"
    )
    if user_agent and len(user_agent) > 1024:
        raise ki.errors.Error("Invalid user agent")

    max_age_sec = int(max_age_sec or 0)

    tx.execute(sql, (user.id, max_age_sec, user_agent))
    r = tx.fetchone()
    if r.id:
        return Session(**r._asdict())
    return None


def touch(tx, session):
    sql = (
        "UPDATE auth.sessions AS s SET mtime = NOW()"
        "  FROM auth.users u"
        "  WHERE s.id = %s AND s.terminated = false"
        "  AND u.id = %s AND u.is_active AND u.is_closed = false"
        "  AND EXTRACT('EPOCH' FROM NOW())::INTEGER - EXTRACT('EPOCH' FROM s.mtime)::INTEGER >= s.max_age_sec "
        "  RETURNING s.id"
    )
    tx.execute(sql, (session.id, session.user_id))
    r = tx.fetchone()
    return r.id if r else None


def load(tx, session):
    sql = (
        "SELECT s.*"
        "  FROM auth.sessions s"
        "  LEFT JOIN auth.users u"
        "  ON u.id = s.user_id"
        "  WHERE s.id = %s AND s.terminated = false"
        "  AND u.id = %s AND u.is_active AND u.is_closed = false"
        "  AND EXTRACT('EPOCH' FROM NOW())::INTEGER - EXTRACT('EPOCH' FROM s.mtime)::INTEGER >= s.max_age_sec "
    )
    tx.execute(sql, (session.id, session.user_id))
    r = tx.fetchone()
    return r


def terminate(tx, session):
    sql = (
        "UPDATE auth.sessions AS s SET mtime = NOW(), terminated = true"
        "  WHERE s.id = %s AND s.terminated = false"
        "  RETURNING s.id"
    )
    tx.execute(sql, (session.id,))
    r = tx.fetchone()
    return r.id if r else None
