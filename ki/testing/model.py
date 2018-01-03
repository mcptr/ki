import os
import unittest
import uuid
import time
import testing.redis
import testing.postgresql
from urllib.parse import urlparse, parse_qsl

import ki.logg
import ki.cache
import ki.pgsql
import ki.tasks

import ki.config.testing as config

import ki.models.users


ki.logg.configure(debug=config.DEBUG)


Postgresql = testing.postgresql.PostgresqlFactory(
    cache_initialized_db=True,
)


# def populate_db():
#     tx = schzd.core.pgsql.Transaction()
#     with schzd.core.pgsql.pg_cursor(tx=tx) as cur:
#         create_test_users(cur)
#         tx.commit()


# def create_test_users(cur):
#     for i in range(0, 10):
#         r = schzd.models.users.create(
#             "user-%d" % i,
#             "password-%d" % i,
#             cursor_type=tuple,
#         )
#         log.debug("Created user: %s", r.id)


class ModelTest(unittest.TestCase):
    log = ki.logg.get(__name__)

    def __del__(self):
        Postgresql.clear_cache()

    @classmethod
    def setUpClass(cls):
        cls.log.debug("Setting up test backend class")
        cls._pgsql_server = Postgresql()
        cls._redis_server = testing.redis.RedisServer()
        redis_url = "redis://{host}:{port}/{db}".format(
            **cls._redis_server.dsn()
        )
        pgurl = cls._pgsql_server.url() + "?sslmode=prefer"
        cls.log.debug("Test postgres: %s", pgurl)
        cls.pgsql = ki.pgsql.Api(pgurl)
        cls.log.debug("Test redis: %s", redis_url)
        cls.cache = ki.cache.Api(redis_url)

        config.CELERY.update(
            broker_url=redis_url,
            result_backend=redis_url,
        )
        cls.celery = ki.tasks.Tasks(config.CELERY)
        # celery.patch_
        cls.load_sql_schema()
        # schzd.testing.pgsql.populate_db()

    @classmethod
    def load_sql_schema(cls):
        cls.log.debug("Loading schema")
        loader = ki.pgsql.SchemaLoader(cls.pgsql)
        loader.load("sql")

    @classmethod
    def tearDownClass(cls):
        cls.log.debug("Stopping test servers")
        cls._pgsql_server.stop()
        cls._redis_server.stop()

    def setUp(self):
        self.log.debug("Setting up")

    def debug_dump_users(self):
        with self.pgsql.transaction() as tx:
            tx.execute("select * from auth.users")
            for r in tx.fetchall():
                u = ki.models.users.User(**r._asdict())
                print(u.as_dict())
