import redis
import json
import atexit

from urllib.parse import urlparse

import ki.logg


class Api:
    log = ki.logg.get(__name__)

    def __init__(self, redis_url):
        self._pool = None
        self.url = redis_url
        self.log.debug("Initializing cache api")
        dsn = urlparse(redis_url)
        self._pool = redis.ConnectionPool(
            host=dsn.hostname,
            port=dsn.port,
            db=(int(dsn.path.lstrip("/") or 0)),
            max_connections=64,
        )

    def __del__(self):
        self.log.debug("Deleting cache api")
        self._pool.disconnect()

    def get_connection(self):
        if not self._pool:
            raise Exception("Connection pool not initialized")
        return redis.StrictRedis(connection_pool=self._pool)
