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

    def test_authenticate(self):
        self.user.password = "password"

        with self.pgsql.transaction() as tx:
            r = ki.models.users.create(tx, self.user)
            assert r.id

    def test_authenticate_password(self):
        self.user.password = "password"

        with self.pgsql.transaction() as tx:
            r = ki.models.users.create(tx, self.user)
            assert r.id

            r = ki.models.users.authenticate(tx, self.user)
            assert r

            self.user.password = "invalid"
            r = ki.models.users.authenticate(tx, self.user)
            assert not r

    def test_authenticate_username(self):
        self.user.password = "password"

        with self.pgsql.transaction() as tx:
            r = ki.models.users.create(tx, self.user)
            assert r.id

            r = ki.models.users.authenticate(tx, self.user)
            assert r

            self.user.name = "invalid"
            r = ki.models.users.authenticate(tx, self.user)
            assert not r

    def test_emails(self):
        self.user.password = "password"

        with self.pgsql.transaction() as tx:
            r = ki.models.users.create(tx, self.user)
            assert r.id
            self.user.id = r.id
            tx.connection.commit()

        with self.assertRaises(ki.errors.ValidationError):
            with self.pgsql.transaction() as tx:
                self.user.email = "invalid"
                ki.models.users.set_email(tx, self.user)

        with self.pgsql.transaction() as tx:
            self.user.email = "valid.email@localhost"
            r = ki.models.users.set_email(tx, self.user)
            assert(r)

            fetched = ki.models.users.get(tx, self.user)
            assert fetched.id
            assert not fetched.email_verified_on

            r = ki.models.users.set_email_verified(tx, self.user)
            assert(r)

            fetched = ki.models.users.get(tx, self.user)
            assert fetched.id
            assert fetched.email == self.user.email
            assert fetched.email_verified_on

            r = ki.models.users.remove_email(tx, self.user)
            assert(r)

            fetched = ki.models.users.get(tx, self.user)
            assert fetched.id
            assert not fetched.email
            assert not fetched.email_verified_on

    def test_password(self):
        with self.pgsql.transaction() as tx:
            r = ki.models.users.create(tx, self.user)
            assert r.id
            self.user.id = r.id
            tx.connection.commit()

        with self.assertRaises(ki.errors.ValidationError):
            invalid = ["", False, True, 12345, None]
            for passwd in invalid:
                with self.pgsql.transaction() as tx:
                    self.user.password = passwd
                    ki.models.users.set_password(tx, self.user)

        valid = ["okokok", "password", "this is also ok", 123456]
        for passwd in valid:
            with self.pgsql.transaction() as tx:
                self.user.password = passwd
                r = ki.models.users.set_password(tx, self.user)
                assert r
