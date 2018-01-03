import uuid
import time

import ki.testing
import ki.errors
import ki.models.users


class Test(ki.testing.ModelTest):
    def setUp(self):
        self.user = ki.models.users.User(name="user-%s" % str(time.time()))
        self.user.password = str(uuid.uuid1())

    def test_create_duplicate(self):
        self.user.password = "whatever"

        with self.pgsql.transaction() as tx:
            cr1 = ki.models.users.create(tx, self.user)
            assert(cr1.id)

        with self.assertRaises(ki.errors.DatabaseError) as e:
            with self.pgsql.transaction() as tx:
                ki.models.users.create(tx, self.user)

    def test_create_password(self):
        self.user.password = "xxxxxx"
        with self.pgsql.transaction() as tx:
            r = ki.models.users.create(tx, self.user)
            assert(r.id)

        for password in [None, "", "xxxxx", 123, True, False]:
            self.user.password = password
            with self.assertRaises(ki.errors.ValidationError) as e:
                with self.pgsql.transaction() as tx:
                    ki.models.users.create(tx, self.user)

    def test_create_email(self):
        # Falsy email values are not used in user creation
        values = [
            "xxx", 123, True, "test@",
            "@localhost", "test@invalid.domain"
        ]

        for email in values:
            self.user.email = email
            with self.assertRaises(ki.errors.ValidationError) as e:
                with self.pgsql.transaction() as tx:
                    ki.models.users.create(tx, self.user)

        self.user.email = "valid@localhost"
        with self.pgsql.transaction() as tx:
            r = ki.models.users.create(tx, self.user)
            assert(r.id)

    def test_delete(self):
        values = [
            "xxx", 123, True, "test@",
            "@localhost", "test@invalid.domain"
        ]

        for uid in values:
            self.user.id = uid
            with self.assertRaises(ki.errors.ValidationError) as e:
                with self.pgsql.transaction() as tx:
                    ki.models.users.delete(tx, self.user)

        # inexistent user (but valid uuid)
        ok = False
        with self.pgsql.transaction() as tx:
            self.user.id = str(uuid.uuid4())
            ok = ki.models.users.delete(tx, self.user)
        assert ok

        with self.pgsql.transaction() as tx:
            r = ki.models.users.create(tx, self.user)
            assert(r.id)
            self.user.id = r.id
            fetched = ki.models.users.get(tx, self.user)
            assert(fetched.id)
            ok = ki.models.users.delete(tx, self.user)
            assert(ok)
            fetched = ki.models.users.get(tx, self.user)
            assert(not fetched)

    def test_delete_keep_comments(self):
        with self.pgsql.transaction() as tx:
            r = ki.models.users.create(tx, self.user)
            assert(r.id)
            self.user.id = r.id

        with self.pgsql.transaction() as tx:
            ok = ki.models.users.delete(tx, self.user, keep_comments=True)
            assert(ok)
            fetched = ki.models.users.get(tx, self.user)
            assert(not fetched)

    def test_delete_keep_username(self):
        """Acts as test_get() too"""
        with self.pgsql.transaction() as tx:
            r = ki.models.users.create(tx, self.user)
            assert(r.id)
            self.user.id = r.id

        with self.pgsql.transaction() as tx:
            ok = ki.models.users.delete(tx, self.user, keep_username=True)
            assert(ok)
            fetched = ki.models.users.get(tx, self.user, active_only=False)
            assert(fetched)

    def test_get_by_email(self):
        self.user.email = "get-by-email@localhost"
        with self.pgsql.transaction() as tx:
            r = ki.models.users.create(tx, self.user)
            assert(r.id)
            self.user.id = r.id

        with self.pgsql.transaction() as tx:
            fetched = ki.models.users.get_by_email(tx, self.user)
            assert(fetched)

            ok = ki.models.users.delete(tx, self.user, keep_username=False)
            assert(ok)

            fetched = ki.models.users.get_by_email(
                tx, self.user, active_only=False
            )

            fetched = ki.models.users.get_by_email(tx, self.user)
            assert(not fetched)

    def test_get_user_info(self):
        with self.pgsql.transaction() as tx:
            r = ki.models.users.create(tx, self.user)
            assert(r.id)
            self.user.id = r.id

        with self.pgsql.transaction() as tx:
            fetched = ki.models.users.get_user_info(tx, self.user)
            assert(fetched.name == self.user.name)
            ok = ki.models.users.delete(tx, self.user, keep_username=False)
            assert(ok)
            fetched = ki.models.users.get_user_info(tx, self.user)
            assert(not fetched)

    def test_authenticate_valid(self):
        self.user.password = "password"

        with self.pgsql.transaction() as tx:
            r = ki.models.users.create(tx, self.user)
            assert r.id

            session_id = str(uuid.uuid1())
            r = users.authenticate(
                username,
                password,
                session_id=session_id
            )
            assert r

        sess = Session(session_id)
        cached = sess.get("user_id", "ctime")
        assert cached
        self.assertEqual(r.id, cached[0])

    # def test_authenticate_invalid(self):
    #     username = "test-authenticate-invalid"
    #     password = "password"

    #     r = users.create(
    #         username,
    #         password,
    #         cursor_type=tuple,
    #     )

    #     assert r.id

    #     r = users.authenticate(
    #         username,
    #         "INVALID",
    #     )
    #     assert not r

    #     r = users.authenticate(
    #         "INVALID",
    #         password,
    #     )
    #     assert not r
