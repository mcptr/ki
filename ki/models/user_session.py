import time
import schzd.core.cache


class Session:
    def __init__(self, id, ttl=(3600 * 24)):
        self.id = id
        self.ttl = ttl
        self.redis = schzd.core.cache.get_connection()
        self.cache_key = "user:session:%s" % self.id

    def update(self, **mapping):
        return self.redis.hmset(self.cache_key, mapping)

    def set(self, k, v):
        return self.redis.hset(self.cache_key, k, v)

    def remove(self, k):
        return self.redis.hdel(self.cache_key, k)

    def get(self, *args):
        return list(
            map(
                lambda v:
                v.decode("utf-8") if v else None,
                self.redis.hmget(self.cache_key, *args)
            )
        )

    def get_all(self):
        return self.redis.hgetall(self.cache_key)

    def get_field(self, name):
        v = self.redis.hget(self.cache_key, name)
        return v.decode("utf-8") if v else None

    def touch(self):
        self.redis.hmset(self.cache_key, dict(
            last_seen=time.time()
        ))
        self.redis.expire(self.cache_key, self.ttl)

    def destroy(self):
        return self.redis.delete(self.cache_key)
