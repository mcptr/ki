import time
import uuid

from schzd import validators
from schzd.core.pgsql import pg_cursor
import schzd.core.logg
import schzd.core.errors


log = schzd.core.logg.get(__name__)


def remove_user_recoveries(user_id):
    with pg_cursor() as c:
        c.execute(
            "DELETE FROM auth.recovery WHERE user_id = %s",
            (user_id,)
        )
        c.connection.commit()


def gen_recovery(user_id, max_age_sec=(3600 * 4)):
    remove_user_recoveries(user_id)
    sql = (
        "INSERT INTO auth.recovery(user_id, max_age_sec)"
        "  VALUES(%s, %s)"
        "  RETURNING id, ctime"
    )
    with pg_cursor() as c:
        c.execute(sql, (user_id, int(max_age_sec)))
        c.connection.commit()
        return c.fetchone()


def get_recovery_user_id(recovery_id):
    sql = (
        "SELECT user_id FROM auth.recovery"
        "  WHERE id=%s"
        "  AND ((EXTRACT('EPOCH' FROM now() AT TIME ZONE 'UTC')::integer -"
        "       EXTRACT('EPOCH' FROM ctime))::integer < max_age_sec)"
    )
    with pg_cursor() as c:
        c.execute(sql, (recovery_id,))
        c.connection.commit()
        return c.fetchone()
