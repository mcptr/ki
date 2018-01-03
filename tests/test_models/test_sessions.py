import uuid
import time

import ki.testing
import ki.errors
import ki.models.users
import ki.models.sessions


class Test(ki.testing.ModelTest):
    def setUp(self):
        self.user = ki.models.users.User(name="user-%s" % str(time.time()))
        self.user.password = str(uuid.uuid1())
        with self.pgsql.transaction() as tx:
            r = ki.models.users.create(tx, self.user)
            assert(r.id)
            self.user.id = r.id

    def test_create(self):
        with self.pgsql.transaction() as tx:
            s = ki.models.sessions.create(tx, self.user, "user agent", 0)
            assert isinstance(s, ki.models.sessions.Session)

        with self.assertRaises(ki.errors.Error):
            with self.pgsql.transaction() as tx:
                s = ki.models.sessions.create(tx, self.user, "x" * 1025, 0)

        with self.assertRaises(ki.errors.Error):
            with self.pgsql.transaction() as tx:
                s = ki.models.sessions.create(tx, self.user, None, "invalid")

    def test_touch(self):
        with self.pgsql.transaction() as tx:
            s = ki.models.sessions.create(tx, self.user, "user agent", 0)
            assert isinstance(s, ki.models.sessions.Session)
            ok = ki.models.sessions.touch(tx, s)
            assert(ok)

            ok = ki.models.users.delete(tx, self.user)
            assert ok

            ok = ki.models.sessions.touch(tx, s)
            assert(not ok)

    def test_terminate(self):
        with self.pgsql.transaction() as tx:
            s = ki.models.sessions.create(tx, self.user, "user agent", 0)
            assert isinstance(s, ki.models.sessions.Session)
            ok = ki.models.sessions.terminate(tx, s)
            assert(ok)

            ok = ki.models.sessions.terminate(tx, s)
            assert(not ok)
