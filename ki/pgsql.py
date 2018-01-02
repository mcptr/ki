import os
import psycopg2
import psycopg2.pool
import psycopg2.extras
import contextlib

from urllib.parse import urlparse, parse_qsl

import ki.logg
import ki.errors


class Api:
    log = ki.logg.get(__name__)

    def __init__(self, url):
        self.log.debug("Initializing pgsql pool")
        dsn = urlparse(url)
        qs = dict(parse_qsl(dsn.query))

        self._pool = psycopg2.pool.ThreadedConnectionPool(
            1, 15,
            host=dsn.hostname,
            port=(dsn.port or 5432),
            user=dsn.username,
            password=dsn.password,
            dbname=dsn.path.lstrip("/"),
            sslmode=qs.get("sslmode", "verify-full"),
        )

    def __del__(self):
        self._pool.closeall()

    @contextlib.contextmanager
    def connection(self):
        try:
            connection = self._pool.getconn()
            yield connection
        except Exception as e:
            self.log.error(e)
        finally:
            self._pool.putconn(connection)

    @contextlib.contextmanager
    def cursor(self, cursor_type=tuple, **kwargs):
        try:
            connection = self._pool.getconn()
            cursor_factory = psycopg2.extras.NamedTupleCursor
            if cursor_type in [dict]:
                cursor_factory = psycopg2.extras.RealDictCursor
            cursor = connection.cursor(cursor_factory=cursor_factory)
            try:
                yield cursor
            finally:
                cursor.close()
        except ki.errors.Error as e:
            # self.log.exception(e)
            raise
        except Exception as e:
            self.log.error(e)
            raise ki.errors.DatabaseError(e)
        finally:
            self._pool.putconn(connection)

    @contextlib.contextmanager
    def transaction(self, cursor_type=tuple, **kwargs):
        try:
            with self.cursor(cursor_type, **kwargs) as cur:
                yield cur
                cur.connection.commit()
        except ki.errors.DatabaseError as e:
            cur.connection.rollback()
            raise


class SchemaLoader:
    def __init__(self, api):
        self.api = api
        self.log = ki.logg.get(self.__class__.__name__)

    def readfile(self, path):
        with open(path, "r") as fh:
            return fh.read()

    def load(self, loc):
        sql = []
        paths = []
        if os.path.isdir(loc):
            for (r, d, files) in os.walk(loc):
                for f in sorted(files):
                    if not f.endswith(".sql"):
                        continue
                    paths.append(os.path.join(r, f))
        elif os.path.isfile(loc):
            paths.append(loc)

        if not paths:
            self.log.debug("No sql paths")
            return

        with self.api.cursor() as cursor:
            for p in sorted(paths):
                self.log.debug(p)
                contents = self.readfile(p)
                if contents:
                    cursor.execute(contents)
            cursor.connection.commit()
