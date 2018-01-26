import time
import uuid

import ki.logg


log = ki.logg.get(__name__)


def remove_user_recoveries(tx, user_id):
    tx.execute(
        "DELETE FROM auth.recovery WHERE user_id = %s",
        (user_id,)
    )


def gen_recovery(tx, user_id, max_age_sec=(3600 * 4)):
    remove_user_recoveries(tx, user_id)
    sql = (
        "INSERT INTO auth.recovery(user_id, max_age_sec)"
        "  VALUES(%s, %s)"
        "  RETURNING id"
    )
    tx.execute(sql, (user_id, int(max_age_sec)))
    r = tx.fetchone()
    return r.id if r else None


def get_recovery_user_id(tx, recovery_id):
    sql = (
        "DELETE FROM auth.recovery"
        "  WHERE id=%s"
        "  AND (EXTRACT('EPOCH' FROM NOW() - ctime))::INTEGER < max_age_sec)"
        "  RETURNING user_id"
    )
    tx.execute(sql, (recovery_id,))
    r = tx.fetchone()
    return r.user_id if r else None
